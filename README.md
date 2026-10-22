# Spectral to Reynolds

Install dependencies: `pip install -r requirements.txt`. Open `notebooks/spectral_to_reynolds.ipynb` and run from top to bottom.

Place the eight existing CSV files under `data/2026-03-04/`; this archive does **not** contain the source data or your previously trained checkpoint. All paths/settings are in `config.json`.

The notebook calls `src/spectral_to_reynolds` for CSV cleaning, windowing, training, evaluation, and inference. Running the search writes `results/compact_gru_search.csv` and the selected e24/h16 checkpoint under `models/`. It does not overwrite the existing e16/h24 checkpoint.

**Important:** the original notebook's model save cell chose the lowest-RMSE model (e16/h24), while the report selected e24/h16 for the size/MAE trade-off. This repository saves the explicitly configured e24/h16 model. Data loading retains the original row-index alignment and zero-filling behavior; it does not filter leak periods.
