import numpy as np
import pandas as pd
from pathlib import Path


def read_sensor_csv(path):
    try:
        df = pd.read_csv(path, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(path, sep="\t")

    if df.shape[1] == 1:
        df = pd.read_csv(path, sep="\t")

    return df.dropna(axis=0, how="all").dropna(axis=1, how="all")


def get_datetime_col(df):
    for c in ["Date-Time", "iDate-Time"]:
        if c in df.columns:
            return c

    for c in df.columns:
        s = str(c).lower()
        if "date" in s and "time" in s:
            return c

    raise KeyError("Could not identify Date-Time column.")


def get_reynolds_col(df):
    for c in df.columns:
        if "reynolds" in str(c).lower():
            return c

    for c in df.columns:
        if str(c).strip().lower() == "re":
            return c

    for c in df.columns:
        if "re" in str(c).lower():
            return c

    raise KeyError("Could not identify Reynolds-number column.")


def parse_frequency_value(col):
    s = str(col)

    if "ǀf" not in s:
        return None

    token = s.split("ǀf", 1)[1].replace("_", ".")

    try:
        return float(token)
    except ValueError:
        return None


def get_frequency_columns(df):
    pairs = []

    for c in df.columns:
        f = parse_frequency_value(c)
        if f is not None:
            pairs.append((f, c))

    pairs.sort(key=lambda x: x[0])

    if len(pairs) != 27:
        raise ValueError(
            f"Expected 27 frequency columns but found {len(pairs)}."
        )

    return [f for f, _ in pairs], [c for _, c in pairs]


def build_iteration(iteration, data_dir, probe_order):
    frames = {
        probe: read_sensor_csv(Path(data_dir) / f"{probe}{iteration}.csv")
        for probe in probe_order
    }

    ref_df = frames[probe_order[0]]
    re_col = get_reynolds_col(ref_df)
    dt_col = get_datetime_col(ref_df)

    reference_freqs = None
    probe_arrays = []

    for probe in probe_order:
        df = frames[probe]
        freqs, freq_cols = get_frequency_columns(df)

        if reference_freqs is None:
            reference_freqs = freqs
        elif not np.allclose(reference_freqs, freqs):
            raise ValueError(
                f"Frequency mismatch for {probe} in {iteration}"
            )

        arr = (
            df[freq_cols]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
            .to_numpy(dtype=np.float32)
        )

        probe_arrays.append(arr)

    min_T = min(arr.shape[0] for arr in probe_arrays)

    spectra_raw = np.stack(
        [arr[:min_T] for arr in probe_arrays],
        axis=1
    ).astype(np.float32)

    Re_raw = (
        pd.to_numeric(ref_df[re_col], errors="coerce")
        .fillna(0.0)
        .to_numpy(dtype=np.float32)[:min_T]
    )

    datetime = pd.to_datetime(
        ref_df[dt_col],
        errors="coerce"
    ).to_numpy()[:min_T]

    return {
        "iteration": iteration,
        "spectra_raw": spectra_raw,
        "Re_raw": Re_raw,
        "datetime": datetime,
        "frequencies": reference_freqs,
    }



def prepare_run(iteration, config, root):
    run = build_iteration(iteration, root / config["data_dir"], config["probe_order"])
    run["X"] = run["spectra_raw"] / config["spectrum_scale"]
    run["Re"] = run["Re_raw"] / config["reynolds_scale"]
    return run

def make_windows(run, window_size):
    X = run["X"].astype(np.float32)
    y = run["Re"].astype(np.float32)
    if len(X) < window_size:
        raise ValueError(f"Need at least {window_size} rows, got {len(X)}")
    return np.stack([X[i:i+window_size] for i in range(len(X)-window_size+1)]), y[window_size-1:]

def verify_files(config, root):
    paths = [root / config["data_dir"] / f"{probe}{run}.csv"
             for run in [config["train_iteration"], config["validation_iteration"]]
             for probe in config["probe_order"]]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError("Missing CSV files:\n" + "\n".join(missing))
    return paths
