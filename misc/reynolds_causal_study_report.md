# Reynolds Effects on Stage 1 Healthy-Spectrum Reconstruction
## Results interpretation and causal-identification assessment

**Study:** `reynolds_causal_study_results.ipynb`  
**Results:** `reynolds_causal_results.tar`  
**Data:** healthy-only endpoints of validation experiment `1212_1`  
**Scope:** observational diagnostics of a previously trained Stage 1 model; **no retraining and no causal effect identified**.

## Executive summary

**Principal finding:** Healthy Stage 1 reconstruction error is substantially associated with **Reynolds operating level**, and several signed sensor–frequency residuals retain strong Reynolds-dependent structure. In contrast, instantaneous per-second Reynolds differences are almost unrelated to instantaneous *changes* in aggregate RMSE.

This does **not** establish that Reynolds level causes reconstruction error, nor that Stage 1 residuals cause Stage 2 false positives. The experiment is a single temporally ordered trajectory, Reynolds and time are correlated, and important operating conditions are not observed. Moreover, the current event-study procedure selected seven small steps *inside ramps*, rather than complete physical flow transitions.

**Engineering implication:** Prioritize whether healthy residual patterns depend on Reynolds **regime and history**, not simply whether large `|ΔRe|` coincides with an immediate RMSE jump. Then test whether those specific residual patterns align with Stage 2 false alarms.

## 1. Data integrity and observational unit

- **7,567** fully healthy Stage 1 endpoints, Reynolds range **0–150**.
- Nominal observation interval: **1 second**.
- **7,561** genuinely adjacent healthy pairs for first differences; **five** cross-gap pairs excluded.
- No missing core Reynolds/RMSE/timestamp fields or duplicate observation indices.
- Stage 1 predicts the healthy 27-frequency spectrum at each of four probes. Its residual is **actual − predicted**.
- `endpoint_RMSE` is a single scalar over **108 probe-frequency amplitudes** at a given endpoint, not an average over the input's 40 time steps.
- The 40-step input length is an inference requirement, **not a restriction on subsequent temporal diagnostics**.

**Statistical caveat:** The 7,567 endpoints are serially dependent observations from **one validation experiment**, not 7,567 independent interventions.

## 2. Descriptive association results

| Predictor | Outcome | n | Pearson | Spearman | Interpretation |
|---|---|---:|---:|---:|---|
| Reynolds | endpoint RMSE | 7,567 | +0.4935 | +0.6276 | Higher Re tends to accompany higher error; nonlinear/clustered |
| Absolute ΔRe | endpoint RMSE | 7,561 | +0.4612 | +0.3745 | Ramp intensity associated with error **level** |
| Signed ΔRe | ΔRMSE | 7,561 | −0.0021 | −0.0035 | No evident instantaneous linear signed response |
| Absolute ΔRe | ΔRMSE | 7,561 | +0.0012 | −0.0012 | No evident instantaneous error increase |
| Absolute ΔRe | Absolute ΔRMSE | 7,561 | +0.0412 | +0.0302 | Very weak instantaneous error-volatility association |
| Reynolds | Relative RMSE | 7,567 | +0.2590 | +0.2622 | Level association persists, more weakly, after normalization |

### Interpretation of the six scatterplots

The **Re vs RMSE** panel shows an upward tendency, regime clusters, nonlinearity, and occasional large errors. The **|ΔRe| vs RMSE** panel suggests observations during ramps can have higher error, but this is not an instantaneous response estimate. Both **ΔRMSE** panels show near-zero centered change regardless of per-second ΔRe. **|ΔRMSE|** shows only a very weak association. **Relative RMSE** also tends to rise with Reynolds.

**Crucial distinction:** The observed per-second `|ΔRe|` is only about **0–0.17** in Reynolds units, whereas the level spans **0–150**. A long gradual ramp can substantially alter the operating regime without generating a large one-step difference. Near-zero first-difference correlation therefore **cannot rule out cumulative, delayed, or nonlinear effects**.

These are associations, not causal estimates.

## 3. Time as a potential confounder

The notebook reports **corr(Re, time) = −0.567**. Reynolds bands are not evenly represented over time:

| Reynolds band | Q1 | Q2 | Q3 | Q4 |
|---|---:|---:|---:|---:|
| <10 | 0 | 0 | 0 | 1,140 |
| 10–25 | 561 | 0 | 0 | 883 |
| 25–50 | 600 | 0 | 861 | 0 |
| 50–75 | 300 | 169 | 580 | 0 |
| 75–100 | 300 | 112 | 0 | 0 |
| 100–125 | 300 | 749 | 0 | 0 |
| ≥125 | 630 | 382 | 0 | 0 |

Six of seven bands occur in two or more quartiles, but **extreme bands have poor overlap**. Consequently, high-Re vs low-Re comparisons also compare different experimental periods. Drift, pump operating state, temperature, pressure, sensor changes, or other unmeasured conditions could contribute. These are **candidate confounders**, not confirmed available columns.

Time-polynomial adjustment can reduce some temporal trends but **cannot guarantee exchangeability** or remove unmeasured confounding.

## 4. HAC-adjusted level regressions

| Model | n | R² | Selected findings |
|---|---:|---:|---|
| Naive level (Re and Re²) | 7,567 | 0.2437 | Re/100 coef **+0.6674**, p=0.00060; quadratic p=0.746 |
| Level + cubic time | 7,567 | 0.2711 | Re/100 coef **+3.1619**, Re² coef **−1.1161**; both statistically significant |
| Level + |ΔRe| + cubic time | 7,561 | 0.3659 | Re coef **+0.7983**, p=0.256; Re² coef **−0.0196**, p=0.950; |ΔRe|/100 coef **+462.84**, p<0.001 |

The Reynolds coefficients change greatly across specifications. In the third model, the level terms lose significance once transition magnitude is included. This **does not prove** that level has no effect: Reynolds level, ramp status, and time are entangled.

**Scaling:** `abs_d_Re_100 = |ΔRe|/100`. A regression coefficient of 462.84 per 100-unit change in ΔRe corresponds to approximately **0.463 RMSE units for a 0.1-unit per-second ΔRe**, holding model covariates fixed. Do not interpret 462.84 as the expected error change from an actual observed one-second transition.

HAC standard errors allow approximate serial-correlation-robust inference conditional on the fitted model. They **do not remove omitted-variable bias, cure limited overlap, or make a single run into multiple independent experiments**. R² values are in-sample.

## 5. First-difference regressions

| Model | ΔRe term coefficient | HAC p-value | Finding |
|---|---:|---:|---|
| Signed ΔRe → signed ΔRMSE | −1.8871 per 100-unit ΔRe | 0.300 | Not significant |
| |ΔRe| → signed ΔRMSE | +1.3118 per 100-unit ΔRe | 0.614 | Not significant |
| Combined signed ΔRe | −1.7316 | 0.332 | Not significant |
| Combined |ΔRe| | +0.5334 | 0.839 | Not significant |

There is **no convincing contemporaneous linear effect** of per-second Reynolds changes on per-second aggregate RMSE changes in these models. This does not rule out effects over longer horizons, nonlinear responses, accumulated ramp exposure, or signed channel-level effects.

First differencing removes fixed offsets but not time-varying confounders.

## 6. Transition event study — important validity warning

- Threshold: **95th percentile of nonzero adjacent |ΔRe| ≈ 0.16667**.
- **185** candidate time points; **seven** events after spacing/validity filtering.
- All seven selected changes are approximately **−0.16667 Reynolds units in one second** at Re levels about **138.5, 126.8, 107.8, 88.5, 78.2, 67.7, 53.3**.
- Reported pre-event placebo mean relative to reference: **+0.1616**.
- Reported post-event mean: **+0.2264**.
- Post minus pre summary: **+0.0647 RMSE units**.

**Do not treat +0.0647 as a causal transition effect.** These seven points are small steps *within descending ramps*, not complete transitions between stable flow regimes. Their spacing does not establish independence, the pre-event placebo is nonzero, and no counterfactual series is provided. The selection rule answers a different question than the intended physical transition analysis.

**Required correction for a future study:** Identify sustained ramp **onsets, ends, directions, total Re change, ramp duration, and subsequent plateaus**. Compare residuals before and after full ramps at comparable starting regimes, and examine placebo leads and sufficient post-ramp recovery. If no valid controls or replicated ramps exist, label the result descriptive.

## 7. Signed channel residuals: the most actionable result

The aggregate RMSE hides systematic bias and direction across **108 channels**.

| Channel | Mean signed residual | Channel RMSE | corr(Re, signed residual) |
|---|---:|---:|---:|
| DS/f250 | −8.919 | 9.299 | +0.006 |
| US/f80 | +5.824 | 6.718 | +0.364 |
| US/f50 | +2.406 | 5.227 | +0.729 |
| US/f31.5 | +3.765 | 5.142 | +0.387 |
| US/f40 | +2.260 | 4.469 | +0.512 |
| US/f63 | +2.693 | 4.138 | +0.625 |
| US/f100 | +2.701 | 4.018 | +0.578 |
| DS/f160 | −2.504 | 3.650 | −0.367 |

Negative signed residual means **overprediction**; positive means **underprediction**. DS/f250 has a large negative offset; several US frequencies show both positive bias and substantial dependence on Reynolds level.

The channel-level correlations between **same-step ΔRe and Δsigned residual** are near zero in the displayed results. These do not negate the level-dependent signed biases or rule out lagged and accumulated changes.

**Interpretation:** Stage 1 has not completely removed Reynolds-associated structure from healthy spectral residuals. This is a promising **diagnostic target**, not proof of a causal effect or proof that these channels generate Stage 2 false alarms. Check sensor ordering, preprocessing, checkpoint compatibility, and train/validation distribution shift before attributing biases to the architecture.

## 8. Relation to Stage 2 false positives

Previous Stage 2 diagnostics for the validation run reported **4.23% false-positive rate in stable Reynolds conditions** versus **8.05% during changing Reynolds conditions**. Those historical groups used a different selection than this healthy-only study, so do not combine their denominators or infer a mediation effect.

The present notebook **does not join Stage 2 false-positive timestamps to the channel residuals**. Therefore, the proposed chain

`Reynolds regime/change → Stage 1 signed residual pattern → Stage 2 false alarm`

remains a **hypothesis**. Even perfect Stage 1 baseline reconstruction would not automatically guarantee that Stage 2's decision boundary is specific to leaks.

## 9. What can and cannot be claimed

### Supported by these outputs

1. Higher Reynolds levels accompany higher healthy Stage 1 endpoint RMSE.
2. The level association weakens, changes shape, or loses significance under alternative time/transition specifications.
3. There is little evidence of an *instantaneous linear* ΔRe → ΔRMSE relationship.
4. Several signed sensor–frequency residuals have large biases and Reynolds-dependent patterns.
5. The current transition-event analysis is insufficient for causal identification.

### Not established

- That changing Reynolds **causes** increased RMSE.
- That the isolated physical effect of Reynolds can be separated from pump/operating-regime changes.
- That signed residual patterns **cause** Stage 2 false positives.
- That Stage 1 redesign or retraining would reduce false positives without harming leak recall.
- That results generalize to independent experiments or unseen sensor geometries.

## 10. Recommended next analyses, in order

1. **Fix the transition definition.** Segment the original Reynolds trajectory into stable plateaus and sustained ramps, not the top 5% of nonzero one-second increments. Audit original units and event times.
2. **Study regime and lag dependence.** Estimate signed residual and RMSE behavior across stable Reynolds levels, cumulative ramp change, time since ramp onset/end, and recovery after reaching a plateau. Avoid treating overlapping samples as independent replications.
3. **Check causal identification.** Evaluate pre-trends, time overlap, repeated levels/ramp directions, and measured operating covariates. Where identification is not credible, report adjusted associations rather than causal effects.
4. **Connect to Stage 2.** Join residual trajectories with healthy false-positive timestamps. Compare FP and TN at similar Reynolds levels, ramp phases, and time periods; inspect channel patterns and alarm continuity.
5. **Test corrective interventions only after diagnosis.** Compare targeted baseline corrections or simpler models using run-level validation and preserved leak recall. Do not tune and claim an unbiased final test on the same validation run.

## Final conclusion

The study provides useful evidence of **Reynolds-regime-dependent healthy baseline errors**, especially in specific signed acoustic channels. It does **not** demonstrate that instantaneous Reynolds changes cause aggregate RMSE changes, and the present event-study design does not identify a causal effect. The scientifically defensible next step is a **ramp/plateau-aware, channel-specific analysis**, followed by direct alignment with Stage 2 false alarms.

The intended system-level objective remains valid: Stage 1 should explain normal acoustic variation well enough that Stage 2 predominantly detects leak-specific departures. The present evidence identifies where to investigate that objective, but does not yet show that it has been achieved.
