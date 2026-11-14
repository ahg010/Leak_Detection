
"""Convert ALL original probe CSV observations into directed pipeline segments.

Reads the complete raw CSV files (including events after the first leak),
without truncating, filtering Reynolds levels, or applying statistical analysis.

For each segment, only timestamps present in BOTH endpoint probes are retained.
Unmatched timestamps are counted and printed as warnings for that segment.

Usage from repository root:
    python3 src/convert_probe_data_to_segments_matched.py data/2026-03-04 data/all_segments.csv

Usage from notebooks/:
    python3 ../src/convert_probe_data_to_segments_matched.py ../data/2026-03-04 ../data/all_segments.csv

Each row represents a (run, timestamp, segment). For each original frequency f,
output columns contain upstream and downstream raw amplitudes and the
SIGNED difference: upstream__f - downstream__f.

contains_leak_site identifies the known location (US-DS); leak_active is the
experiment-wide original 'Leak Event' indicator at that timestamp.

leak_active=True does NOT imply every segment contains the physical leak.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


# Same input-column and filename conventions as extract_through_first_leak.py.
# Defined locally so this script does not depend on another source file.

def normalize_column(name: str) -> str:
    """Keep the segment following the last pipe-like delimiter."""
    name = str(name).strip()

    for delimiter in ("ǀ", "|", "｜", "¦"):
        if delimiter in name:
            name = name.rsplit(delimiter, 1)[-1].strip()

    return name


def probe_from_filename(stem: str) -> str:
    """Identify the probe from the source filename."""
    for probe in ("UUS", "DDS", "US", "DS"):
        if re.match(
            rf"^{probe}(?=\d|_|-|$)",
            stem,
            flags=re.IGNORECASE
        ):
            return probe

    raise ValueError(
        f"Cannot identify probe from filename: {stem}"
    )


SEGMENTS = (
    ("UUS", "US"),
    ("US", "DS"),
    ("DS", "DDS"),
)

PROBES = ("UUS", "US", "DS", "DDS")

REQUIRED_COLUMNS = (
    "Date-Time",
    "Reynolds_level",
    "Leak Event",
)

FREQUENCY_RE = re.compile(r"f\d+(?:\.\d+)?\Z")


def read_probe(
    file: Path
) -> tuple[str, str, pd.DataFrame, list[str]]:
    """Read original observations without removing any rows or phases."""

    df = pd.read_csv(file, low_memory=False)

    # Normalize source column names.
    columns = [normalize_column(col) for col in df.columns]

    if len(columns) != len(set(columns)):
        duplicates = sorted({
            col for col in columns
            if columns.count(col) > 1
        })

        raise ValueError(
            f"{file.name}: duplicate columns after normalization: "
            f"{duplicates}"
        )

    df.columns = columns

    # Standardize Reynolds column name.
    df = df.rename(
        columns={"Reynolds_Level": "Reynolds_level"}
    )

    if df.columns.duplicated().any():
        raise ValueError(
            f"{file.name}: duplicate columns after Reynolds normalization"
        )

    # Validate required columns.
    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df
    ]

    if missing:
        raise ValueError(
            f"{file.name}: missing required columns {missing}"
        )

    # Identify probe and experiment.
    probe = probe_from_filename(file.stem)
    run_id = file.stem[len(probe):]

    if not run_id:
        raise ValueError(
            f"{file.name}: missing experiment/run identifier"
        )

    # Identify original frequency columns.
    frequencies = sorted(
        [
            c for c in df.columns
            if FREQUENCY_RE.fullmatch(c)
        ],
        key=lambda c: float(c[1:]),
    )

    if not frequencies:
        raise ValueError(
            f"{file.name}: no frequency amplitude columns"
        )

    # Validate leak indicator.
    leak = pd.to_numeric(
        df["Leak Event"],
        errors="coerce"
    )

    if leak.isna().any() or not leak.isin([0, 1]).all():
        raise ValueError(
            f"{file.name}: Leak Event must contain only numeric 0/1 values"
        )

    df["Leak Event"] = leak.astype("int8")

    # Validate Reynolds level.
    levels = pd.to_numeric(
        df["Reynolds_level"],
        errors="raise"
    )

    if levels.isna().any():
        raise ValueError(
            f"{file.name}: Reynolds_level contains missing values"
        )

    df["Reynolds_level"] = levels

    # Parse and validate timestamps.
    timestamps = pd.to_datetime(
        df["Date-Time"],
        errors="raise"
    )

    if timestamps.isna().any() or timestamps.duplicated().any():
        raise ValueError(
            f"{file.name}: timestamps must be present and unique"
        )

    df.insert(0, "_timestamp", timestamps)

    df = (
        df.sort_values("_timestamp")
        .reset_index(drop=True)
    )

    df.insert(
        1,
        "_original_timestamp",
        df["Date-Time"].copy()
    )

    return run_id, probe, df, frequencies


def convert_probe_data_to_segments(
    source_folder: str | Path,
    destination_filename: str | Path
) -> pd.DataFrame:
    """Convert all probe CSV files into segment-level observations."""

    source = Path(source_folder).expanduser().resolve()
    destination = Path(destination_filename).expanduser().resolve()

    if not source.is_dir():
        raise NotADirectoryError(
            f"Source folder not found: {source}"
        )

    files = sorted(source.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {source}"
        )

    if destination in files:
        raise ValueError(
            "Destination must not overwrite an original probe CSV"
        )

    # Group data by experiment and probe.
    by_run: dict[
        str,
        dict[str, tuple[pd.DataFrame, Path]]
    ] = {}

    all_frequencies: list[str] | None = None

    for file in files:
        run, probe, df, frequencies = read_probe(file)

        if all_frequencies is None:
            all_frequencies = frequencies

        elif frequencies != all_frequencies:
            raise ValueError(
                f"{file.name}: frequency columns do not match other files; "
                "refusing to silently discard measurements"
            )

        run_files = by_run.setdefault(run, {})

        if probe in run_files:
            raise ValueError(
                f"{run}: duplicate {probe} probe file"
            )

        run_files[probe] = (df, file)

        print(
            f"Loaded {file.name}: "
            f"{len(df):,} rows, "
            f"{len(frequencies)} frequencies"
        )

    assert all_frequencies is not None

    pieces: list[pd.DataFrame] = []

    expected_rows_by_run: dict[str, int] = {}

    # Process each experiment independently.
    for run_id in sorted(by_run):

        probes = by_run[run_id]

        missing = sorted(
            set(PROBES) - set(probes)
        )

        if missing:
            raise ValueError(
                f"{run_id}: missing probe files {missing}; "
                "cannot construct all segments"
            )

        # Experiment start time.
        run_times = probes[PROBES[0]][0]["_timestamp"]
        run_start = run_times.min()

        # Build the three segments.
        for upstream_probe, downstream_probe in SEGMENTS:

            upstream, upstream_file = probes[upstream_probe]
            downstream, downstream_file = probes[downstream_probe]

            id_ = f"{upstream_probe}-{downstream_probe}"

            # Match timestamps between the two endpoint probes.
            #
            # Outer merge allows us to count unmatched timestamps.
            # Only rows with measurements from BOTH probes are retained.

            paired = upstream.merge(
                downstream,
                on="_timestamp",
                how="outer",
                validate="one_to_one",
                indicator=True,
                suffixes=("_up", "_down"),
                sort=True,
            )

            # Count mismatches independently for this segment.
            upstream_only = int(
                paired["_merge"].eq("left_only").sum()
            )

            downstream_only = int(
                paired["_merge"].eq("right_only").sum()
            )

            unmatched = upstream_only + downstream_only

            # Print warning without terminating processing.
            if unmatched:
                print(
                    f"WARNING {run_id}/{id_}: "
                    f"excluded {unmatched:,} unmatched timestamps "
                    f"({upstream_only:,} upstream-only, "
                    f"{downstream_only:,} downstream-only); "
                    "other segments are unaffected."
                )

            # Retain only synchronized timestamps.
            paired = (
                paired.loc[paired["_merge"].eq("both")]
                .drop(columns="_merge")
                .reset_index(drop=True)
            )

            # Track expected output rows.
            expected_rows_by_run[run_id] = (
                expected_rows_by_run.get(run_id, 0)
                + len(paired)
            )

            # Check that synchronized probes agree on
            # Reynolds level and leak status.
            for col in ("Reynolds_level", "Leak Event"):

                differences = paired[
                    f"{col}_up"
                ].ne(
                    paired[f"{col}_down"]
                )

                if differences.any():
                    raise ValueError(
                        f"{run_id}/{id_}: "
                        f"{int(differences.sum())} synchronized "
                        f"observations disagree on {col}"
                    )

            # Construct segment-level metadata.
            result = pd.DataFrame({
                "run_id": run_id,

                "Date-Time-orig": paired[
                    "_original_timestamp_up"
                ],

                "Date-Time": (
                    paired["_timestamp"] - run_start
                ).dt.total_seconds(),

                "Reynolds_level": paired[
                    "Reynolds_level_up"
                ],

                "segment_id": id_,

                "contains_leak_site": id_ == "US-DS",

                "leak_active": paired[
                    "Leak Event_up"
                ].astype(bool),

                "upstream_probe": upstream_probe,

                "downstream_probe": downstream_probe,

                "upstream_file_name": upstream_file.stem,

                "downstream_file_name": downstream_file.stem,
            })

            # Generate frequency columns.
            #
            # Example for f315:
            #
            # upstream__f315
            # downstream__f315
            # upstream_minus_downstream__f315
            #
            # The difference is SIGNED.
            # No absolute value is applied.

            for frequency in all_frequencies:

                u = pd.to_numeric(
                    paired[f"{frequency}_up"],
                    errors="raise"
                )

                d = pd.to_numeric(
                    paired[f"{frequency}_down"],
                    errors="raise"
                )

                result[
                    f"upstream__{frequency}"
                ] = u

                result[
                    f"downstream__{frequency}"
                ] = d

                result[
                    f"upstream_minus_downstream__{frequency}"
                ] = u - d

            # Preserve additional original source columns.
            excluded = (
                set(REQUIRED_COLUMNS)
                | set(all_frequencies)
            )

            for col in upstream.columns:

                if col.startswith("_") or col in excluded:
                    continue

                result[
                    f"upstream__{col}"
                ] = paired[f"{col}_up"]

            for col in downstream.columns:

                if col.startswith("_") or col in excluded:
                    continue

                result[
                    f"downstream__{col}"
                ] = paired[f"{col}_down"]

            pieces.append(result)

            print(
                f"{run_id}/{id_}: "
                f"{len(result):,} synchronized segment observations"
            )

    # Combine all segments from all experiments.
    output = pd.concat(
        pieces,
        ignore_index=True
    )

    output = (
        output.sort_values(
            ["run_id", "Date-Time"],
            kind="stable"
        )
        .reset_index(drop=True)
    )

    # Verify retained row counts for every experiment.
    for run_id, expected in expected_rows_by_run.items():

        actual = len(
            output.loc[
                output["run_id"].eq(run_id)
            ]
        )

        if actual != expected:
            raise AssertionError(
                f"{run_id}: expected {expected} rows, got {actual}"
            )

    # Save output.
    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        destination,
        index=False
    )

    print(
        f"Saved {len(output):,} segment observations "
        f"to {destination}"
    )

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "source_folder",
        help="Original per-probe CSV directory"
    )

    parser.add_argument(
        "destination_filename",
        help="Output segment CSV file"
    )

    args = parser.parse_args()

    convert_probe_data_to_segments(
        args.source_folder,
        args.destination_filename
    )


if __name__ == "__main__":
    main()

