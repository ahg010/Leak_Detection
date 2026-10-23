
# Sensor Fidelity Analysis — Updated Results After Truncation

## 1. Objective and Dataset

Evaluate whether each sensor reproduces the source's temporal fluctuations at the **same timestamp and frequency**, regardless of differences in absolute amplitude.

- First 10 rows removed independently from each original CSV.
- 180 matched timestamps analyzed.
- 27 frequency bands.
- 3 sensors: Thing01, Thing02, Thing03.
- 81 sensor–frequency comparisons.
- No temporal lag correction is considered.

The main evaluation metrics are:

- **Pearson correlation:** Overall source–sensor co-movement.
- **First-difference correlation:** Agreement in consecutive increases and decreases.
- **Regression residual error:** Consistency of a linear relationship between source and sensor readings.

---

## 2. Overall Sensor Performance

| Metric | Thing01 | Thing02 | Thing03 |
|---|---:|---:|---:|
| Mean Pearson correlation | -0.0883 | -0.0902 | -0.1347 |
| Median Pearson correlation | -0.1178 | -0.1248 | -0.1556 |
| Mean first-difference correlation | -0.0026 | -0.0157 | -0.0486 |
| Median normalized residual RMSE | 0.9916 | 0.9916 | 0.9878 |
| Frequencies won (Pearson) | **14** | 11 | 2 |

### Interpretation

**Thing01 is now the relative winner**, with the highest mean Pearson correlation, the highest mean first-difference correlation, and 14 of 27 frequency wins.

Thing02 performs very similarly overall, while Thing03 ranks last on mean correlation.

However, all three sensors have negative mean Pearson correlations and first-difference correlations close to zero.

This indicates that none of the sensors reliably reproduces the source's temporal fluctuations across the full frequency range.

The normalized residual RMSE values are also close to 1, consistent with weak linear relationships.

---

## 3. Frequency-Level Analysis

### Best Frequencies by Pearson Correlation

For each frequency, select the sensor with the highest zero-lag Pearson correlation, then rank the frequencies.

| Rank | Frequency | Best Sensor | Pearson r | First-difference r |
|---:|---|---|---:|---:|
| 1 | f50 | Thing01 | 0.1485 | 0.1161 |
| 2 | f63 | Thing03 | 0.1475 | 0.0437 |
| 3 | f80 | Thing02 | 0.1394 | 0.0986 |
| 4 | f25 | Thing01 | 0.1375 | 0.1345 |
| 5 | f40 | Thing01 | 0.1281 | 0.0326 |
| 6 | f125 | Thing02 | 0.0532 | 0.1815 |
| 7 | f31_5 | Thing01 | 0.0319 | -0.0073 |
| 8 | f100 | Thing02 | 0.0054 | 0.0693 |

These are the only eight frequency bands where at least one sensor achieves a positive Pearson correlation.

Even the strongest result, **f50 with Thing01 (r = 0.1485)**, indicates very weak tracking.

### Best Frequencies for Second-to-Second Changes

Ranking by the strongest first-difference correlation at each frequency:

| Frequency | Best Sensor | First-difference r |
|---|---|---:|
| f125 | Thing02 | 0.1815 |
| f25 | Thing01 | 0.1345 |
| f160 | Thing02 | 0.1268 |
| f50 | Thing01 | 0.1161 |
| f250 | Thing01 | 0.1089 |
| f80 | Thing02 | 0.0986 |

The highest first-difference correlation is only 0.1815.

Therefore, even the best sensor–frequency combinations show weak agreement in second-to-second fluctuations.

---

## 4. Frequency-Dependent Behavior

### Low Frequencies: f25–f125

These exhibit the strongest relative source tracking.

Notable combinations:

- Thing01: f25, f40, f50.
- Thing02: f80, f125.
- Thing03: f63.

The most promising frequencies are concentrated in this range.

### Intermediate Frequencies: f160–f1000

Pearson correlations are negative for all three sensors.

Some first-difference correlations are positive, particularly at f160 and f250, but remain weak.

### High Frequencies: f1250–f10000

Pearson correlations are negative across all three sensors.

No high-frequency band demonstrates convincing source tracking.

Thing01 wins several high-frequency comparisons, but these are relative wins among negative correlations.

**Overall pattern:** Low frequencies preserve slightly more of the source's temporal behavior than intermediate and high frequencies.

---

## 5. Comparison With the Previous Analysis

| Metric | Previous: 190 rows | Updated: 180 rows |
|---|---:|---:|
| Thing01 mean Pearson r | -0.134 | -0.088 |
| Thing02 mean Pearson r | -0.135 | -0.090 |
| Thing03 mean Pearson r | -0.113 | -0.135 |
| Thing01 frequency wins | 9 | 14 |
| Thing02 frequency wins | 4 | 11 |
| Thing03 frequency wins | 14 | 2 |

### What Changed?

Removing the first 10 observations changed the relative ranking substantially.

- Thing01 improved from -0.134 to -0.088.
- Thing02 improved from -0.135 to -0.090.
- Thing03 deteriorated from -0.113 to -0.135.
- Thing01 replaced Thing03 as the relative winner.

This demonstrates that the sensor rankings are sensitive to the analyzed time window.

However, truncation did **not** produce strong positive source–sensor correlations.

The results are consistent with the possibility that the initial observations influence the correlation estimates, but they do not establish that those observations were the cause of poor fidelity.

---

## 6. Final Conclusions

### Finding 1 — Thing01 is the relative winner

Thing01 wins 14 of 27 frequencies and has the highest mean Pearson and first-difference correlations.

Thing02 is relatively close, winning 11 frequencies.

Thing03 now wins only 2 frequencies.

### Finding 2 — Low frequencies perform better

The strongest positive Pearson correlations occur between f25 and f125.

The most promising sensor–frequency combinations are:

- Thing01 at f50 and f25.
- Thing02 at f80 and f125.
- Thing03 at f63.

Nevertheless, their correlations remain weak.

### Finding 3 — Short-term tracking remains poor

Mean first-difference correlations remain close to zero or negative.

This indicates that sensors generally fail to reproduce the source's consecutive increases and decreases.

### Finding 4 — Truncation changes the ranking, not the overall conclusion

Removing the first 10 rows materially changes which sensor performs best.

However, no sensor demonstrates convincing source fidelity across the frequency range.

### Finding 5 — Sensor selection remains premature

Thing01 is the strongest relative candidate under the current evaluation, but the evidence does not establish acceptable tracking performance.

---

## 7. Recommended Next Analysis

Rather than introducing lag correction or additional sensor rankings, examine whether source–sensor relationships remain consistent over different portions of the recording.

For each sensor and frequency:

1. Calculate Pearson correlation separately for the first and second halves of the truncated recording.
2. Calculate first-difference correlation for each half.
3. Compare whether the same sensor–frequency combinations remain relatively strong.
4. Examine the best low-frequency combinations using standardized time-series plots.

This will help determine whether the weak correlations reflect consistently poor tracking or whether fidelity changes over the recording period.

## Bottom Line

**After removing the first 10 rows, Thing01 becomes the best relative sensor, winning 14 of 27 frequency comparisons.**

The strongest frequency matches occur at low frequencies, particularly f25–f125.

However, Pearson correlations remain weak and first-difference correlations are approximately zero.

**The current evidence does not establish reliable temporal source tracking by any of the three sensors.**
