# Current LSTM Leak-Detection Flow and Proposed CUSUM Replacement

## 1. Current Approach

Based on `LSTM_Dev_Report_April2026.pdf` and `GTvate_leak_detect(1).ipynb`, the current approach can be summarized as:

```text
Reynolds-number history
+
Probe coordinates
        │
        ▼
Baseline LSTM
        │
        ▼
27 predicted healthy frequency amplitudes
        │
        ▼
Measured 27 frequency amplitudes
        −
Predicted 27 frequency amplitudes
        │
        ▼
27 residuals per probe
        │
        ▼
Second LSTM
        │
        ▼
Additional frequency/probe processing
        │
        ▼
Leak probability
+
Leak magnitude
```

---

## 2. Baseline LSTM

The purpose of the first LSTM is to learn the expected acoustic spectrum under **healthy operating conditions**.

Its conceptual input is:

```text
Reynolds-number history
+
Probe coordinates
```

For example:

```text
Re(t-W+1)
Re(t-W+2)
...
Re(t)
+
Probe coordinates
```

The model predicts:

```text
27 healthy frequency amplitudes
```

The mapping is:

$$
\left(
Re_{t-W+1:t},
P_p
\right)
\rightarrow
\left[
\hat{x}_{p,1,t},
\hat{x}_{p,2,t},
\ldots,
\hat{x}_{p,27,t}
\right]
$$

where:

- $Re_{t-W+1:t}$ = Reynolds-number history
- $P_p$ = probe coordinates
- $\hat{x}_{p,f,t}$ = predicted healthy amplitude at frequency $f$

The notebook confirms that the output dimension is 27:

```python
self.re_to_spec = nn.Linear(hidden_dim, Freq)
```

with:

```python
Freq = 27
```

---

## 3. Residual Calculation

After predicting the healthy spectrum, the predicted spectrum is compared with the measured acoustic spectrum.

The notebook performs:

```python
baseline = baseline_model(Xw, Rew, coords_b)["baseline"]

residual = Xw - baseline
```

Therefore:

$$
r_{p,f,t}
=
x_{p,f,t}
-
\hat{x}_{p,f,t}
$$

where:

- $x_{p,f,t}$ = measured amplitude
- $\hat{x}_{p,f,t}$ = predicted healthy amplitude
- $r_{p,f,t}$ = residual

For each probe and each time step, this produces:

$$
\mathbf{r}_{p,t}
=
\left[
r_{p,1,t},
r_{p,2,t},
\ldots,
r_{p,27,t}
\right]
$$

In simple terms:

```text
Measured spectrum
27 amplitudes

        −

Predicted healthy spectrum
27 amplitudes

        │
        ▼

Residual spectrum
27 residuals
```

---

## 4. Second LSTM

The residual vector is then passed to the second LSTM.

The notebook calls:

```python
out = residual_model(residual, coords_b)
```

Inside the residual model:

```python
self.lstm = nn.LSTM(
    input_size=Freq,
    hidden_size=hidden_dim,
    ...
)
```

Since:

```python
Freq = 27
```

the second LSTM receives the 27-dimensional residual vector at each time step:

$$
\mathbf{r}_{p,t}
=
\left[
r_{p,1,t},
r_{p,2,t},
\ldots,
r_{p,27,t}
\right]
$$

The second LSTM therefore learns **temporal patterns in the residual acoustic spectrum**.

---

## 5. Current Architecture in Simple Terms

The current approach can be viewed as three stages.

### Stage 1 — Predict Normal Acoustic Behavior

```text
Reynolds history
+
Probe position
        │
        ▼
Baseline LSTM
        │
        ▼
27 expected healthy amplitudes
```

### Stage 2 — Calculate What the Baseline Cannot Explain

```text
27 measured amplitudes
        −
27 expected amplitudes
        │
        ▼
27 residuals
```

For each frequency:

$$
r_{p,f,t}
=
x_{p,f,t}
-
\hat{x}_{p,f,t}
$$

Conceptually:

$$
\text{Residual}
=
\text{Measured Amplitude}
-
\text{Predicted Healthy Amplitude}
$$

### Stage 3 — Determine Whether the Residual Pattern Represents a Leak

```text
Sequence of 27-dimensional residual vectors
                │
                ▼
           Second LSTM
                │
                ▼
    Frequency/probe processing
                │
                ▼
       Leak classification
```

The fundamental idea is:

```text
Predict normal behavior
        │
        ▼
Subtract normal from measured
        │
        ▼
Analyze the unexplained component
```

---

## 6. Where the Proposed CUSUM Approach Changes the Architecture

The initial CUSUM proposal does **not** require changing the baseline LSTM.

We retain:

```text
Reynolds history
+
Probe coordinates
        │
        ▼
Baseline LSTM
        │
        ▼
27 predicted healthy amplitudes
        │
        ▼
Measured − Predicted
        │
        ▼
27 residuals
```

The proposed change begins **after the 27 residuals have been generated**.

---

## 7. Current vs. Proposed Architecture

### Current Architecture

```text
27 residuals
     │
     ▼
Second LSTM
     │
     ▼
Frequency processing
     │
     ▼
Probe relationship processing
     │
     ▼
Learned probe weighting
     │
     ▼
Global representation
     │
     ▼
Leak classifier
```

### Proposed CUSUM Architecture

```text
27 residuals
     │
     ▼
Standardize residuals
     │
     ▼
Combine 27 residuals
     │
     ▼
One anomaly score per probe
     │
     ▼
CUSUM
     │
     ▼
Segment aggregation
     │
     ▼
Threshold + persistence rule
     │
     ▼
Leak alarm
+
Approximate leak location
```

---

## 8. Standardizing the 27 Residuals

The 27 frequencies can have different natural scales and different levels of variability.

Each residual is therefore standardized using statistics calculated from healthy residuals:

$$
z_{p,f,t}
=
\frac{
r_{p,f,t}
-
\mu_{p,f}
}{
\sigma_{p,f}
}
$$

where:

- $r_{p,f,t}$ = residual
- $\mu_{p,f}$ = mean healthy residual
- $\sigma_{p,f}$ = standard deviation of healthy residuals
- $z_{p,f,t}$ = standardized residual

For every probe and time point we now have:

$$
\mathbf{z}_{p,t}
=
\left[
z_{p,1,t},
z_{p,2,t},
\ldots,
z_{p,27,t}
\right]
$$

---

## 9. Combining the 27 Residuals

The 27 standardized residuals can be combined into one anomaly score for each probe.

A simple approach is standardized RMS:

$$
A_{p,t}
=
\sqrt{
\frac{1}{27}
\sum_{f=1}^{27}
z_{p,f,t}^{2}
}
$$

This transforms:

```text
27 standardized residuals
        │
        ▼
RMS aggregation
        │
        ▼
1 anomaly score
per probe
per time step
```

An advantage of using squared standardized residuals is that positive and negative residuals do not cancel each other.

---

## 10. CUSUM

CUSUM accumulates evidence of persistent abnormal behavior.

For probe $p$:

$$
C_{p,t}
=
\max
\left(
0,
C_{p,t-1}
+
A_{p,t}
-
k
\right)
$$

where:

- $C_{p,t}$ = current CUSUM value
- $C_{p,t-1}$ = previous CUSUM value
- $A_{p,t}$ = current anomaly score
- $k$ = reference value controlling sensitivity

A probe-level alarm occurs when:

$$
C_{p,t}
>
h
$$

where $h$ is the alarm threshold.

The second LSTM's task:

```text
Learn temporal patterns
in the residual sequence
```

is therefore replaced by:

```text
Accumulate statistical evidence
of persistent abnormal residual behavior
```

---

## 11. Exact Replacement Boundary

```text
                  COMMON PART

Reynolds history + probe coordinates
                    │
                    ▼
              Baseline LSTM
                    │
                    ▼
        27 predicted healthy amplitudes
                    │
                    ▼
Measured amplitudes − predicted amplitudes
                    │
                    ▼
              27 residuals
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
   CURRENT APPROACH     PROPOSED APPROACH
          │                   │
    Second LSTM          Standardization
          │                   │
          ▼                   ▼
Frequency processing     RMS anomaly score
          │                   │
          ▼                   ▼
Probe relationship           CUSUM
    processing                │
          │                   ▼
          ▼             Segment aggregation
Learned weighting             │
          │                   ▼
          ▼             Threshold +
Global classifier       persistence rule
          │                   │
          ▼                   ▼
Leak probability         Leak detection
+ magnitude              + localization
```

---

## 12. Simple Numerical Example

For illustration, suppose there are only three frequencies.

The predicted healthy spectrum is:

```text
Frequency 1 = 10
Frequency 2 = 20
Frequency 3 = 30
```

The measured spectrum is:

```text
Frequency 1 = 11
Frequency 2 = 24
Frequency 3 = 28
```

The residuals are:

$$
r_1
=
11-10
=
1
$$

$$
r_2
=
24-20
=
4
$$

$$
r_3
=
28-30
=
-2
$$

Therefore:

$$
\mathbf{r}
=
\left[
1,
4,
-2
\right]
$$

In the actual system, this vector contains 27 residuals.

After standardization we obtain:

$$
\mathbf{z}_{p,t}
=
\left[
z_{p,1,t},
z_{p,2,t},
\ldots,
z_{p,27,t}
\right]
$$

The anomaly score is then:

$$
A_{p,t}
=
\sqrt{
\frac{1}{27}
\sum_{f=1}^{27}
z_{p,f,t}^{2}
}
$$

Suppose:

$$
A_{p,t}
=
1.4
$$

This enters CUSUM:

$$
C_{p,t}
=
\max
\left(
0,
C_{p,t-1}
+
1.4
-
k
\right)
$$

If abnormal residual behavior persists, $C_{p,t}$ continues to increase.

An alarm occurs when:

$$
C_{p,t}
>
h
$$

---

## 13. Segment-Level Localization

Suppose the physical probe arrangement is:

```text
A1 -------- B1 -------- A2 -------- B2
     S1          S2          S3
```

Suppose the probe CUSUM values are:

```text
A1 = 0.7
B1 = 6.4
A2 = 7.0
B2 = 1.2
```

A simple segment score can be calculated from the two probes surrounding each segment.

For Segment S1:

$$
G_{S1,t}
=
\frac{
C_{A1,t}
+
C_{B1,t}
}{2}
$$

Therefore:

$$
G_{S1,t}
=
\frac{
0.7+6.4
}{2}
=
3.55
$$

For Segment S2:

$$
G_{S2,t}
=
\frac{
C_{B1,t}
+
C_{A2,t}
}{2}
$$

Therefore:

$$
G_{S2,t}
=
\frac{
6.4+7.0
}{2}
=
6.70
$$

For Segment S3:

$$
G_{S3,t}
=
\frac{
C_{A2,t}
+
C_{B2,t}
}{2}
$$

Therefore:

$$
G_{S3,t}
=
\frac{
7.0+1.2
}{2}
=
4.10
$$

If:

$$
h_{\text{segment}}
=
5
$$

then:

```text
S1 = 3.55    Healthy
S2 = 6.70    Abnormal
S3 = 4.10    Healthy
```

The approximate leak location is therefore:

```text
Segment S2
between probes B1 and A2
```

This should be interpreted as **approximate localization**, not exact physical leak localization.

---

## 14. Does the First LSTM Also Need to Be Replaced?

This is a **separate research question**.

Replacing the second LSTM with CUSUM does not require replacing the baseline LSTM.

There are therefore two independent questions.

### Question 1 — Leak Detector

```text
Should the residual LSTM
be replaced with CUSUM?
```

This can be tested while keeping the baseline LSTM exactly the same:

```text
              Same baseline LSTM
                     │
                     ▼
               Same residuals
                     │
             ┌───────┴───────┐
             ▼               ▼
      Residual LSTM         CUSUM
             │               │
             ▼               ▼
      Leak detection    Leak detection
```

This isolates the effect of replacing the second LSTM.

---

## 15. Separate Benchmark of the Baseline LSTM

The first LSTM can then be evaluated separately.

The question is:

> Does Reynolds-number history provide enough additional information to justify using an LSTM?

Models that use only the current Reynolds number can provide a useful benchmark:

```text
Current Reynolds number
+
Probe position
        │
        ├── Linear Regression
        ├── Random Forest
        ├── XGBoost
        └── MLP
                │
                ▼
       27 predicted amplitudes
```

Their mapping is:

$$
\left(
Re_t,
P_p
\right)
\rightarrow
\left[
\hat{x}_{p,1,t},
\hat{x}_{p,2,t},
\ldots,
\hat{x}_{p,27,t}
\right]
$$

The LSTM instead uses Reynolds-number history:

$$
\left(
Re_{t-W+1:t},
P_p
\right)
\rightarrow
\left[
\hat{x}_{p,1,t},
\hat{x}_{p,2,t},
\ldots,
\hat{x}_{p,27,t}
\right]
$$

The comparison therefore asks:

```text
Does Reynolds history materially improve
prediction of the healthy acoustic spectrum?
```

---

## 16. Stronger Baseline Benchmark

A stronger experiment should also provide Reynolds-history features to a non-LSTM model.

For example:

```text
Re(t)
Re(t-1)
Re(t-2)
...
Re(t-W+1)
+
Probe position
        │
        ▼
XGBoost / MLP
        │
        ▼
27 predicted amplitudes
```

This gives three useful comparisons.

### Model A

```text
Current Reynolds
+
Probe position
        │
        ▼
XGBoost
        │
        ▼
27 amplitudes
```

### Model B

```text
Reynolds lag features
+
Probe position
        │
        ▼
XGBoost
        │
        ▼
27 amplitudes
```

### Model C

```text
Reynolds sequence
+
Probe position
        │
        ▼
LSTM
        │
        ▼
27 amplitudes
```

Then:

```text
Model A vs. Model B
        │
        ▼
Does Reynolds history help?
```

and:

```text
Model B vs. Model C
        │
        ▼
If history helps, does sequence modeling
with an LSTM provide additional value?
```

---

## 17. Recommended Experimental Sequence

### Experiment 1 — Replace Only the Leak Detector

Keep:

```text
Baseline LSTM
        │
        ▼
27 predicted amplitudes
        │
        ▼
27 residuals
```

Then compare:

```text
              27 residuals
                   │
           ┌───────┴───────┐
           ▼               ▼
    Residual LSTM         CUSUM
           │               │
           ▼               ▼
    Leak detection    Leak detection
```

This directly tests whether CUSUM can replace the second LSTM.

### Experiment 2 — Evaluate the Baseline Model

Then separately compare:

```text
Current Reynolds + position
→ Linear Regression

Current Reynolds + position
→ Random Forest

Current Reynolds + position
→ XGBoost

Current Reynolds + position
→ MLP

Reynolds history + position
→ XGBoost / MLP

Reynolds sequence + position
→ LSTM
```

All models predict the same target:

```text
27 healthy frequency amplitudes
```

---

## 18. Main Takeaway

The current implementation is approximately:

```text
Reynolds history
+
Probe position
        │
        ▼
Baseline LSTM
        │
        ▼
Predict 27 healthy amplitudes
        │
        ▼
Measured − Predicted
        │
        ▼
27 residuals
        │
        ▼
Second LSTM
        │
        ▼
Learn temporal residual patterns
        │
        ▼
Leak prediction
```

The proposed architecture is:

```text
Reynolds history
+
Probe position
        │
        ▼
Baseline LSTM
        │
        ▼
Predict 27 healthy amplitudes
        │
        ▼
Measured − Predicted
        │
        ▼
27 residuals
        │
        ▼
Standardize residuals
        │
        ▼
Combine into anomaly score
        │
        ▼
CUSUM
        │
        ▼
Accumulate persistent evidence
        │
        ▼
Segment aggregation
        │
        ▼
Leak detection
+
Approximate localization
```

The **first proposed experiment is therefore very specific**:

> Keep the existing baseline LSTM and residual calculation unchanged. Replace the second residual LSTM and downstream learned leak-detection components with standardized residual aggregation, CUSUM, and explicit segment-level decision logic.

Only after this comparison should the baseline LSTM itself be independently benchmarked against simpler healthy-spectrum prediction models.