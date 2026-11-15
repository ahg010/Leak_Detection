
# Robust Acoustic Onset Detection with Healthy Baseline Comparison
## 1. Executive summary

**Goal.** Assess whether acoustic frequency amplitudes change **immediately at the recorded onset of the first gas leak** more than they change during (a) a healthy Reynolds-number transition from **100 to 150**, or (b) normal fluctuations at a stable **Reynolds level of 150**. Characterize the **first observed return to the original baseline band** following a qualifying onset jump.

**Core method.** For each of five experimental runs, each of three adjacent sensor pairs, and each of 26 frequency features, use the preceding **60 seconds** to estimate a baseline median and a robust noise scale based on median absolute deviation (MAD). Compare **only the value at the exact event timestamp** with that baseline. Then examine whether the onset reading was outside the existing **±2 robust-noise band**, and, if so, when the signal first re-enters that band during the next **60 seconds**. Compare the leak-onset magnitude with the same measurement at a healthy **100→150** transition and at sampled stable-Re=150 healthy pseudo-events.

**Main finding from the notebook's saved results.** Frequencies **f2500** and **f3100** repeatedly produce large normalized leak-onset responses in **four of the five runs**. Run **`1213_1`** is a major exception. Large spikes also occur in sensor pairs **outside** the known leak-containing segment, so amplitude alone does not locate the leak. **This is an event-aligned exploratory analysis; it is not an operationally validated leak detector.**

### Questions the notebook addresses

1. **Does a leak produce a sudden acoustic jump at the recorded onset, rather than only a later change?**
2. **Which frequency and sensor-pair combinations show larger onset jumps at a leak than at a healthy Reynolds 100→150 transition?**
3. **Are leak-onset jumps unusual compared with sampled event-free, healthy Re=150 fluctuations?**
4. **For onset excursions that leave the baseline band, how soon does the first observed return occur?**
5. **Do these patterns recur across runs and segments, and what prevents a stronger detection or localization claim?**

### Scope of the claim

The notebook knows the experiment's **true event timestamps**. It measures responses at those timestamps; it does **not** infer an unknown leak-onset time from the acoustic signal. Consequently, its rankings do not by themselves establish sensitivity, false alarms per hour, detection delay, classification of an ongoing leak, or leak-location accuracy.

---

## 2. Files and reproduction

### Notebook

- **Annotated notebook with interpretation:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY_results_ANNOTATED.ipynb`
- **Original executed notebook with saved outputs:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY_results.ipynb`
- **Underlying computational version:** `event_aligned_IMMEDIATE_ONSET_jumps_VALID_RECOVERY.ipynb`

The annotated notebook adds explanatory Markdown cells. **Its computational code and existing saved outputs were preserved.** This README documents that implementation; it does not introduce a different method.

### Input data

The notebook reads:

```text
data/all_segments.csv
```

From the repository root, the established timestamp-matched dataset-generation command is:

```bash
python src/convert_probe_data_to_segments_matched.py data/2026-03-04 data/all_segments.csv
```

The input folder contains the original experimental probe CSV files. The generated analysis CSV represents timestamp-matched adjacent sensor measurements, keeping **each segment separately** and retaining the full experimental time series. Its core fields are:

| Field | Meaning |
|---|---|
| `run_id` | Experiment identifier: `1211_1`, `1212_1`, `1212_2`, `1213_1`, or `1213_2` |
| `segment_id` | One adjacent sensor pair: `UUS-US`, `US-DS`, `DS-DDS` |
| `Date-Time` | Elapsed seconds within a run |
| `Reynolds_level` | Flow condition at that timestamp |
| `leak_active` | Experiment-level indication that the leak is active at that timestamp |
| `contains_leak_site` | Marks **US-DS**, which contains the known physical leak location |
| `upstream_minus_downstream__f...` | **Signed** upstream minus downstream acoustic amplitude at the specified frequency |

**Important:** `contains_leak_site=False` does **not** mean that a segment cannot respond acoustically to the leak. Likewise, `leak_active=True` is a run-level event state and does not place a leak inside every segment.

### How to run

The notebook resolves the repository root when launched from either the repository root or its `notebooks/` directory. Keep the existing `data/all_segments.csv` layout and execute the notebook cells in order. Its outputs are written to:

```text
results/event_aligned_immediate_onset_jumps/
```

Python dependencies used in the notebook include `numpy`, `pandas`, `matplotlib`, and `IPython` for result displays. No LSTM training or CUSUM model is required to execute this notebook.

---

## 3. Experimental design and event definitions

The experiment has **four probes** and **three adjacent directed pairs**:

```text
UUS ----- US ----- DS ----- DDS
     |         |         |
   UUS-US    US-DS     DS-DDS
              ^
         Known leak site
```

Each of the three segment signals is analyzed independently. The method does **not** aggregate segment amplitudes or select the segment containing the leak before ranking frequencies.

### Events under comparison

| Event | Pre-event physical state | Event boundary | Post-event state used |
|---|---|---|---|
| Healthy Reynolds change | Healthy **Re=100**, before first leak | First observed **100→150** Reynolds transition | Healthy **Re=150**, before first leak |
| First leak onset | Healthy **Re=150**, before first leak | First `leak_active=True` timestamp | First continuous active-leak block at **Re=150** |
| Healthy pseudo-event | Stable healthy **Re=150**, before first leak | A selected observed timestamp with no physical event | Still stable healthy **Re=150** |

The first leak time is determined **globally for each run**, using the run's full timeline. It is not determined separately by searching for amplitude spikes in each segment. This matters when a sensor pair lacks a synchronized sample: a missing observation cannot shift the defined event timestamp.

The notebook **never treats a later inactive period after the first leak as healthy**, even if `leak_active` becomes false again.

### Recorded event times in the saved execution

| Run | Healthy Reynolds 100→150 at (s) | First leak onset at (s) | Elapsed interval (s) |
|---|---:|---:|---:|
| `1211_1` | 2400 | 3000 | 600 |
| `1212_1` | 2400 | 3000 | 600 |
| `1212_2` | 2400 | 3000 | 600 |
| `1213_1` | 2700 | 3300 | 600 |
| `1213_2` | 2400 | 3000 | 600 |

These timestamps are **recorded state boundaries**, not timestamps estimated from the acoustic data.

---

## 4. Exact-onset measurement: baseline, MAD, and Z-score

For one `run_id`, one `segment_id`, one frequency, and one recorded event at `t0`, consider the **60 seconds immediately preceding that event**. The notebook uses **only pre-event samples in the appropriate physical state** described above.

### Step 1: Local baseline median

$$
B = \operatorname{median}\left(A(t):t_0-60 \le t < t_0\right)
$$

Here, `A(t)` is the signed upstream-minus-downstream amplitude for the selected sensor pair and frequency, **restricted to the relevant pre-event condition**.

### Step 2: Median absolute deviation and robust noise

$$
\mathrm{MAD}_{\mathrm{pre}} = \operatorname{median}\left(\left|A(t)-B\right|\right)
$$

$$
\sigma_{\mathrm{pre}} = 1.4826\,\mathrm{MAD}_{\mathrm{pre}}
$$

The constant **1.4826** converts MAD to a standard-deviation-comparable scale for approximately normally distributed noise. It is **not** a leak threshold. MAD is more resistant than ordinary standard deviation to occasional large pre-event observations.

The two real events **do not share a noise estimate**:

- The **Reynolds-transition Z-score** uses the preceding **Re=100 healthy** observations.
- The **first-leak Z-score** uses the preceding **Re=150 healthy** observations.

Thus, the two Z-scores measure how unusual their respective onset amplitudes are **relative to the noise conditions immediately before each event**. They are not differences in a common raw-amplitude unit.

### Step 3: Immediate jump at exactly `t0`

$$
\Delta_{0} = A(t_0)-B
$$

$$
Z_{0} = \frac{\left|A(t_0)-B\right|}{\sigma_{\mathrm{pre}}}
$$

- `peak_signed` retains the sign of the deviation from the baseline.
- `peak_abs` is the absolute magnitude of this deviation in the original amplitude units.
- `peak_z` is its absolute magnitude divided by the local noise scale.
- `time_to_peak_s` is **0 seconds** for a valid measurement, because **only `t0` qualifies**.
- `first_sample_jump` is a **different** diagnostic: `A(t0)` minus the immediately preceding measured amplitude, whereas `peak_signed` subtracts the **60-second median**.

Despite their historic `peak_*` names, these are **not maxima over a post-event search window**. A spike at `t0+5` or `t0+20` cannot increase the event's `peak_z`.

### Data sufficiency and timestamp requirements

The code requires at least **30 usable pre-event amplitude samples** (`MIN_PRE_SAMPLES=30`), an amplitude reading **at exactly `t0`**, and a preceding observation within **2.5 seconds**. If these conditions are not met, the immediate-onset measurement may be unavailable and a status field records why. A later available sample is **not substituted** for a missing `t0` sample.

If the pre-event robust noise scale is zero or unavailable, `peak_z` is undefined rather than being assigned an artificial value.

### What a large Z-score does—and does not—mean

A value of `leak_peak_z=8` means the **observed amplitude at the known leak onset** differs from its pre-leak median by eight times its own estimated robust noise scale. It does **not** mean the original amplitude is eight, nor that this jump has an eight-standard-deviation Gaussian tail probability. Acoustic observations are not assumed independent or Gaussian for inference here.

---

## 5. Recovery measurement: a distinct question

The notebook defines an original pre-event baseline band:

$$
B-2\sigma_{\mathrm{pre}}\ \le\ A(t)\ \le\ B+2\sigma_{\mathrm{pre}}
$$

**Recovery is assessed only when the event-onset observation is outside this band**, i.e. when `peak_z > 2`.

1. **Onset Z ≤ 2:** The onset did **not** leave the band; recovery is **not applicable** and no green dot is plotted.
2. **Onset Z > 2, with a later in-band observation:** Record the **first subsequent observed timestamp** within the band, searching no farther than **60 seconds after onset**. `recovery_time_s` is that timestamp minus `t0`.
3. **Onset Z > 2, with no in-band observation in the search window:** `recovery_time_s` is `NaN`; the data do not show a return **within that window**.

The separate Boolean `next_sample_returned_to_baseline` describes whether the **very next adjacent observation**, within the existing **2.5-second** adjacency rule, is already inside the band. It should **not** be confused with the first in-band observation that may occur several seconds later.

### Why recovery needs careful interpretation

The green marker documents **one observed band re-entry**, not sustained recovery. A series can briefly cross back into its original band and then stay at a different post-leak level. This is visible in some of the f2500 plots. No stable post-leak baseline shift is computed in the present notebook: `leak_late_baseline_shift` remains unavailable (`NaN`).

Similarly, a short `recovery_time_s` should not automatically be called a desirable property of a leak detector. It is a **descriptive feature of the transient**, and its usefulness for discrimination still needs to be demonstrated.

---

## 6. Healthy Re=150 pseudo-event reference

A large Z-score is more meaningful if similarly large jumps are **rare in comparable healthy operation**. The notebook therefore evaluates the **same `t0`-only jump calculation** at pseudo-onset timestamps selected from healthy **Re=150** observations before the first leak.

Selection and calculation in the existing code:

- Use **observed timestamps**, not an interpolated or resampled grid.
- Space retained candidate pseudo-onsets by at least **30 seconds** (`SHAM_STRIDE_S=30`).
- Require the nominal **60-second pre-window** and **60-second post-window** to remain within one stable, pre-first-leak, event-free **Re=150** period.
- Apply the same immediate-onset baseline/noise calculation to each frequency; maintain separate values for each run and segment.
- In the saved run, **16 pseudo-onset times** were retained for every run/segment combination: **240 times total** (`5 runs × 3 segments × 16`).

This is a **descriptive healthy-background comparison**, not randomized sampling and not a direct measurement of false alarms per hour.

### Healthy metrics

| Metric | Definition | Interpretation |
|---|---|---|
| `n_healthy_shams` | Number of healthy pseudo-onset Z values available for that run/segment/frequency | Sample size for the reference distribution; **16** in the saved tables |
| `healthy_peak_z_p95` | 95th percentile of sampled healthy `t0` Z values | A descriptive upper reference level for ordinary healthy jumps |
| `healthy_peak_z_max` | Largest sampled healthy `t0` Z | Extreme observed among the selected healthy pseudo-onsets |
| `healthy_peak_exceedance_fraction` | Fraction of sampled healthy Z values **at least as large as that case's observed leak Z** | Smaller suggests the leak jump is unusual relative to those sampled healthy times |

For a given run, segment, and frequency, the fraction is calculated as:

$$
\mathrm{ExceedanceFraction} = \frac{\#\{\text{healthy pseudo-onsets with }Z_{\mathrm{healthy}}\ge Z_{\mathrm{leak}}\}}{\#\{\text{valid healthy pseudo-onsets}\}}
$$

With 16 pseudo-onsets, each observation changes the fraction by **1/16 = 0.0625**. A displayed value of **0.0000** means **none of those 16** reached the observed leak-onset Z. It does **not** establish zero future false alarms or a calibrated false-positive rate.

---

## 7. Reading the notebook's result tables

The main comparison has **one row per run, segment, frequency**. In the saved run, this gives:

```text
5 runs × 3 segments × 26 frequencies = 390 comparison rows
```

The real-event metrics include one Reynolds event and one leak event per run:

```text
10 physical event boundaries × 3 segments × 26 frequencies = 780 event-frequency rows
```

### Key columns to inspect

| Column | What it represents | How to read it |
|---|---|---|
| `run_id`, `segment_id`, `frequency` | The measurement identity | Compare the **same** frequency and segment across events and runs |
| `leak_peak_z` | Absolute normalized jump exactly at first-leak onset | A larger value indicates a more unusual onset amplitude relative to local **pre-leak** noise |
| `re_peak_z` | Analogous normalized jump at the healthy **100→150** transition | A smaller value is desirable **when distinguishing leak from that transition** |
| `healthy_peak_z_p95` | 95th percentile from sampled healthy Re=150 pseudo-events | Compare leak Z with typical upper healthy pseudo-event magnitudes |
| `healthy_peak_exceedance_fraction` | Fraction of healthy pseudo-events matching/exceeding leak Z | Small is encouraging but **not** a validated false-positive rate |
| `leak_recovery_time_s` | Time to the **first** observed baseline-band re-entry after a qualifying jump | `NaN` needs `leak_peak_z` and `leak_status` to interpret |
| `leak_returned_to_baseline` | At least one observed return occurred after qualifying onset excursion | **Not** proof of persistent recovery |
| `leak_next_sample_returned_to_baseline` | The very next adjacent sample was already inside the band | A narrower test than eventual first observed return |
| `leak_peak_signed` | Signed deviation at `t0` | The sign can differ across runs and segments |
| `leak_status` | Explanation of available/unavailable onset assessment | Helps distinguish no excursion from missing or insufficient data |
| `leak_late_baseline_shift` | Reserved historical field | **Not calculated** in this notebook; do not interpret its `NaN` as zero shift |

**Important:** `leak_peak_z` and `re_peak_z` each use a **different pre-event baseline and robust noise estimate**, because their preceding Reynolds levels differ. Comparing them answers whether each onset is unusual relative to its own relevant healthy background—not whether the two raw amplitude jumps are numerically identical.

### Why `leak_recovery_time_s` can be `NaN`

| Case | Meaning |
|---|---|
| `leak_peak_z ≤ 2` | No qualifying onset excursion; recovery is **not applicable** |
| `leak_peak_z > 2`, but no later in-band observation within 60 s | An excursion occurred, but no return was **observed** in the available post-event window |
| `leak_peak_z` unavailable | Check `leak_status` for missing onset sample, insufficient pre-samples, non-adjacent preceding sample, or related data limitations |

### What is sorted, and what is not

In the notebook's main frequency tables, **each run and each segment is ranked separately by `leak_peak_z` descending** and the **top five** are displayed. There is **no combined detection score** involving recovery, Reynolds separation, or healthy exceedance. The separate convenience display that includes `f315` and `f630` appends those frequencies for inspection; it does **not** change the underlying rank ordering or the actual comparisons.

Therefore, **appearing in a top-five list** means only being among the five largest immediate leak-onset Z values for that particular run/segment. A frequency absent from a list can still have a nonzero response, and its omission is not a negative detection result.

---

## 8. Saved experimental results

### 8.1 Overall run coverage

The uploaded notebook's saved outputs report:

| Item | Saved result |
|---|---:|
| Source rows | **161,114** |
| Independent runs | **5** |
| Adjacent sensor pairs | **3** |
| Acoustic frequencies | **26** |
| Recorded real event boundaries | **10** (one Reynolds transition and one first leak per run) |
| Event-frequency measurements | **780** |
| Run/segment/frequency comparisons | **390** |
| Healthy pseudo-event timestamps | **240** |
| Event plots from the main plot cell | **90** (45 leak + 45 Reynolds) |

The subsequent plotting cell displays another **45 first-leak figures for the same combinations**; these are **not 45 new leak events**.

### 8.2 Strongest observed onset response by run and segment

The next table reports the **largest leak-onset Z** in the displayed per-run/per-segment top-five results; each entry includes the frequency at which it occurs.

| Run | UUS-US: max leak Z | US-DS: max leak Z | DS-DDS: max leak Z |
|---|---:|---:|---:|
| `1211_1` | **94.35** (`f5000`) | **4.62** (`f2500`) | **5.40** (`f2500`) |
| `1212_1` | **14.02** (`f2500`) | **14.39** (`f6300`) | **29.24** (`f8000`) |
| `1212_2` | **10.74** (`f2500`) | **11.21** (`f2500`) | **4.96** (`f5000`) |
| `1213_1` | **1.49** (`f200`) | **2.37** (`f10000`) | **2.41** (`f10000`) |
| `1213_2` | **8.40** (`f2500`) | **6.43** (`f3100`) | **2.05** (`f25`) |

**Interpretation.** Four runs contain several prominent immediate leak-onset excursions. The fifth, **`1213_1`**, does not show comparable separation: its largest displayed response is only **Z=2.41**. For `1213_1`, the `f10000` Reynolds-transition Z in US-DS (**8.62**) and DS-DDS (**4.41**) is **larger** than the corresponding first-leak Z (**2.37** and **2.41**). This is a warning against declaring that a single large standardized jump reliably identifies a leak.

**Spatial observation.** The largest response is **not consistently in US-DS**, even though that pair contains the known leak. For example, `1211_1` has a **Z=94.35** response at `UUS-US / f5000`, while the strongest US-DS response is **Z=4.62**. Such responses are worth investigating, but **Z-score magnitude alone cannot be used to infer the leak location**.

### 8.3 Frequency recurrence in the displayed top-five tables

There are **5 runs × 3 segments = 15 possible top-five tables** for each frequency. The table below is calculated from the **75 rows displayed in the saved main ranking cell** (five highest-Z frequencies for each run/segment). The medians below use **all appearances** in those top-five tables, including weak onsets.

| Frequency | Runs represented | Top-five appearances (out of 15) | Median leak-onset Z | Median Reynolds-onset Z | Onset Z > 2 | First observed return among appearances |
|---|---:|---:|---:|---:|---:|---:|
| **f2500** | **4/5** | **9/15** | **8.40** | **0.26** | **8/9** | **8/9** |
| **f3100** | **4/5** | **9/15** | **6.43** | **0.30** | **8/9** | **8/9** |
| **f5000** | **4/5** | **7/15** | **6.15** | **0.78** | **6/7** | **6/7** |
| f4000 | 3/5 | 5/15 | 4.10 | 0.46 | 4/5 | 4/5 |
| f6300 | 3/5 | 5/15 | 14.39 | 0.55 | 3/5 | 3/5 |
| f8000 | 4/5 | 7/15 | 2.85 | 0.57 | 5/7 | 5/7 |

**Correct denominator for f2500.** There are **9** top-five appearances. **Eight** of the nine exceed Z=2 and return within the observation window. The median leak Z is **8.40 across all nine**, whereas **8.92** is the median if only the eight qualifying (>2) entries are retained. Those are different summaries and must not be interchanged.

**Selection bias.** These medians are conditioned on **being one of the top five for a run and segment**. They cannot be interpreted as average performance over all 15 run/segment combinations. Likewise, 9/15 is a **top-five appearance frequency**, not 60% leak-detection sensitivity.

### 8.4 Why f2500 and f3100 are the strongest exploratory candidates

- **f2500:** In four runs, it frequently has a large onset Z, low corresponding Reynolds Z, and low sampled healthy exceedance. Its direction is **not fixed**: `leak_peak_signed` can be positive in some runs and negative in others. Consequently, the study uses an **absolute standardized onset deviation**, not a one-sided positive-jump requirement.
- **f3100:** Also appears in **9/15** top-five tables across four runs and has **8** qualifying excursions among those appearances. Some responses are exceptionally large, especially `1211_1 / UUS-US` and `1212_1 / DS-DDS`.
- **f5000:** Also promising, including the exceptional `1211_1 / UUS-US` response, but has fewer top-five appearances (**7**) than f2500 or f3100.
- **f6300:** Its median among selected appearances is high (**14.39**), but it appears in only **3 runs**, and only **3/5** top-five entries are qualifying onset excursions. One impressive conditional median is **not** enough to establish more reproducible detection.

The preference for f2500 and f3100 is **exploratory**, based on **recurrence and separation within these saved known-onset comparisons**, not a fitted or externally validated model-selection procedure.

### 8.5 Concrete comparison: f315 versus f2500 in run `1211_1`

The saved plots provide a particularly useful visual contrast:

| Segment | `f315` leak onset Z | `f2500` leak onset Z |
|---|---:|---:|
| UUS-US | 0.77 | **5.84** |
| US-DS | 0.67 | **4.62** |
| DS-DDS | 0.40 | **5.40** |

- At **f315**, the exact onset readings are still inside the established baseline band. No recovery measurement is applicable.
- At **f2500**, the onset readings are outside the band across all three segments.
- This shows a stronger **instantaneous** leak-onset response at f2500 in **that run**.
- The f2500 plots can also show deviations **before** the labeled onset and apparent differences between post-leak levels and the old baseline. Those patterns are **not quantified** by the `t0` Z-score. They motivate checking event timing and the original probe signals before inferring a physical mechanism.

The UUS-US f2500 onset Z of **5.84** does **not** occur among the displayed top five for that run/segment because other frequencies have even larger Z; **absence from the top-five table is not absence of a jump**.

---

## 9. How to inspect the event-aligned plots

For each selected frequency and run, the plotting code generates **separate figures** for:

1. **HEALTHY REYNOLDS 100→150**, and
2. **FIRST LEAK ONSET (Re=150)**.

Each figure contains **three panels**: UUS-US, US-DS, DS-DDS, with x-axis in **seconds relative to the recorded event** (`t0=0`) and y-axis showing **signed upstream minus downstream amplitude**. The normal context is **60 seconds before** and **60 seconds after** the event, subject to the existing event-state filtering.

### Legend and markers

| Visual element | Meaning | Caution |
|---|---|---|
| Blue trace | Pre-event samples in the prescribed healthy Reynolds state | Includes normal fluctuations and possibly isolated spikes |
| Orange trace | Post-event samples in the prescribed physical event state | Shape after `t0` does **not** alter the onset Z ranking |
| Vertical dashed line | **Recorded** event boundary at `t0=0` | Not an acoustically inferred change point |
| Gray dashed horizontal line | Pre-event median baseline `B` | Local to this run, segment, frequency, and event |
| Gray dotted horizontal lines | `B ± 2 × sigma_pre` baseline band | Used for onset excursion and band-return status |
| Red X | Observed acoustic amplitude **at exactly `t0`** | The red X itself is in raw y-axis amplitude units, **not in Z units** |
| Green dot | **First subsequent in-band observation**, only if onset Z > 2 | It is not proof that the signal subsequently stays recovered |

**Why inspect the plots if the ranking uses only onset Z?** The plots can reveal suspicious **pre-onset spikes**, apparent timestamp alignment problems, **persistent post-event level changes**, spikes after onset, and shared versus different responses across segments. Those features can challenge the narrow interpretation of the onset score, even though the current notebook does not quantitatively score them.

### How to interpret labels

- `onset Z=0.77, no onset excursion; recovery N/A`: red X is inside the band; **no green dot should appear**.
- `onset Z=5.84, first return=1.0s, next-return=True`: there was a qualifying onset excursion, and the next adjacent sample is the first observed in-band return.
- `onset Z=5.40, first return=10.0s, next-return=False`: the first observed in-band return is ten seconds after onset; the very next adjacent sample **did not** return.
- `no observed return`: the onset excursion was observed, but no qualifying return was found in the available 60-second post-onset context.

A green dot while the orange trace remains generally shifted is **not contradictory under the current definition**: the dot marks the **first individual in-band point**, not a stable post-leak state.

---

## 10. Output files and what to use each for

All generated files live under:

```text
results/event_aligned_immediate_onset_jumps/
```

| Output | Contents | Primary use |
|---|---|---|
| `event_inventory.csv` | Recorded event timestamps and event types per run | Confirm which physical boundaries were analyzed |
| `event_aligned_transient_metrics.csv` | Per-event, per-segment, per-frequency baseline, onset, status, and recovery fields | Audit individual measurements and missing values |
| `healthy_sham_event_inventory.csv` | Selected event-free healthy pseudo-onset timestamps | Inspect how background times were chosen |
| `healthy_sham_transient_metrics.csv` | Per-pseudo-onset, per-frequency Z and recovery measurements | Explore background fluctuations beyond the summary percentile |
| `healthy_sham_peak_summary.csv` | Count, 95th percentile, and maximum healthy pseudo-onset Z | Compare leak responses with stable healthy Re=150 behavior |
| `transient_reynolds_vs_first_leak_comparison.csv` | Joined leak, healthy Reynolds, and healthy pseudo-event measurements | Most complete quantitative comparison |
| `transient_comparison_essential.csv` | Reduced main comparison columns | Review the principal per-frequency metrics |
| `event_plots/` | Saved event-aligned PNGs for each plotted run/frequency/event type | Inspect timing and signal shape visually |

### Minimal working interpretation of a result row

For one `run_id`, `segment_id`, and `frequency`:

1. Start with **`leak_peak_z`**: was the amplitude at the **known leak onset** unusually far from its local pre-leak baseline?
2. Compare **`re_peak_z`**: was the corresponding **healthy flow change** similarly unusual relative to its own baseline?
3. Compare **`healthy_peak_z_p95`** and **`healthy_peak_exceedance_fraction`**: did the selected stable healthy Re=150 pseudo-onsets commonly reach that leak jump size?
4. If `leak_peak_z > 2`, inspect **`leak_recovery_time_s`** and the plotted trace; do **not** infer sustained recovery from one band crossing.
5. Check the **same frequency across all runs and all three segments**. A single highly ranked row is insufficient to establish a repeatable leak signature.

---

## 11. Limitations: what this study does not establish

### 11.1 Known-onset evaluation, not blind detection

The event timestamp is supplied by `leak_active` and `Reynolds_level`. A deployed detector would need to discover an event **without those labels**. The reported Z-scores are descriptive measurements of known boundaries, not detection alarms produced in real time.

### 11.2 Weakness in run `1213_1`

In `1213_1`, no segment has a first-leak top-frequency Z above **2.41**, and the Reynolds event can cause a larger standardized jump at the same frequency. A reliable across-run conclusion is therefore **not supported** by these saved results.

### 11.3 Healthy comparison sample size and non-independence

There are **16** sampled healthy Re=150 pseudo-onsets per run/segment in the saved execution. These observations are separated in time but come from the **same underlying continuous experiment**, so independence and full coverage of possible operating conditions are not guaranteed. A measured exceedance fraction of zero means **zero of 16 sampled times**, not a certified zero false-alarm probability.

### 11.4 Top-five selection inflates apparent frequency strength

The frequency table above summarizes **only the five largest leak-onset Z values in each run/segment**. Frequencies outside those top fives are missing from that summary, even though they are present in the full comparison CSV. Medians or recovery fractions calculated from the selected appearances can be optimistic and **must not** be presented as performance across all 390 comparisons.

### 11.5 Recovery is a first crossing, not sustained normalization

The current recovery result can be triggered by **one sample** inside the band, even if subsequent observations remain elevated or depressed. Persistent post-leak shifts and the duration of an abnormal state are **not** measured by the recovery field. The `late_baseline_shift` field remains `NaN` and does **not** support any conclusion about a lasting change.

### 11.6 Spatial response is not leak localization

Strong onset Z-scores appear outside **US-DS**, the known leak-containing segment. Without additional localization evidence, ranking the largest segment Z would be an unsupported location estimator.

### 11.7 Temporal alignment and physical interpretation

Certain plots show conspicuous spikes **just before** the recorded `t0`. The current method does not move the event or search for delayed peaks; therefore those pre-onset excursions do not enter `peak_z`. The discrepancy should be checked against the original probe records and event labels before assigning a physical explanation.

### 11.8 No calibrated operational accuracy statistics

The notebook does not report a validated **event-level recall**, **false alarms per hour**, **detection delay on unseen runs**, or **leak-location error**. The `Z > 2` condition determines **whether recovery is meaningful**, not a validated deployed alarm rule. No performance claim should replace those missing evaluations.

---

## 12. Conclusions

1. **Evidence of immediate acoustic leak-onset transients:** Some frequencies show unusually large normalized deviations **at the recorded first-leak boundary**, notably in four runs.
2. **Leading exploratory frequencies:** **f2500** and **f3100** recur most frequently among the displayed strongest responses. **f5000** is another notable candidate, though less recurrent in these tables.
3. **Leak versus Reynolds distinction:** Many selected cases exhibit much larger normalized leak Z than healthy Reynolds-transition Z, but this is not true in every run or frequency.
4. **Healthy comparison:** Several large leak jumps are not matched by any of the **16 selected healthy Re=150 pseudo-onsets** for the same run, segment, and frequency; this is encouraging but insufficient for a low-false-alarm claim.
5. **Recovery:** First observed baseline-band return can be characterized, but **sustained recovery is not evaluated**.
6. **Major unresolved issues:** **`1213_1`**, onset-timing ambiguity in certain plots, top-five selection effects, and large responses in segments away from the physical leak.

**Final assessment:** This is the **most promising exploratory approach among the evaluated acoustic comparisons for identifying immediate changes at known leak onset**. The current evidence **does not establish a reliable continuous leak detector**, does not prove the best frequency across all operating conditions, and does not determine leak location.

## 13. Documentation and validation status

- This README expands interpretation of the **existing implementation and saved outputs**; it does **not** alter parameters, data handling, model selection, event identification, or notebook code.
- The uploaded notebook includes saved outputs for the main analyses and figures, which were examined to prepare this README. The main plot cell reports **90 event-aligned figures**.
- The final assertion/check code cell **has no saved execution output** in the uploaded notebook. The check cannot be claimed to have passed based on the file alone.
- The notebook was **not re-executed against the experimental dataset** for this documentation update; the numerical statements above were checked against the saved table outputs, not recomputed from `data/all_segments.csv`.

