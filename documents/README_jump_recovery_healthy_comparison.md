# Immediate Onset-Jump, Recovery & Healthy-Comparison Analysis

## Executive summary

**Purpose:** Evaluate whether an acoustic jump **at the recorded first-leak onset** is distinguishable from a normal **Reynolds 100→150** transition and from event-free healthy fluctuations. Assess the **first observed return** after a genuine onset excursion. The experiment also asks which frequencies and sensor pairs are most responsive.

**Finding:** **f2500** and **f3100** repeatedly have strong *immediate-onset* responses in four of the five runs. The fifth run (`1213_1`) shows weak separation. **This is exploratory event-aligned analysis, not a validated leak detector.**

## Notebook and input

- **Annotated notebook:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY_results_ANNOTATED.ipynb`
- **Original uploaded notebook:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY_results.ipynb`
- **Input:** `data/all_segments.csv` (looked up relative to the repository root; launch the notebook from the root or `notebooks/`)
- **Output directory:** `results/event_aligned_immediate_onset_jumps/`
- **Segments:** `UUS-US`, `US-DS`, `DS-DDS`
- **Scope:** 5 experiments; 26 acoustic-frequency features, each the signed upstream-minus-downstream amplitude of a sensor pair.

The notebook uses the recorded run-level event times from the input and does **not** detect events by choosing an acoustic peak. Execute the notebook with its existing cell order and existing configuration. The edited copy adds **documentation only**, not computational changes.

## Methodology

1. **Select physical events:** healthy **Reynolds 100→150** transition before first leak, and **first leak onset at Re=150**. Later inactive periods are not considered healthy.
2. **Estimate local baseline:** use the median `B` and the robust noise scale `sigma_pre = 1.4826 × MAD` of the preceding **60 s** at the relevant pre-event Reynolds level (Re=100 before transition; Re=150 before leak).
3. **Measure exact onset:** `leak_peak_z = |A(t0) − B| / sigma_pre` (and analogously `re_peak_z`). **No delayed peaks** are counted.
4. **Check recovery:** only when **onset Z > 2**, search the **following 60 s** for the first observed sample inside `B ± 2 × sigma_pre`. Record its elapsed time and separately whether the immediately following adjacent sample returned.
5. **Healthy comparator:** sample event-free healthy Re=150 pseudo-onsets every **30 s**, with **16 such timestamps per run and segment** in the saved run. Compare each frequency's leak-onset Z with these background jumps for the **same run and segment**.
6. **Inspect plots:** independently show the healthy Reynolds transition and first-leak event with **60 s before and after t0**, without using post-onset spikes in the t0 ranking.

## Key result columns

| Column | Meaning | Desirable pattern |
|---|---|---|
| `leak_peak_z` | Absolute immediate leak-onset jump relative to the local pre-leak robust noise | High |
| `re_peak_z` | Immediate healthy Reynolds 100→150 jump relative to its *own* local noise | Low |
| `healthy_peak_z_p95` | 95th percentile of sampled healthy immediate jumps | Below leak Z |
| `healthy_peak_exceedance_fraction` | Proportion of sampled healthy jumps at least as large as the observed leak jump | Low (descriptive only) |
| `leak_recovery_time_s` | Seconds until **first observed** return inside the original baseline band after an onset excursion | Interpret with plots |

**`leak_recovery_time_s = NaN`** means either **onset Z ≤ 2** (no qualifying excursion, so recovery is not applicable) or **onset Z > 2** without an observed return in the 60-second post-event window. A green dot marks one in-band observation, **not sustained recovery**.

## Observations from the notebook's saved outputs

- Input/results: **161,114 rows**, **5 runs**, **3 sensor pairs**, **26 frequencies**, **10 event boundaries**, **780 event-frequency measurements**, and **390 merged run/segment/frequency comparisons**.
- Event times: Reynolds transition at **2400 s** and first leak at **3000 s** in four runs; **2700 s** and **3300 s** respectively in `1213_1`.
- **f2500** occurs in **9 of the 15** top-five lists (4 runs); **8 of those 9** entries have onset **Z > 2** and an observed first return. **f3100** occurs **9 times** (8 qualifying excursions); **f5000** occurs **7 times** (6 qualifying excursions). These counts are conditional on **top-five selection**, not sensitivity rates.
- **`1213_1` is weak:** the largest displayed leak-onset Z across the three segments is only **2.41**; Reynolds transitions sometimes produce larger immediate Z values.
- **f2500 vs f315, run `1211_1`:** f2500 shows onset Z ≈ **5.84 / 4.62 / 5.40**, compared with f315 **0.77 / 0.67 / 0.40**, ordered UUS-US / US-DS / DS-DDS. This shows better immediate-onset response in **this run**, not necessarily better ongoing-leak detection.
- Some of the largest jumps occur **outside** the segment containing the known physical leak, so a large Z by itself **cannot localize** that leak.
- The saved plotting cell generated **90 separate event plots** (45 first-leak and 45 Reynolds). A later cell re-plots **45 first-leak combinations**, not new independent leak events.

## Limitations and conclusions

- **Known-onset analysis:** event times come from recorded labels; no real-time threshold, detection delay, false alarms per hour, or field operating point has been validated.
- **Healthy sampling:** 16 pseudo-onsets per run/segment are too limited to establish an operational false-positive rate, even when the sampled exceedance fraction is zero.
- **Recovery:** one return inside a tight band is **not** stable recovery. Plots can show a persisting level shift after the green dot; that effect is **not measured** by the notebook's `late_baseline_shift` column.
- **Run inconsistency:** results from `1213_1` prevent a claim of reliable detection across all runs.

**Conclusion:** The most promising **instantaneous event-onset** candidates in these saved results are **f2500 and f3100**. A continuous leak detector and reliable leak localization are **not established**.

## Saved output files and execution status

The notebook writes:

- `event_inventory.csv`
- `event_aligned_transient_metrics.csv`
- `transient_reynolds_vs_first_leak_comparison.csv`
- `transient_comparison_essential.csv`
- `healthy_sham_event_inventory.csv`
- `healthy_sham_transient_metrics.csv`
- `healthy_sham_peak_summary.csv`
- `event_plots/` with separate figures for the two event types

**Reproducibility note:** The uploaded notebook has saved analysis outputs, but its **final assertion/check cell has no saved execution output**. The annotated version preserves this status; the full notebook was **not rerun against `data/all_segments.csv`** during documentation editing.
