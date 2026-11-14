# Acoustic Pipeline Leak Detection — Analysis Notebooks

## 1. Create the analysis dataset

From the **repository root**, run:

```bash
python src/convert_probe_data_to_segments_matched.py data/2026-03-04 data/all_segments.csv
```

- **Input:** `data/2026-03-04/` — original acoustic probe CSV files.
- **Output:** `data/all_segments.csv`.
- **Script:** `src/convert_probe_data_to_segments_matched.py` (the timestamp-matched version).
- **Dataset:** One row per run, matched timestamp, and adjacent probe pair (`UUS-US`, `US-DS`, or `DS-DDS`). Includes signed upstream-minus-downstream frequency amplitudes, Reynolds level, and leak-event information. The script retains the full observation period and matches timestamps across each segment's two probes.

## 2. Leak detection approaches and corresponding notebooks

| # | Approach | Latest corresponding notebook |
|---|---|---|
| 1 | LSTM (original) | |
| 2 | CUSUM / Change-Point Detection | |
| 3 | Difference-in-Differences (DiD) | `first_leak_frequency_analysis_DiD_posthealthy.ipynb` |
| 4 | ABA Analysis | `first_leak_frequency_sensitivity_ABA.ipynb` |
| 5 | Median-Based Leak Analysis | `segment_reynolds_level_and_change_vs_first_leak_SETTLED_SAMPLES_FIXED_v1.ipynb` |
| 6 | Reynolds LEVEL Correlation | `segment_reynolds_level_and_change_vs_first_leak_SETTLED_SAMPLES_FIXED_v1.ipynb` |
| 7 | Reynolds TRANSITION Analysis | `segment_reynolds_level_and_change_vs_first_leak_SETTLED_SAMPLES_FIXED_v1.ipynb` |
| 8 | Immediate Onset-Jump Analysis | `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY.ipynb` |
| 9 | Jump Recovery + Healthy Comparison | `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY.ipynb` |

*Blank notebook entries mean the corresponding LSTM and CUSUM filenames were not identifiable in the supplied notebook list.*

## 3. Selected approach

**Selected method:** Immediate onset-jump analysis with recovery and healthy-event comparisons.

**Selected notebook:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY.ipynb`

This is the final approach selected from the analyses above. Its results were the most promising in the exploratory comparisons, but leak detection performance and false-positive rates have **not** been conclusively validated.
