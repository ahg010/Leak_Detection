import pandas as pd


def load_recording(path, label, freqs, skip_first_rows=10, timestamp_column="receipt_time"):
    if not path.is_file():
        raise FileNotFoundError(f"Required recording not found: {path}")
    raw = pd.read_csv(path)
    raw.columns = raw.columns.str.strip()
    missing = [c for c in [timestamp_column, *freqs] if c not in raw.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    if skip_first_rows < 0:
        raise ValueError("skip_first_rows must be >= 0")
    raw = raw.iloc[skip_first_rows:].copy()
    raw["timestamp"] = pd.to_datetime(raw[timestamp_column], utc=True, errors="coerce").dt.floor("s")
    if raw["timestamp"].isna().any():
        raise ValueError(f"{path.name}: unparseable timestamps")
    for f in freqs:
        raw[f] = pd.to_numeric(raw[f], errors="coerce")
    grouped = raw.groupby("timestamp", as_index=False)[freqs].mean()
    return grouped.rename(columns={f: f"{f}_{label}" for f in freqs})


def match_recordings(config):
    source = config["selected_source"]
    labels = [source, *config["sensors"]]
    frames = {}
    summary = []
    for label in labels:
        path = config["data_path"] / config["files"][label]
        frame = load_recording(path, label, config["freq_cols"],
            config["preprocessing"]["skip_first_rows"],
            config["preprocessing"]["timestamp_column"])
        frames[label] = frame
        summary.append({"recording": label, "unique_seconds": len(frame),
                        "first_second": frame.timestamp.min(), "last_second": frame.timestamp.max()})
    matched = frames[source].rename(columns={f"{f}_{source}": f"{f}_source" for f in config["freq_cols"]})
    for sensor in config["sensors"]:
        matched = matched.merge(frames[sensor], on="timestamp", how="inner", validate="one_to_one")
    if matched.empty:
        raise ValueError("No timestamps shared by source and all sensors")
    return matched.sort_values("timestamp").reset_index(drop=True), pd.DataFrame(summary)
