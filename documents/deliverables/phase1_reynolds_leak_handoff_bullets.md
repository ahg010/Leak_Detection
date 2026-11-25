# Phase 1 Reynolds and acoustic leak detection handoff — bullet summary

- Prepared for Maziar and the GTvate project team.
- The selected Phase 2 candidate is the compact GRU e24/h16 that estimates current Reynolds number from acoustic spectra. It achieved the lowest reported validation MAE with 2,705 parameters. The next experiment should test whether predicted Reynolds can replace measured Reynolds in the leak detector without increasing false alarms or masking leaks during flow changes.

## Reynolds prediction benchmark

- The compact search notebook uses four probes, 40-step acoustic windows, run `1211_1` for training, and run `1212_1` for validation. The grid contains 16 embedding and hidden-width combinations from 16, 24, 32 and 48. These are validation comparisons on a small number of independent runs. The saved benchmark reports errors on the notebook's Reynolds scale, on which a value of 150 corresponds to the 150,000 operating point used in the test workbook.
- **LSTM 64/64.** MAE 8.178, RMSE 12.176, R² 0.9395, 35,137 parameters.
- **Full GRU 64/64.** MAE 8.540, RMSE 12.597, R² 0.9353, 26,817 parameters.
- **TCN.** MAE 9.911, RMSE 12.723, R² 0.9340.
- **Temporal-statistics MLP.** MAE 13.69, RMSE 16.81, R² 0.885.
- **Current-spectrum MLP.** MAE 15.70, RMSE 19.41, R² 0.846.
- **Extra Trees.** MAE 16.337, RMSE 21.345, R² 0.8142.
- **Random Forest.** MAE 21.030, RMSE 25.550, R² 0.7337.
- **XGBoost.** MAE 28.091, RMSE 33.087, R² 0.5534.
- **Ridge.** MAE 45.010, RMSE 56.557, R² −0.3048.
- **Compact GRU e16/h24.** MAE 7.846, RMSE 11.914, R² 0.9421, 3,497 parameters.
- **Compact GRU e24/h16 selected.** MAE 7.777, RMSE 12.000, R² 0.9413, 2,705 parameters.
- The e24/h16 model used 92% fewer parameters than the LSTM, reduced validation MAE by 4.9%, and reduced RMSE by 1.4%. Reported training time was 90.5 seconds versus 343.3 seconds for the LSTM. Against Extra Trees, the strongest classical model, MAE fell by 52%. Training time is a separate metric from inference latency.
- The e16/h24 variant achieved the smallest RMSE, by 0.086, while e24/h16 gave lower MAE and used 23% fewer parameters than e16/h24. The selected checkpoint is `models/compact_gru_e24_h16_1211_1_to_1212_1.pt`. The branch also contains the e16/h24 checkpoint. The compact search notebook's example save cell selects by RMSE, so freeze the explicitly selected e24/h16 checkpoint for Phase 2.

## Data exploration and findings

- **Historical test log.** Original tests varied leak size and Reynolds. The log records a correction to upstream and downstream sensor labels. Verify physical probe IDs, positions and distances before comparing signs or spatial contrasts.
- **Healthy cross-run spectra.** The notebook loaded 59,400 rows and found 6,000 matched operating-point groups with multiple experiments. In its matched subset, replication was available for DS and UUS, while US and DDS had only one experiment each. Healthy amplitudes varied between runs even at matched flow. DS at 250 Hz is one documented high-spread example. Confirm frequency mapping because this EDA used 26 channels while the baseline uses 27.
- **Healthy endpoints in run 1212_1.** Across 7,567 healthy endpoints, Reynolds and baseline RMSE correlated at 0.4935. Same-second Reynolds increments were weak predictors of same-second RMSE changes in the fitted analysis. The descending ramps followed gaps that included leak periods, so the data cannot isolate Reynolds level, rate, direction and previous leak effects.
- **Matched 100k to 150k transitions and first leaks at 150k.** The archived comparison separates stable level shifts, ramp overshoot, leak onset and later excursions. Their magnitudes depend on probe and frequency. Score each event phase separately and use matching healthy transitions to test whether candidate leak features also respond to changes in flow.
- **Existing two-stage detector.** With measured Reynolds and a 0.5 threshold, validation run 1212_1 gave 78.5% precision, 58.0% recall, 66.7% F1 and 0.765 average precision. There were 476 false-positive and 1,260 false-negative windows. The run was used for validation, so those figures do not establish independent test performance. Adjacent 40-step windows share 39 observations.

## Phase 2 work and acceptance

- **Pilot the rig and logging.** Synchronize valve and pump commands, acoustic channels, measured flow, pressure and temperature. Record actual event times and measured velocity, Reynolds and rates of change. Verify channel mapping, signs, timestamp alignment and usable sample counts.
- **Separate each effect.** Hold flow steady while varying leak size. Run matched no-leak ramps up and down at two measured rates. Then introduce the same leak before, during and after a matched ramp. Counterbalance order across independent sessions and collect no-leak controls with matched elapsed time.
- **Measure settlement.** Start the pilot with 10-minute holds. Set stability thresholds for the hydraulic signals and selected acoustic bands, a safe maximum hold, and a minimum five-minute settled analysis window. Record onset, through-ramp, settled leak and recovery as distinct phases. Flag events that fail to settle and keep them visible in transient analysis.
- **Validate Reynolds independently.** Freeze the checkpoint, window alignment and preprocessing. Compare the compact GRU with persistence and the LSTM against synchronized measured Reynolds. Report error, bias and delay by regime, ramp direction and rate, and leak state. Record inference latency and missing-probe performance separately.
- **Validate the leak pipeline end to end.** Replay the same streams with measured Reynolds and then GRU-estimated Reynolds feeding the healthy baseline. Keep detector weights and threshold fixed for the paired comparison. Report event recall, false alarms per healthy hour, onset and clearance delays, and separate scores near flow transitions. Agree acceptance limits before opening the held-out sessions.
- **Close out the experiment.** Commit split manifests, run metadata, model identifiers, stable result tables and reproducible commands. Report uncertainty at the independent session or event level. Preserve the raw data according to the project's access and retention rules.
- The accompanying Phase 2 workbook contains 34 conditions and an event log. Numeric ramp rates and settle tolerances are pilot inputs.

## Sources

- `spectral_to_reynolds_lstm_benchmark_fixed _results.ipynb` and `spectral_to_reynolds_compact_gru_search_FIXED.ipynb`
- `Data_log.xlsx` and `healthy_frequency_cross_experiment_eda_results.ipynb`
- `reynolds_full_causal_assessment_report.md` and `reynolds_100_to_150_vs_first_leak_150_findings_report`
- `leak_detection_handoff_updated_2026-10-26.md`
- Repository files [Reynolds model selection report](../Reinalds_predictions.md) and [executive benchmark summary](../Reinalds_predictions_summary.md)
