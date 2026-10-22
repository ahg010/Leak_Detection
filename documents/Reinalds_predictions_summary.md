# Executive Summary — Reynolds Number Prediction Model Selection

## Objective

The goal was to determine whether the **Reynolds number can be reliably estimated from acoustic sensor measurements** and identify a model that provides strong prediction accuracy without unnecessary complexity.

To make the evaluation realistic, the models were:

- **trained on experiment `1211_1`**
- **evaluated on a different experiment, `1212_1`**

This tests whether the learned relationship transfers from one experimental run to another.

---

## Methods Evaluated

We evaluated a broad range of approaches, progressing from conventional machine-learning methods to models specifically designed to use the history of the acoustic signal.
| Method | MAE | RMSE | R² | Training Time (sec) |
|---|---:|---:|---:|---:|
| Ridge Regression | 45.01 | 56.56 | -0.305 | 6.8 |
| XGBoost | 28.09 | 33.09 | 0.553 | 292.7 |
| Random Forest | 21.03 | 25.55 | 0.734 | 92.9 |
| Extra Trees | 16.34 | 21.35 | 0.814 | 85.4 |
| Current-Spectrum Neural Network | 15.70 | 19.41 | 0.846 | 6.6 |
| Temporal-Statistics Neural Network | 13.69 | 16.81 | 0.885 | 19.1 |
| TCN | 9.91 | 12.72 | 0.934 | 1,056.6 |
| Standard GRU | 8.54 | 12.60 | 0.935 | 161.6 |
| LSTM | 8.18 | 12.18 | 0.940 | 343.3 |
| **Compact GRU — Final Model** | **7.78** | **12.00** | **0.941** | **90.5** |



**Lower MAE and RMSE are better. Higher R² is better.**

---

# Key Finding

The experiments showed that **using the recent history of the acoustic measurements is important**.

Traditional machine-learning approaches performed substantially worse than models designed to use this history.

For example:

- Extra Trees: **MAE = 16.34**
- LSTM: **MAE = 8.18**
- Final Compact GRU: **MAE = 7.78**

The final model therefore reduced average prediction error by approximately **52% compared with the best classical model**.

---

# Why We Did Not Stop at the LSTM

The LSTM initially provided the strongest performance and demonstrated that Reynolds number can be accurately recovered from the acoustic measurements.

However, the LSTM was relatively complex.

We therefore investigated whether the same predictive capability could be achieved with a substantially smaller model.

This resulted in the **Compact GRU**.

|  | LSTM | **Final Compact GRU** |
|---|---:|---:|
| MAE | 8.18 | **7.78** |
| RMSE | 12.18 | **12.00** |
| R² | 0.940 | **0.941** |
| Model Parameters | 35,137 | **2,705** |
| Training Time | 343 sec | **91 sec** |

---

# Advantages of the Final Model

The Compact GRU provides essentially the best of both objectives:

### Better prediction

Compared with the original LSTM:

- MAE improved from **8.18 → 7.78**
- RMSE improved from **12.18 → 12.00**
- R² improved from **0.940 → 0.941**

### Much smaller model

Model size decreased from:

**35,137 → 2,705 parameters**

This represents approximately:

**92% fewer parameters**

### Faster training

Training time decreased from:

**343 seconds → 91 seconds**

or approximately:

**3.8× faster**

### Strong performance on a different experiment

The model was trained on one experimental run and evaluated on another, rather than being evaluated only on randomly separated observations from the same experiment.

This provides stronger evidence that the model is learning a relationship that can transfer between these two experiments.

---

# Final Recommendation

Based on the currently available data, the **Compact GRU is the preferred model for predicting Reynolds number from the acoustic measurements**.

It provides:

- **the lowest average prediction error**
- **approximately 52% lower MAE than the best classical model**
- slightly better accuracy than the original LSTM
- **92% fewer model parameters than the LSTM**
- approximately **3.8× faster training**
- a much simpler model while retaining the benefit of acoustic signal history

The main conclusion from the model-selection exercise is therefore:

> **The acoustic measurements contain sufficient information to predict Reynolds number accurately. Using recent signal history significantly improves prediction, but a large LSTM is not required. A small GRU provides the strongest combination of accuracy, simplicity, and computational efficiency on the current data.**

## Current Limitation

The comparison currently uses one cross-experiment evaluation:

**Train: `1211_1` → Validate: `1212_1`**

Therefore, the Compact GRU is the preferred model **based on the data currently available**. Additional experimental runs should be used to confirm that this advantage continues across a broader range of operating conditions.