# Stage 1 Evaluation — Reynolds Tracking and Healthy Spectrum Prediction

## 1. Objective

Determine whether Stage 1 correctly predicts how the healthy acoustic
spectrum changes with Reynolds number.

Stage 1 receives:
- Reynolds history (40 time steps)
- Sensor position information

Stage 1 predicts:
- Healthy acoustic amplitudes at 27 frequencies for each of 4 sensors

The expected behavior is:

    Reynolds changes
          |
          v
    Healthy acoustic spectrum changes
          |
          v
    Stage 1 predicts these changes
          |
          v
    Actual - Predicted ≈ small, stable residuals

If Stage 1 fails to capture these changes, Stage 2 receives residual
patterns that are unrelated to leakage.

This report evaluates Stage 1 independently. Stage 2 is not used.

---

## 2. Dataset and Evaluation

Validation experiment: 1212_1

Healthy observations evaluated: 7,567

Sensors:
- UUS
- US
- DS
- DDS

Frequencies per sensor: 27

Total predicted amplitudes per observation:

    4 × 27 = 108

Total healthy sensor-frequency predictions evaluated:

    7,567 × 108 = 817,236

Only healthy 40-step windows were retained.

Metrics:

    Residual = Actual - Predicted

    RMSE = sqrt(mean(Residual²))

    Relative RMSE = RMSE / RMS(Actual spectrum)

    Bias = mean(Actual - Predicted)

A positive bias means Stage 1 systematically underpredicts amplitude.
A negative bias means Stage 1 systematically overpredicts amplitude.

---

## 3. Overall Stage 1 Prediction Accuracy

| Metric | Result |
|---|---:|
| Mean endpoint RMSE | 2.398 |
| Median endpoint RMSE | 2.237 |
| Mean relative RMSE | 9.5% |
| Median relative RMSE | 9.1% |
| Maximum endpoint RMSE | 14.099 |

### Interpretation

Across healthy observations, Stage 1 has an average prediction RMSE
of approximately 2.4 amplitude units.

Its relative RMSE is approximately 9.5% of the actual spectrum RMS.

This does not mean that every frequency has a 9.5% error.

Some sensor-frequency combinations are predicted accurately,
while others have much larger errors.

Therefore, aggregate RMSE hides important channel-specific failures.

---

## 4. Does Stage 1 Capture Reynolds Changes?

### 4.1 Stable versus changing Reynolds

| Condition | Observations | Mean RMSE | Median RMSE | Mean relative RMSE |
|---|---:|---:|---:|---:|
| Stable Reynolds | 3,895 | 2.272 | 2.191 | 9.07% |
| Changing Reynolds | 3,672 | 2.532 | 2.349 | 10.01% |

During Reynolds changes:

    RMSE increases by approximately 11.5%.

    Relative RMSE increases from 9.07% to 10.01%.

### Finding 1

Stage 1 predicts the healthy acoustic spectrum less accurately
during changing Reynolds conditions.

This is direct evidence that Stage 1 does not completely account
for the effect of Reynolds transitions.

However, it does not prove that the model has a temporal lag.
The increased error could also reflect systematic bias,
unmodeled operating conditions, or higher acoustic variability.

---

## 5. How Does Accuracy Change with Reynolds Number?

| Reynolds range | Observations | Mean RMSE | Relative RMSE |
|---|---:|---:|---:|
| <10 | 1,140 | 2.101 | 8.96% |
| 10–25 | 2,045 | 2.148 | 9.09% |
| 25–50 | 1,461 | 2.240 | 9.21% |
| 50–75 | 450 | 2.498 | 9.89% |
| 75–100 | 1,011 | 2.559 | 9.92% |
| 100–125 | 450 | 3.274 | 11.65% |
| 125–150 | 1,010 | 2.870 | 10.00% |

### Finding 2

Stage 1 prediction error generally increases at higher Reynolds
numbers, although the relationship is not strictly monotonic.

The largest mean error occurs at Reynolds 100–125:

    Mean RMSE = 3.274
    Relative RMSE = 11.65%

Compared with Reynolds below 10:

    Mean RMSE = 2.101
    Relative RMSE = 8.96%

The higher-Reynolds range has approximately 56% greater
absolute RMSE.

Importantly, relative RMSE also increases.

This suggests the increase is not explained solely by
larger acoustic amplitudes at higher Reynolds numbers.

### Correlation analysis

    corr(Reynolds, RMSE)          = +0.494

    corr(Reynolds, Relative RMSE) = +0.259

    corr(|Change in Reynolds|, RMSE) = +0.461

### Interpretation

Both Reynolds level and Reynolds changes are associated with
Stage 1 prediction errors.

The model has not learned a completely Reynolds-invariant
healthy residual representation.

---

## 6. Which Frequencies Does Stage 1 Predict Poorly?

The following sensor-frequency combinations have the largest RMSE.

| Sensor | Frequency | RMSE | Bias | Actual/predicted correlation |
|---|---|---:|---:|---:|
| DS | 250 Hz | 9.299 | -8.919 | 0.333 |
| US | 80 Hz | 6.718 | +5.824 | 0.867 |
| US | 50 Hz | 5.227 | +2.406 | 0.879 |
| US | 31.5 Hz | 5.142 | +3.765 | 0.773 |
| US | 40 Hz | 4.469 | +2.260 | 0.775 |
| US | 63 Hz | 4.138 | +2.693 | 0.888 |
| US | 100 Hz | 4.018 | +2.701 | 0.889 |
| DS | 160 Hz | 3.650 | -2.504 | 0.873 |

### Finding 3 — Significant systematic bias

Two channels are particularly concerning.

#### DS / 250 Hz

    RMSE = 9.299
    Bias = -8.919
    Correlation = 0.333

Stage 1 systematically overpredicts this frequency.

The magnitude of the bias is close to the total RMSE,
suggesting that systematic prediction offset is a major
component of the error.

This is not merely random prediction noise.

#### US / 80 Hz

    RMSE = 6.718
    Bias = +5.824
    Correlation = 0.867

Stage 1 systematically underpredicts this frequency.

The relatively high correlation indicates that the model
captures some variation in the measured amplitude, but
its predicted amplitude level is substantially biased.

### Important distinction

A model can have a high correlation with actual amplitudes
while still producing inaccurate predictions.

For example:

    Actual:     20, 25, 30
    Predicted:  15, 20, 25

Correlation = 1.0

But every prediction is 5 units too low.

This is relevant to the US / 80 Hz results.

---

## 7. Which Frequencies Are Most Affected by Reynolds Transitions?

The following channels exhibit the largest increases in RMSE
when Reynolds is changing.

| Sensor | Frequency | Stable RMSE | Transition RMSE | Increase |
|---|---|---:|---:|---:|
| US | 40 Hz | 3.341 | 5.313 | +1.972 |
| US | 31.5 Hz | 4.249 | 5.857 | +1.608 |
| DDS | 50 Hz | 2.238 | 3.829 | +1.591 |
| US | 160 Hz | 2.118 | 3.534 | +1.416 |
| DDS | 63 Hz | 1.786 | 3.174 | +1.388 |
| DDS | 315 Hz | 1.912 | 3.245 | +1.333 |
| DS | 160 Hz | 2.954 | 4.198 | +1.244 |
| US | 315 Hz | 2.463 | 3.633 | +1.169 |

### Finding 4

Reynolds transitions do not affect all frequencies equally.

Some channels deteriorate substantially during transitions,
while others remain relatively stable.

For example:

    US / 40 Hz

    Stable RMSE     = 3.341
    Transition RMSE = 5.313

    Increase ≈ 59%

And:

    DDS / 50 Hz

    Stable RMSE     = 2.238
    Transition RMSE = 3.829

    Increase ≈ 71%

This is important because Stage 2 receives individual residual
channels, not just one aggregate RMSE value.

Even when overall Stage 1 error changes modestly, certain
frequencies can develop much larger errors.

---

## 8. Does Stage 1 Have a Prediction Lag?

The notebook also generated:

    1212_1_rmse_since_reynolds_change.csv

This attempts to measure prediction errors at different
time intervals after Reynolds changes.

However, the current results are not sufficient to
establish a meaningful recovery time.

For example:

| Steps since Reynolds change | Observations | Mean RMSE |
|---|---:|---:|
| 0 | 3,672 | 2.532 |
| 1 | 6 | 2.949 |
| 2 | 6 | 2.614 |
| 3 | 6 | 2.574 |
| 4 | 6 | 2.759 |
| 5 | 6 | 3.154 |

The first group includes thousands of observations,
while subsequent groups contain only six each.

These groups are not directly comparable.

### Finding 5

We have evidence of higher prediction errors during
Reynolds changes, but we have NOT established that
Stage 1 responds too slowly.

To test lag properly, we need to identify independent
Reynolds transitions and align the actual and predicted
frequency trajectories around those events.

---

## 9. Why This Matters for Stage 2

The complete architecture is:

    Reynolds history
          |
          v
    Stage 1 healthy-spectrum prediction
          |
          v
    Actual spectrum - Predicted spectrum
          |
          v
    Residual sequence
          |
          v
    Stage 2 leak classifier

Ideally, during healthy conditions:

    Reynolds changes
          |
          v
    Stage 1 captures acoustic changes
          |
          v
    Small residuals
          |
          v
    Stage 2 predicts no leak

But our results demonstrate:

    Reynolds changes
          |
          v
    Stage 1 prediction accuracy deteriorates
          |
          v
    Some frequencies develop larger residuals
          |
          v
    Stage 2 receives Reynolds-dependent residual patterns

These patterns may be mistaken for leak-related changes.

This provides a plausible mechanism for the elevated
false-positive rate during Reynolds transitions.

### Critical qualification

We have not demonstrated that these specific Stage 1
errors cause Stage 2 false positives.

That requires linking the identified residual patterns
to Stage 2 predictions at the same observations.

---

## 10. Connection to the Previous Stage 2 Evaluation

The earlier validation analysis found:

    Stable Reynolds:
        False-positive rate = 4.23%

    Changing Reynolds:
        False-positive rate = 8.05%

The current Stage 1 analysis found:

    Stable Reynolds:
        Mean RMSE = 2.272

    Changing Reynolds:
        Mean RMSE = 2.532

Together, these results show:

1. Stage 1 prediction error increases during Reynolds changes.
2. Stage 2 false positives are more frequent during Reynolds changes.

These findings are consistent with Stage 1 contributing
to the false-positive problem.

However, they do not establish a causal relationship.

The analyses also use different observation-selection rules,
so a direct comparison should align the exact observation
indices and transition definitions.

---

## 11. Recommended Next Steps

### Priority 1 — Investigate systematic prediction bias

Start with:

    DS / 250 Hz
    US / 80 Hz
    US / 31.5 Hz

These channels have substantial prediction errors
even in healthy conditions.

Check whether the bias is present in training data,
validation data, or both.

If the bias appears only in validation, investigate
data distribution shift and preprocessing consistency.

### Priority 2 — Analyze Reynolds-sensitive frequencies

Focus on:

    US / 40 Hz
    US / 31.5 Hz
    DDS / 50 Hz
    US / 160 Hz

Compare actual and predicted amplitudes around
specific Reynolds transitions.

Determine whether the errors reflect:

- Systematic underprediction or overprediction
- Delayed model response
- Increased measurement noise
- Missing operating-condition information

### Priority 3 — Connect Stage 1 errors to Stage 2 false positives

Join the Stage 1 residual data with the existing
Stage 2 validation predictions using observation_index.

For healthy observations, compare:

    Stage 2 false positives
              versus
    Stage 2 true negatives

Specifically test whether the frequencies with
large Reynolds-transition errors are also the
frequencies associated with false alarms.

### Priority 4 — Validate preprocessing and calibration

Before retraining Stage 1, verify:

- Reynolds normalization
- Frequency-amplitude normalization
- Sensor ordering
- Consistency between training and validation
- Output inverse transformations
- Sensor-position handling

Large systematic biases should not automatically
be attributed to insufficient model capacity.

---

## 12. Final Assessment

### Question

Does Stage 1 successfully capture the effect of
Reynolds changes on healthy acoustic spectra?

### Answer

**Partially, but not consistently across all frequencies
and operating conditions.**

Evidence:

1. Stage 1's mean relative RMSE is approximately 9.5%.

2. Prediction error increases during Reynolds transitions.

3. Higher Reynolds ranges generally have greater errors.

4. Several frequencies have substantial systematic bias.

5. Some frequencies deteriorate by more than 50% during
   Reynolds transitions.

6. The available results do not establish temporal lag.

### Main Conclusion

Stage 1 does not completely remove Reynolds-dependent
variation from the healthy acoustic spectra.

Consequently, Stage 2 receives residuals that can contain
both:

    A. Deviations associated with actual leaks

    B. Deviations caused by imperfect healthy-spectrum prediction

This makes leak classification more difficult.

The next step should not be immediate retraining.

First, determine whether Stage 1's systematic biases and
Reynolds-transition residual patterns are responsible for
the specific false positives observed in Stage 2.

That investigation will help determine whether improving
Stage 1 is likely to improve the overall detector.
