# Leak Detection Model — Validation Evaluation Report

**Experiment:** `1212_1`  
**Model:** Two-stage LSTM (healthy spectral baseline + residual leak detector)  
**Source:** `validation_outputs_reynalds.tar`  
**Classification threshold:** 0.50  
**Window size:** 40 observations

## 1. Executive Summary

The model demonstrates reasonable overall discrimination (ROC-AUC = 0.892), but its performance is inconsistent across leak events and Reynolds numbers.

The main findings are:

1. The model misses 42% of observations where a leak is present.
2. It produces 476 false-positive observations.
3. Leak detection deteriorates substantially at certain Reynolds numbers.
4. Predicted probabilities frequently oscillate between near zero and near one during sustained leaks.
5. The additional Reynolds data reveal that model performance is strongly associated with operating conditions.

**Overall assessment:** The model shows useful leak-detection capability but is not sufficiently reliable for operational deployment in its current form.

---

## 2. Overall Classification Performance

The validation contains 10,762 predictions.

| Metric | Value |
|---|---:|
| Accuracy | 83.87% |
| Precision | 78.52% |
| Recall (Sensitivity) | 58.00% |
| F1 Score | 66.72% |
| ROC-AUC | 0.8918 |
| Average Precision | 0.7651 |
| Brier Score | 0.1443 |

### Confusion Matrix

| Actual / Predicted | No Leak | Leak |
|---|---:|---:|
| No Leak | 7,286 (TN) | 476 (FP) |
| Leak | 1,260 (FN) | 1,740 (TP) |

### Interpretation

- **False positives:** 476 healthy observations incorrectly classified as leaking.
- **False negatives:** 1,260 leaking observations incorrectly classified as healthy.
- **Recall of 58%:** The model misses 42% of the observations during known leak periods.
- **Precision of 78.5%:** Approximately 21.5% of predicted-positive observations are false alarms.

The relatively high ROC-AUC suggests that the model has some ability to rank leaking observations above healthy observations.

However, ROC-AUC does not establish that its probabilities are well calibrated or that the detector performs reliably at the selected operating threshold.

---

## 3. Leak Detection Performance by Reynolds Number

Adding Reynolds number to the output reveals an important relationship between operating conditions and detection performance.

There are five actual leak events, each lasting 600 observations.

| Leak event | Reynolds number | Recall | Mean predicted leak probability |
|---|---:|---:|---:|
| 1 | 150 | 82.0% | 0.804 |
| 2 | 100 | 82.5% | 0.814 |
| 3 | 50 | 44.0% | 0.441 |
| 4 | 25 | 16.8% | 0.168 |
| 5 | 12.5 | 64.7% | 0.651 |

### Key Finding: Detection Is Not Consistent Across Reynolds Conditions

At Reynolds = 150 and 100, the model detects approximately 82% of leaking observations.

At Reynolds = 50, recall drops to 44%.

At Reynolds = 25, recall collapses to 16.8%.

Interestingly, at Reynolds = 12.5, recall increases again to 64.7%.

This is **not a simple monotonic relationship** between Reynolds number and detection performance.

### Interpretation

The model may be learning leak signatures that are more distinguishable under certain flow conditions.

Possible explanations include:

- Acoustic leak signatures change with Reynolds number.
- Signal-to-noise ratios differ across operating conditions.
- Stage 1 baseline errors vary with Reynolds number.
- Stage 2 has not learned sufficiently transferable leak representations.

These explanations are hypotheses, not established causes.

**Important limitation:** Each leaking Reynolds condition occurs in only one event in this validation experiment. Therefore, Reynolds effects are confounded with event order and other time-varying conditions.

We cannot conclude from this experiment alone that Reynolds = 25 intrinsically causes poor detection.

---

## 4. False Positives and Reynolds Number

The additional Reynolds measurements allow us to identify where false alarms occur.

| Reynolds range | Healthy observations | False positives | False-positive rate |
|---|---:|---:|---:|
| 0–10 | 1,140 | 22 | 1.9% |
| 10–25 | 2,123 | 109 | 5.1% |
| 25–50 | 1,500 | 55 | 3.7% |
| 50–75 | 450 | 126 | 28.0% |
| 75–100 | 1,050 | 137 | 13.0% |
| 100–125 | 450 | 3 | 0.7% |
| 125–150 | 1,049 | 24 | 2.3% |

### Important Observation

False positives are not distributed uniformly across Reynolds conditions.

The highest false-positive rates occur at:

- Reynolds 50–75: 28.0%
- Reynolds 75–100: 13.0%

Together, these ranges account for 263 of the 476 false-positive observations.

This suggests that the model may be particularly sensitive to some intermediate-flow conditions.

However, these ranges also include portions of Reynolds transitions.

**We should investigate whether false positives are associated with Reynolds values themselves or with changes in Reynolds number.**

This distinction matters because a model that mistakes flow transitions for leaks has a different failure mechanism from a model that performs poorly at a particular steady-state flow.

---

## 5. False Negatives and Reynolds Number

The missed-leak observations are distributed as follows:

| Reynolds number | Leaking observations | False negatives | Miss rate |
|---|---:|---:|---:|
| 150 | 600 | 108 | 18.0% |
| 100 | 600 | 105 | 17.5% |
| 50 | 600 | 336 | 56.0% |
| 25 | 600 | 499 | 83.2% |
| 12.5 | 600 | 212 | 35.3% |

The most serious problem is at Reynolds = 25.

During that event, the model predicts no leak for 499 of the 600 observations.

This is not merely an issue of occasional noisy predictions.

The model fails to recognize most of a sustained, known leak event.

### Implication

The system cannot currently be assumed to maintain reliable leak detection across the observed operating range.

Performance must be evaluated separately for different Reynolds regimes rather than summarized by one overall accuracy or F1 score.

---

## 6. Temporal Instability of Predictions

The validation graph shows frequent transitions between very low and very high predicted leak probabilities.

During actual leak events, probabilities sometimes fall toward zero even though the leak remains present.

During healthy periods, probabilities occasionally spike toward one.

This suggests that the Stage 2 model is not consistently maintaining its classification across time.

Possible causes include:

1. Sensitivity to short-term acoustic fluctuations.
2. Errors in the Stage 1 healthy-spectrum predictions.
3. Excessive sensitivity in the learned sensor-interaction graph.
4. Insufficient generalization across Reynolds conditions.
5. Differences between training-time and inference-time preprocessing.

The graph alone cannot distinguish these explanations.

### Why this is concerning for an LSTM

One motivation for using a temporal model is to exploit persistence over time.

A sustained leak should provide repeated evidence of an abnormal condition.

However, the observed oscillations indicate that the 40-step LSTM representation does not consistently produce stable probabilities during these events.

This does not prove that the LSTM architecture is unsuitable, but it raises questions about whether it is learning robust temporal leak characteristics.

---

## 7. Additional Insights from Reynolds Measurements

The Reynolds measurements provide information that was missing from the original probability-only graph.

### 7.1 Leak detection depends on operating conditions

The strongest evidence is the substantial variation in recall between the five constant-Reynolds leak events.

This means aggregate evaluation metrics conceal important differences in detection performance.

### 7.2 False alarms may be associated with flow transitions

The elevated false-positive rates in intermediate Reynolds ranges warrant further investigation.

Recommended analysis:

- Calculate the change in Reynolds number between consecutive observations.
- Compare false-positive rates during stable versus changing Reynolds conditions.
- Examine whether Stage 1 residual magnitudes increase during flow transitions.

This would help distinguish baseline-model errors from Stage 2 classification errors.

### 7.3 Stage 1 may be contributing to the problem

Stage 1 predicts the expected healthy spectrum using Reynolds history.

If its predictions are inaccurate at particular Reynolds values or during transitions, Stage 2 receives distorted residuals.

The resulting errors could be interpreted as leak signatures.

A useful next diagnostic would compare Stage 1 residual distributions across:

- Healthy, stable Reynolds conditions.
- Healthy, changing Reynolds conditions.
- Actual leak periods at different Reynolds numbers.

### 7.4 The five leak events provide a useful stress test

The experiment includes leak events at Reynolds numbers:

150, 100, 50, 25, and 12.5.

This provides an opportunity to assess detection across multiple operating conditions within one experiment.

However, because there is only one leak event at each Reynolds level, the results should not be interpreted as independent estimates of performance for each Reynolds regime.

---

## 8. Recommended Next Steps

### Priority 1 — Verify the inference pipeline

Before changing the model, confirm that the validation notebook reproduces the original implementation's:

- Input normalization.
- Sensor ordering.
- Residual calculations.
- Window alignment.
- Model checkpoint loading.

This is essential before attributing failures to model design.

### Priority 2 — Analyze false positives during Reynolds transitions

Add the following variables to the evaluation output:

```text
Reynolds
delta_Reynolds
abs_delta_Reynolds
actual_leak
predicted_leak_probability
predicted_leak
error_type
```

Then compare false-positive rates for stable versus changing Reynolds conditions.

### Priority 3 — Investigate the failed leak event at Reynolds = 25

Compare the residual spectra for:

- Reynolds = 100, where recall is 82.5%.
- Reynolds = 25, where recall is 16.8%.

Determine whether the poor detection originates from weak acoustic leak signatures, inaccurate Stage 1 baseline predictions, or Stage 2 interpretation.

### Priority 4 — Evaluate temporal stability

In addition to observation-level metrics, calculate:

- Event-level detection rate.
- Time to first detection.
- Longest continuous missed interval during each leak.
- False-alarm episodes per hour.
- Duration of false-positive episodes.

These are more informative for an operational leak detector than accuracy alone.

---

## 9. Final Assessment

The Reynolds-enhanced evaluation reveals a more specific weakness than the original probability graph.

**The model's detection reliability varies substantially across operating conditions.**

At Reynolds = 100 and 150, it detects most leaking observations.

At Reynolds = 25, it misses more than 83%.

False-positive rates also vary considerably across Reynolds ranges, with elevated rates in intermediate-flow conditions.

These findings suggest that the model may be sensitive to the operating regime and potentially to Reynolds transitions.

However, the current evidence does not establish whether the root cause lies in Stage 1 baseline prediction, Stage 2 classification, preprocessing, or the underlying acoustic signal.

### Overall Verdict

**The model demonstrates meaningful discrimination but insufficient reliability and temporal stability for operational leak detection.**

The immediate priority should be diagnosing Reynolds-dependent errors and verifying the inference pipeline, rather than increasing model complexity or simply adjusting the classification threshold.

Finally, `1212_1` was used as the original model's validation experiment. These results therefore do not constitute independent final-test performance.
