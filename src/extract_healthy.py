#!/usr/bin/env python3
"""Extract strictly pre-first-leak rows from each probe CSV.

Usage:
    python src/extract_healthy.py data/2026-03-04 data/healthy_pre_leak.csv
    python ../src/extract_healthy.py ../data/2026-03-04 ../data/healthy_pre_leak.csv

Paths are resolved relative to the current working directory.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

PROBES = ("UUS", "DDS", "US", "DS")  # longest first


def normalize_column(name: str) -> str:
    """Keep the segment following the last pipe-like delimiter."""
    name = str(name).strip()
    for delimiter in ("ǀ", "|", "｜", "¦"):
        if delimiter in name:
            name = name.rsplit(delimiter, 1)[-1].strip()
    return name


def probe_from_filename(stem: str) -> str:
    for probe in PROBES:
        if re.match(rf"^{probe}(?=\d|_|-|$)", stem, flags=re.IGNORECASE):
            return probe
    raise ValueError(f"Cannot identify probe from filename: {stem}")



def extract_healthy(source_folder: str | Path, destination_filename: str | Path) -> pd.DataFrame:
    """Extract rows before the first leak event (1) in each CSV, then concatenate.

    Date-Time is seconds elapsed from the first retained timestamp in each file.
    Date-Time-orig retains the original timestamp text.
    """
    source = Path(source_folder).expanduser().resolve()
    destination = Path(destination_filename).expanduser().resolve()

    if not source.is_dir():
        raise NotADirectoryError(f"Source folder not found: {source}")

    files = sorted(source.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {source}")

    pieces = []

    for file in files:
        df = pd.read_csv(file)

        # Normalize column names
        renamed = [normalize_column(col) for col in df.columns]

        if len(renamed) != len(set(renamed)):
            duplicates = sorted({
                col for col in renamed if renamed.count(col) > 1
            })
            raise ValueError(
                f"{file.name}: duplicate columns after normalization: {duplicates}"
            )

        df.columns = renamed

        # Standardize Reynolds level column name
        df = df.rename(columns={
            "Reynolds_Level": "Reynolds_level"
        })

        # Validate required columns
        for col in ["Leak Event", "Date-Time", "Reynolds_level"]:
            if col not in df.columns:
                raise ValueError(f"{file.name}: missing '{col}' column")

        # Validate leak indicator
        leak = pd.to_numeric(df["Leak Event"], errors="coerce")

        if leak.isna().any() or not leak.isin([0, 1]).all():
            raise ValueError(
                f"{file.name}: Leak Event must contain only numeric 0/1 values"
            )

        # Stop at the first leak event
        first_leak_positions = leak.to_numpy().nonzero()[0]
        stop = (
            int(first_leak_positions[0])
            if len(first_leak_positions)
            else len(df)
        )

        healthy = df.iloc[:stop].copy()

        if not healthy.empty:
            # Preserve original timestamps and compute elapsed seconds
            original = healthy["Date-Time"].copy()
            timestamps = pd.to_datetime(original, errors="raise")
            elapsed_seconds = (
                timestamps - timestamps.iloc[0]
            ).dt.total_seconds()

            healthy = healthy.rename(
                columns={"Date-Time": "Date-Time-orig"}
            )

            healthy.insert(
                healthy.columns.get_loc("Date-Time-orig") + 1,
                "Date-Time",
                elapsed_seconds
            )

            healthy["Date-Time-orig"] = original

            # Add source metadata
            healthy.insert(0, "file_name", file.stem)
            healthy.insert(
                1,
                "probe",
                probe_from_filename(file.stem)
            )

            pieces.append(healthy)

        print(
            f"{file.name}: kept {len(healthy):,}/{len(df):,} rows; "
            f"first leak at row "
            f"{stop if stop < len(df) else 'none'} (0-based)"
        )

    if not pieces:
        raise ValueError(
            "No pre-leak healthy rows found in any CSV; destination not written"
        )

    # Combine all healthy observations
    result = pd.concat(pieces, ignore_index=True)

    # Validate Reynolds levels before saving
    result["Reynolds_level"] = pd.to_numeric(
        result["Reynolds_level"], errors="raise"
    )

    if result["Reynolds_level"].isna().any():
        raise ValueError("Missing Reynolds_level values in extracted data")

    # Save
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False)

    print(
        f"Saved {len(result):,} rows from "
        f"{len(pieces)} files to {destination}"
    )

    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_folder", help="Directory containing probe CSV files")
    parser.add_argument("destination_filename", help="Output CSV path")
    args = parser.parse_args()
    extract_healthy(args.source_folder, args.destination_filename)


if __name__ == "__main__":
    main()
