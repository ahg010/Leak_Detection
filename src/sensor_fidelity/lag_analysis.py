import numpy as np
import pandas as pd


def safe_corr(x, y, min_pairs=20):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < min_pairs or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def scan_lags(matched, freqs, sensors, min_lag=0, max_lag=30, min_pairs=20):
    indexed = matched.set_index("timestamp").sort_index()
    source = indexed[[f"{f}_source" for f in freqs]]
    rows = []
    for sensor in sensors:
        sensor_data = indexed[[f"{f}_{sensor}" for f in freqs]]
        for lag in range(min_lag, max_lag + 1):
            shifted = sensor_data.copy()
            shifted.index = shifted.index - pd.Timedelta(seconds=lag)
            paired = source.join(shifted, how="inner")
            for freq in freqs:
                x, y = paired[f"{freq}_source"], paired[f"{freq}_{sensor}"]
                rows.append({"sensor": sensor, "frequency": freq, "lag_seconds": lag,
                             "pearson_r": safe_corr(x, y, min_pairs),
                             "n_pairs": int((x.notna() & y.notna()).sum())})
    scan = pd.DataFrame(rows)
    curves = scan.groupby(["sensor", "lag_seconds"], as_index=False).agg(
        mean_corr=("pearson_r", "mean"), median_corr=("pearson_r", "median"),
        frequencies_used=("pearson_r", "count"))
    if curves.groupby("sensor").mean_corr.apply(lambda s: s.notna().any()).eq(False).any():
        raise ValueError("Insufficient nonconstant matched data for lag estimation")
    best = curves.loc[curves.groupby("sensor").mean_corr.idxmax()].sort_values("sensor").reset_index(drop=True)
    zero = curves.loc[curves.lag_seconds.eq(0), ["sensor", "mean_corr"]].rename(columns={"mean_corr":"corr_at_zero"})
    best = best.merge(zero, on="sensor", how="left")
    best["improvement"] = best.mean_corr - best.corr_at_zero
    return scan, curves, best


def align_comparison(matched, freqs, sensors, delays, min_pairs=20):
    base = matched.set_index("timestamp").sort_index()
    corrected = base[[f"{f}_source" for f in freqs]].copy()
    common = base.index
    for sensor in sensors:
        shifted = base[[f"{f}_{sensor}" for f in freqs]].copy()
        shifted.index -= pd.Timedelta(seconds=int(delays[sensor]))
        common = common.intersection(shifted.index)
        corrected = corrected.join(shifted, how="left")
    common = common.sort_values()
    if len(common) < min_pairs:
        raise ValueError(f"Only {len(common)} shared source timestamps for corrected comparison")
    return base.loc[common].reset_index(), corrected.loc[common].reset_index()


def source_autocorrelation(matched, freqs, max_lag=30, min_pairs=20):
    source = matched.set_index("timestamp")[[f"{f}_source" for f in freqs]]
    rows = []
    for lag in range(max_lag + 1):
        shifted = source.copy()
        shifted.index -= pd.Timedelta(seconds=lag)
        paired = source.join(shifted, how="inner", lsuffix="_now", rsuffix="_later")
        for f in freqs:
            rows.append({"frequency":f, "lag_seconds":lag,
                         "autocorr":safe_corr(paired[f"{f}_source_now"], paired[f"{f}_source_later"],min_pairs)})
    return pd.DataFrame(rows)
