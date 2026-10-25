# Stage 1 Baseline Error Diagnostics — Evaluation Report

**Experiment:** `1212_1`  
**Source:** `stage1_diagnostics.tar`  
**Model:** Two-stage LSTM leak detector  
**Classification threshold:** 0.50  
**Observations evaluated:** 10,762

## 1. Executive Summary

The objective was to determine whether errors in Stage 1's healthy-spectrum predictions explain the false positives and missed leaks produced by Stage 2.

### Main Findings

1. **False positives do not have higher overall residual RMSE than true negatives.**
2. False positives occur approximately 1.9 times as frequently during changing Reynolds conditions.
3. Stage 1 residual RMSE increases with Reynolds number and Reynolds changes during healthy periods.
4. Some individual probe-frequency residuals are larger during false positives, even though overall RMSE is not.
5. Missed leaks generally have slightly smaller residual magnitudes than correctly detected leaks.
6. The current diagnostics do not establish that Stage 1 is the primary cause of Stage 2's errors.

**Verdict:** Stage 1's aggregate prediction error is not a convincing explanation for the false positives. However, flow-dependent residual behavior and specific sensor-frequency patterns remain plausible contributors.

---

## 2. Classification Results

| Actual / Predicted | No Leak | Leak |
|---|---:|---:|
| No Leak | 7,286 (TN) | 476 (FP) |
| Leak | 1,260 (FN) | 1,740 (TP) |

Definitions:

- **TN:** Correctly identifies a healthy observation.
- **FP:** Reports a leak when the pipe is healthy.
- **FN:** Misses a real leak.
- **TP:** Correctly identifies a leak.

The detector misses 42% of leaking observations and produces 476 false-positive observations.

These are observation-level results, not counts of independent leak or false-alarm events.

---

## 3. Does Stage 1 Residual RMSE Explain False Positives?

Stage 1 estimates the healthy spectrum.

The residual is:

    residual = observed_spectrum - predicted_healthy_spectrum

For each prediction endpoint, residual RMSE is calculated across the four probes and 27 frequencies.

### 3.1 Residual RMSE by Classification Outcome

| Outcome | Observations | Mean endpoint RMSE | Median endpoint RMSE | Mean 40-step RMSE |
|---|---:|---:|---:|---:|
| True Negative | 7,286 | 2.399 | 2.227 | 2.423 |
| False Positive | 476 | 2.363 | 2.319 | 2.375 |
| True Positive | 1,740 | 2.311 | 2.271 | 2.340 |
| False Negative | 1,260 | 2.196 | 2.136 | 2.220 |

### 3.2 Interpretation

The mean endpoint RMSE is:

    False Positive = 2.363
    True Negative  = 2.399

The false-positive mean is approximately 1.5% lower than the true-negative mean.

The median tells a slightly different story:

    False Positive = 2.319
    True Negative  = 2.227

The false-positive median is approximately 4.1% higher.

These mixed results indicate substantial overlap between the two distributions.

### 3.3 Healthy-Period RMSE Quantiles

| Percentile | False Positive | True Negative |
|---|---:|---:|
| 10th | 2.000 | 1.925 |
| 50th | 2.319 | 2.227 |
| 90th | 2.752 | 3.037 |

The upper tail of RMSE is actually larger among true negatives.

### Conclusion

**Large overall Stage 1 residual errors are not sufficient to explain false positives.**

Some healthy observations have substantial baseline residuals without triggering a false alarm.

Conversely, false alarms occur at residual magnitudes that overlap strongly with correctly classified healthy observations.

This suggests that Stage 2 responds to more than overall residual magnitude.

It may respond to particular temporal, frequency, or cross-sensor patterns.

---

## 4. Does Stage 1 Error Depend on Reynolds Number?

The diagnostics include healthy observations grouped by Reynolds range.

| Reynolds range | Healthy observations | Median endpoint RMSE | False positives | FP rate |
|---|---:|---:|---:|---:|
| <10 | 1,140 | 2.065 | 22 | 1.93% |
| 10–25 | 1,521 | 2.111 | 109 | 7.17% |
| 25–50 | 1,500 | 2.098 | 53 | 3.53% |
| 50–75 | 1,050 | 2.265 | 127 | 12.10% |
| 75–100 | 450 | 2.898 | 42 | 9.33% |
| 100–125 | 1,052 | 2.503 | 99 | 9.41% |
| 125–150 | 448 | 2.869 | 14 | 3.13% |
| >150 | 601 | 2.616 | 10 | 1.66% |

### 4.1 Stage 1 Error Changes with Reynolds

During healthy observations, the correlation between Reynolds number and endpoint residual RMSE is approximately:

    corr(Reynolds, RMSE) = +0.487

This indicates a moderate positive association.

Stage 1's absolute prediction errors tend to be larger at higher Reynolds values.

However, this does not automatically mean the model is performing worse in relative terms.

Higher-Reynolds spectra may have larger acoustic amplitudes, making absolute RMSE larger even if relative prediction accuracy remains similar.

### 4.2 False Positives Do Not Simply Follow RMSE

Consider:

    Reynolds 75–100:
        Median RMSE = 2.898
        FP rate     = 9.33%

    Reynolds 125–150:
        Median RMSE = 2.869
        FP rate     = 3.13%

Despite similar median RMSE, the false-positive rates differ substantially.

Likewise:

    Reynolds 50–75:
        Median RMSE = 2.265
        FP rate     = 12.10%

This range has a lower median RMSE but a higher false-positive rate.

### Conclusion

**Stage 1 residual magnitude varies with Reynolds, but residual magnitude alone does not explain the Reynolds-dependent false-positive pattern.**

---

## 5. Are Reynolds Transitions Associated with False Positives?

This is one of the strongest findings in the diagnostics.

### 5.1 Stable vs Changing Reynolds

| Reynolds condition | Healthy observations | False positives | FP rate | Median RMSE |
|---|---:|---:|---:|---:|
| Stable | 3,901 | 165 | 4.23% | 2.1916 |
| Changing | 3,861 | 311 | 8.05% | 2.3351 |

False-positive rate ratio:

    8.05 / 4.23 = 1.90

**False positives are approximately 1.9 times as frequent during changing Reynolds conditions.**

### 5.2 Relationship Between Reynolds Changes and Stage 1 Error

During healthy observations:

    corr(abs(delta_Reynolds), RMSE) = +0.440

This indicates that larger Reynolds changes are associated with larger Stage 1 residual errors.

However, the correlation between healthy-period predicted leak probability and endpoint RMSE is approximately:

    corr(leak_probability, RMSE) = -0.018

This is effectively zero as a linear association.

### Interpretation

Two findings coexist:

1. Reynolds transitions are associated with increased Stage 1 residual RMSE.
2. Reynolds transitions are also associated with more false positives.

But overall residual RMSE does not directly explain the probability of a false alarm.

A possible explanation is that flow transitions produce particular frequency or sensor patterns that Stage 2 mistakes for leaks.

Those patterns need not increase aggregate RMSE substantially.

### Important Qualification

The current stable/changing comparison is observational.

Reynolds transitions occur at particular times and operating regimes, so the difference in false-positive rates may be confounded by Reynolds level, temporal position, or other experimental conditions.

**The results support an association, not a causal conclusion.**

---

## 6. Which Probe-Frequency Residuals Are Associated with False Positives?

The diagnostics compare residual RMSE for each probe and frequency during healthy false positives versus healthy true negatives.

### 6.1 Largest Increases During False Positives

| Probe | Frequency | FP RMSE | TN RMSE | Difference |
|---|---|---:|---:|---:|
| US | f80 | 7.718 | 6.659 | +1.059 |
| DDS | f80 | 3.599 | 2.649 | +0.949 |
| UUS | f80 | 3.094 | 2.333 | +0.762 |
| UUS | f160 | 2.588 | 1.890 | +0.697 |
| DS | f250 | 9.922 | 9.266 | +0.656 |
| US | f200 | 4.231 | 3.613 | +0.618 |
| UUS | f125 | 2.567 | 2.034 | +0.533 |
| US | f100 | 4.424 | 3.992 | +0.432 |

### 6.2 Interpretation

Frequency f80 stands out:

- US f80: higher residual RMSE during false positives.
- DDS f80: higher residual RMSE during false positives.
- UUS f80: higher residual RMSE during false positives.

This suggests that f80 may be worth investigating as a possible contributor to false alarms.

However, these are descriptive comparisons across many probe-frequency combinations.

They do not prove that f80 causes false positives or that Stage 2 assigns high importance to f80.

### 6.3 Some Frequencies Show the Opposite Pattern

Examples:

| Probe | Frequency | FP RMSE minus TN RMSE |
|---|---|---:|
| DDS | f315 | -1.752 |
| UUS | f250 | -1.615 |
| UUS | f315 | -1.557 |
| DDS | f250 | -1.274 |
| US | f50 | -1.192 |

Therefore, false positives are not characterized by uniformly larger residual errors across all frequencies.

**This supports examining the residual pattern rather than only its overall magnitude.**

---

## 7. What Do the Diagnostics Reveal About Missed Leaks?

Compare the two leaking-observation categories:

    True Positive:
        Mean endpoint RMSE = 2.311
        Mean window RMSE   = 2.340

    False Negative:
        Mean endpoint RMSE = 2.196
        Mean window RMSE   = 2.220

Missed leaks have somewhat smaller residual magnitudes on average.

This is consistent with a possible explanation:

    Weaker residual signal
            |
            v
    Less distinguishable leak pattern
            |
            v
    Lower Stage 2 leak probability

However, the difference is relatively modest.

It does not establish that Stage 1 causes missed leaks.

### Important Distinction

During an actual leak, Stage 1 residuals are expected to contain the acoustic deviation caused by the leak.

A large residual during a leaking period is not automatically a Stage 1 prediction error.

Therefore, comparing true-positive and false-negative residuals primarily evaluates the strength of the residual evidence available to Stage 2.

It does not directly measure Stage 1 accuracy under healthy conditions.

---

## 8. What the Timeline Reveals

The synchronized diagnostic plot contains:

1. Actual leak state and predicted probability.
2. Stage 1 endpoint residual RMSE.
3. Stage 1 40-step residual RMSE.
4. Reynolds number.

### Observation A — Residual RMSE spikes do not always trigger leak predictions

There are isolated large endpoint RMSE spikes without corresponding sustained leak probabilities.

This supports the finding that Stage 2 is not simply applying a threshold to overall residual magnitude.

### Observation B — Leak probabilities can change sharply without comparable RMSE changes

Some large changes in predicted probability occur while aggregate residual RMSE remains relatively stable.

This suggests sensitivity to the structure of residuals rather than their total energy alone.

### Observation C — Flow changes coincide with changes in residual behavior

During parts of the Reynolds ramp and subsequent operating changes, the residual RMSE varies noticeably.

This is consistent with the positive correlation between Reynolds changes and residual RMSE.

### Observation D — Temporal stability remains poor

During some sustained leak events, the predicted probability drops toward zero despite the true leak state remaining positive.

The 40-step temporal representation is not producing consistently stable leak detection.

---

## 9. Does Stage 1 Cause the False Positives?

### Evidence Against a Simple Stage 1 Error Explanation

- FP mean RMSE is slightly lower than TN mean RMSE.
- FP and TN RMSE distributions overlap substantially.
- Healthy-period correlation between probability and RMSE is approximately zero.
- Some large residual spikes occur without false alarms.

### Evidence That Stage 1 May Still Contribute

- Residual RMSE is associated with Reynolds number.
- Residual RMSE increases during Reynolds changes.
- False positives are more common during Reynolds changes.
- Specific probe-frequency residuals differ between FP and TN observations.

### Verdict

**The diagnostics do not support the claim that large overall Stage 1 prediction errors are the primary cause of false positives.**

A more plausible unresolved hypothesis is that Stage 2 reacts to particular flow-dependent residual patterns, potentially including artifacts introduced by Stage 1.

The current results cannot separate Stage 1 artifacts from genuine healthy acoustic patterns that Stage 2 misinterprets.

---

## 10. Recommended Next Experiments

### Priority 1 — Examine residual patterns during false positives

For each probe-frequency combination, compare:

    Healthy True Negatives
            versus
    Healthy False Positives

Focus initially on:

    US/f80
    DDS/f80
    UUS/f80
    UUS/f160
    DS/f250

Compare signed residuals, not just RMSE.

This may reveal systematic residual patterns that disappear when absolute values are aggregated.

### Priority 2 — Separate Reynolds level from Reynolds transitions

Evaluate false-positive rates within comparable Reynolds ranges while distinguishing stable and changing flow.

This would help determine whether transitions themselves are associated with false alarms beyond differences in operating regime.

### Priority 3 — Test Stage 2 sensitivity to specific residual features

Use the existing trained model and modify selected residual channels during inference.

For example:

    Original residuals
            |
            v
    Stage 2 probability

    Residuals with f80 channels replaced
    by an appropriate healthy reference
            |
            v
    Stage 2 probability

Compare the resulting probabilities during false-positive periods.

This is a sensitivity test, not a causal proof, because modified inputs may be outside the model's training distribution.

### Priority 4 — Evaluate Stage 1 using healthy data only

Measure baseline prediction quality by Reynolds regime using:

- RMSE.
- MAE.
- Relative or normalized error where appropriate.
- Per-frequency and per-probe residual distributions.

This provides a more direct assessment of Stage 1 than leak-classification outcomes alone.

---

## 11. Final Conclusion

The Stage 1 diagnostic results substantially narrow the investigation.

**The main problem does not appear to be simply that Stage 1 produces large residual errors and Stage 2 interprets them as leaks.**

Instead:

1. Stage 1 residual magnitude varies with operating conditions.
2. False positives are nearly twice as frequent during changing Reynolds conditions.
3. Overall residual RMSE has almost no linear relationship with predicted leak probability during healthy observations.
4. Specific probe-frequency residual patterns differ between false positives and true negatives.
5. Missed leaks have somewhat smaller residual magnitudes, but this does not fully explain their occurrence.

### Overall Assessment

The evidence points toward a **flow-dependent residual-pattern interpretation problem**, rather than a straightforward aggregate Stage 1 accuracy problem.

The next most informative investigation is to identify which residual patterns cause Stage 2 to assign high leak probabilities during healthy Reynolds transitions.

**Important:** All results come from the single validation experiment `1212_1`. They are descriptive findings and do not establish generalization or causality.
