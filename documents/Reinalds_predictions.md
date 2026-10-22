# Model Selection Report: Acoustic Spectrum → Reynolds Number Prediction

## 1. Objective

The objective of this experiment was to determine whether the Reynolds number can be predicted from the measured acoustic spectrum and, if so, identify the simplest model that provides strong cross-experiment predictive performance.

The prediction problem is:

$$
X_{t-39:t} \rightarrow \hat{Re}_t
$$

where:

- $X$ contains the acoustic measurements from **4 probes**,
- each probe contains **27 frequency amplitudes**,
- a temporal window of **40 measurements** is available,
- the target is the Reynolds number at the current time $t$.

The evaluation was deliberately performed across experiments:

- **Training:** `1211_1`
- **Validation:** `1212_1`

Therefore, the models are not simply interpolating randomly held-out observations from the same experiment. They must learn a relationship from one experimental run and apply it to another.

---

# 2. Models Evaluated

The model-selection process was performed progressively, starting with classical machine-learning models and then evaluating models capable of explicitly representing temporal structure.

The evaluated models included:

### Classical models

- Ridge Regression
- Random Forest
- Extra Trees
- XGBoost

For these models, the complete 40-step history was available, but the temporal window was flattened into a conventional feature vector.

The input therefore contained:

$$
40 \times 4 \times 27 = 4320
$$

features.

### Temporal neural-network models

The following sequence models were evaluated:

- LSTM
- TCN
- GRU

Unlike the classical models, these architectures preserve the temporal organization of the 40-step acoustic history.

### Simplified models

Additional experiments were performed to determine whether the temporal architecture could be eliminated or substantially simplified:

- Current-spectrum MLP
- Temporal-statistics MLP
- GRU with current-spectrum skip connection
- Compact GRUs with reduced embedding and hidden dimensions

---

# 3. Initial Model Comparison

The initial benchmark produced the following results.

| Model | MAE | RMSE | R² | Training Time |
|---|---:|---:|---:|---:|
| **LSTM** | **8.18** | **12.18** | **0.9395** | 343 s |
| TCN | 9.91 | 12.72 | 0.9340 | 1057 s |
| Extra Trees | 16.34 | 21.35 | 0.8142 | 85 s |
| Random Forest | 21.03 | 25.55 | 0.7337 | 93 s |
| XGBoost | 28.09 | 33.09 | 0.5534 | 293 s |
| Ridge | 45.01 | 56.56 | -0.3048 | 7 s |

The first important observation is the large separation between the temporal models and the classical models.

For example:

$$
RMSE_{LSTM}=12.18
$$

compared with:

$$
RMSE_{ExtraTrees}=21.35
$$

Even the strongest classical model, Extra Trees, was substantially less accurate than the LSTM.

Ridge Regression performed particularly poorly:

$$
R^2=-0.305
$$

A negative $R^2$ indicates that the linear model performed worse on the validation experiment than simply predicting the validation-set mean Reynolds number.

---

# 4. Why the Classical Models Were Insufficient

The classical models received the same 40-step acoustic history, but that history was represented as one flattened vector:

$$
40\times4\times27 \rightarrow 4320
$$

This provides the model with the measurements but does not explicitly represent the sequential relationship:

$$
t-39 \rightarrow t-38 \rightarrow \cdots \rightarrow t
$$

The large performance difference between the classical models and the sequence models indicates that **temporal organization contains useful information for predicting Reynolds number**.

This is particularly evident from the comparison:

| Architecture | RMSE |
|---|---:|
| Ridge | 56.56 |
| Random Forest | 25.55 |
| Extra Trees | 21.35 |
| LSTM | **12.18** |

Thus, simply providing the historical observations is not sufficient. How the model represents the temporal history is important.

---

# 5. LSTM vs TCN

Because the LSTM substantially outperformed the classical models, the next question was whether another temporal architecture could improve upon it.

A Temporal Convolutional Network (TCN) was evaluated.

| Model | MAE | RMSE | R² | Training Time |
|---|---:|---:|---:|---:|
| **LSTM** | **8.18** | **12.18** | **0.9395** | **343 s** |
| TCN | 9.91 | 12.72 | 0.9340 | 1057 s |

The TCN came reasonably close to the LSTM in RMSE and R², providing additional evidence that temporal modeling is important.

However, it did not improve prediction accuracy:

$$
RMSE_{TCN}=12.72
$$

versus:

$$
RMSE_{LSTM}=12.18
$$

and required approximately three times the training time.

Therefore, there was no evidence from the current experiment that the TCN should replace the LSTM.

---

# 6. Testing Whether the LSTM Was More Complex Than Necessary

Although the LSTM performed well, the next objective was to determine whether its complexity was actually required.

Three simpler alternatives were evaluated.

| Model | MAE | RMSE | R² | Parameters | Training Time |
|---|---:|---:|---:|---:|---:|
| LSTM | **8.18** | **12.18** | **0.9395** | 35,137 | 343 s |
| GRU | 8.54 | 12.60 | 0.9353 | 26,817 | 162 s |
| GRU + Current Skip | 9.42 | 12.70 | 0.9342 | 21,569 | 120 s |
| Temporal-Statistics MLP | 13.69 | 16.81 | 0.8848 | 73,409 | 19 s |
| Current-Spectrum MLP | 15.70 | 19.41 | 0.8464 | 8,033 | 7 s |

These experiments provide additional information about the structure of the problem.

---

# 7. Is the Current Acoustic Spectrum Sufficient?

The Current-Spectrum MLP removed the temporal history completely and used only:

$$
X_t \rightarrow Re_t
$$

Its performance deteriorated to:

$$
MAE=15.70
$$

$$
RMSE=19.41
$$

$$
R^2=0.846
$$

compared with the LSTM:

$$
MAE=8.18
$$

$$
RMSE=12.18
$$

$$
R^2=0.940
$$

Therefore, although the current spectrum contains substantial Reynolds information, the current measurement alone does not reproduce the performance obtained when temporal history is modeled.

---

# 8. Can Temporal History Be Replaced by Summary Statistics?

A second simplification summarized the 40-step history using quantities such as:

- current value,
- mean,
- standard deviation,
- recent change,
- temporal trend.

The resulting Temporal-Statistics MLP achieved:

$$
MAE=13.69
$$

$$
RMSE=16.81
$$

$$
R^2=0.885
$$

This was better than using only the current spectrum, but still substantially worse than the LSTM and GRU.

Therefore:

$$
\text{Current spectrum}
<
\text{Temporal summaries}
<
\text{Explicit temporal model}
$$

The results indicate that simply summarizing the temporal window removes information that is useful for Reynolds prediction.

---

# 9. GRU as a Simpler Temporal Model

The GRU produced a much more interesting result.

The original GRU achieved:

$$
MAE=8.54
$$

$$
RMSE=12.60
$$

$$
R^2=0.9353
$$

This was very close to the LSTM while using fewer parameters and substantially less training time.

This suggested that the important component was not necessarily the full complexity of the LSTM architecture.

Instead, the results suggested that the model primarily needed:

1. a representation of the acoustic spectrum,
2. preservation of temporal order,
3. a relatively small recurrent state.

This motivated reducing the GRU architecture further.

---

# 10. Compact GRU Search

A systematic search was performed over smaller spectral embedding and GRU hidden dimensions.

The models satisfying the predefined performance requirements were:

| Model | Embedding | Hidden | MAE | RMSE | R² | Parameters | Training Time |
|---|---:|---:|---:|---:|---:|---:|---:|
| **GRU e24/h16** | **24** | **16** | **7.777** | **12.000** | **0.9413** | **2,705** | **91 s** |
| GRU e32/h16 | 32 | 16 | 8.390 | 12.500 | 0.9363 | 3,313 | 118 s |
| GRU e16/h24 | 16 | 24 | 7.846 | **11.914** | **0.9421** | 3,497 | 98 s |
| GRU e24/h24 | 24 | 24 | 8.937 | 12.936 | 0.9317 | 4,297 | 123 s |
| GRU e24/h32 | 24 | 32 | 8.465 | 12.799 | 0.9332 | 6,273 | 87 s |
| GRU e16/h48 | 16 | 48 | 8.670 | 12.599 | 0.9352 | 10,001 | 123 s |
| GRU e32/h48 | 32 | 48 | 8.377 | 12.782 | 0.9334 | 12,753 | 92 s |

Two models stand out:

### GRU e16/h24

This model obtained the best RMSE and R²:

$$
RMSE=11.914
$$

$$
R^2=0.9421
$$

with only:

$$
3497
$$

parameters.

### GRU e24/h16

This model obtained the lowest MAE:

$$
MAE=7.777
$$

while achieving:

$$
RMSE=12.000
$$

$$
R^2=0.9413
$$

with only:

$$
2705
$$

parameters.

---

# 11. Final Model Selection

Based on the current experiments, the selected model is:

$$
\boxed{\text{GRU with embedding dimension 24 and hidden dimension 16}}
$$

or:

$$
\boxed{\text{GRU e24/h16}}
$$

The selection is based on the combination of **predictive accuracy and model simplicity**, rather than accuracy alone.

The comparison with the original LSTM is:

| Metric | LSTM | GRU e24/h16 |
|---|---:|---:|
| MAE | 8.178 | **7.777** |
| RMSE | 12.176 | **12.000** |
| R² | 0.9395 | **0.9413** |
| Parameters | 35,137 | **2,705** |
| Training Time | 343 s | **91 s** |

The compact GRU therefore improves all three validation accuracy metrics while dramatically reducing model complexity.

---

# 12. Reduction in Model Complexity

The parameter reduction is:

$$
1-\frac{2705}{35137}
\approx 0.923
$$

or approximately:

$$
\boxed{92\% \text{ fewer parameters}}
$$

The compact GRU contains only about:

$$
\frac{2705}{35137}\approx7.7\%
$$

of the parameters of the original LSTM.

Training time was also reduced from approximately:

$$
343\text{ seconds}
$$

to:

$$
91\text{ seconds}
$$

which is approximately:

$$
\boxed{3.8\times \text{ faster}}
$$

for this experiment.

---

# 13. Why GRU e24/h16 Is Preferred Over GRU e16/h24

The GRU e16/h24 produced slightly better RMSE and R²:

$$
RMSE: 11.914 \text{ vs } 12.000
$$

$$
R^2: 0.9421 \text{ vs } 0.9413
$$

However, GRU e24/h16 has:

- lower MAE,
- 2,705 instead of 3,497 parameters,
- approximately 23% fewer parameters than e16/h24,
- essentially equivalent RMSE and R².

The differences in validation accuracy are very small:

$$
\Delta RMSE \approx 0.086
$$

and:

$$
\Delta R^2 \approx 0.0008
$$

Given the current evidence, the additional complexity of e16/h24 is not justified by such a small improvement in RMSE.

Therefore, GRU e24/h16 provides the stronger **accuracy–complexity trade-off**.

---

# 14. What the Model Comparison Tells Us

The experiments reveal an important progression:

$$
\text{Linear model}
\rightarrow
\text{Tree ensembles}
\rightarrow
\text{Temporal model}
\rightarrow
\text{Compact temporal model}
$$

The classical models demonstrated that simply flattening the 40-step acoustic history was insufficient.

The Current-Spectrum MLP demonstrated that the current acoustic spectrum alone was insufficient to achieve the best accuracy.

The Temporal-Statistics MLP demonstrated that simple summaries of the history also lose useful information.

The LSTM and TCN demonstrated that preserving temporal structure substantially improves prediction.

The GRU then showed that the full complexity of the LSTM was unnecessary.

Finally, the compact-GRU search showed that the recurrent representation itself can be very small without sacrificing predictive performance.

The evidence therefore supports the following interpretation:

$$
\boxed{\text{Temporal structure matters, but a large temporal model is not required.}}
$$

---

# 15. Final Architecture

The selected architecture can be summarized as:

$$
X_{t-39:t,p,f}
$$

$$
\downarrow
$$

$$
\text{Shared 27-frequency encoder}
$$

with embedding dimension:

$$
27 \rightarrow 24
$$

followed by aggregation across the four probes:

$$
\text{Mean}_{p=1}^{4}
$$

producing a temporal sequence:

$$
40\times24
$$

which is passed through a GRU with hidden dimension:

$$
h=16
$$

followed by a scalar prediction head:

$$
h_t \rightarrow \hat{Re}_t
$$

Therefore:

$$
\boxed{
40\times4\times27
\rightarrow
40\times24
\rightarrow
GRU_{16}
\rightarrow
\hat{Re}_t
}
$$

with only:

$$
\boxed{2705\text{ trainable parameters}}
$$

---

# 16. Current Conclusion

Based on the **currently available train/validation experiment**, GRU e24/h16 is the preferred model.

It provides:

- the lowest observed MAE among the LSTM and selected compact models,
- slightly lower RMSE than the original LSTM,
- slightly higher R² than the original LSTM,
- approximately 92% fewer parameters,
- approximately 3.8× shorter observed training time,
- and substantially better predictive performance than the classical models and non-recurrent neural-network alternatives.

The result also changes the interpretation of the original LSTM success.

The evidence does **not** indicate that a large LSTM is necessary to recover Reynolds number from the acoustic measurements.

Instead, the experiments indicate that:

$$
\boxed{\text{temporal information is important}}
$$

but:

$$
\boxed{\text{a small recurrent representation is sufficient on the current data}}
$$

Therefore, GRU e24/h16 is currently the strongest balance between predictive performance and model complexity.

---

# 17. Important Limitation

The model-selection conclusion is based on one cross-experiment evaluation:

$$
1211\_1 \rightarrow 1212\_1
$$

This is stronger than a random train/test split within one experiment because the model is evaluated on a different experimental run.

However, it is still only **one train/validation experiment pair**.

Therefore, the current evidence supports:

> **GRU e24/h16 is the preferred model on the currently available cross-experiment benchmark.**

It does not yet establish that GRU e24/h16 will universally outperform the LSTM on future experimental runs.

The final confirmation should therefore come from additional independent experimental runs when they become available. The preferred model should retain its advantage in MAE/RMSE/R² without showing substantially greater variability across experiments.