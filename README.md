# Sensor fidelity — lag-corrected exploratory analysis

One interactive notebook plus reusable `src/sensor_fidelity` functions. `config.json` lives at the project root.

## Layout

- `config.json`:   file names, selected source, frequency bands, lag range, input/output paths.
- `data/August_Records/`: raw CSV recordings (not committed).
- `notebooks/sensor_fidelity_analysis.ipynb`: **interactive** matching, lag search, autocorrelation, before/after EDA, frequency ranking, annotated heatmaps, overlays, temporal-trend diagnostics.
- `src/sensor_fidelity/`: pure data processing and metric functions, plus optional plotting helpers.
- `results/<source>/`: generated CSVs (not committed).
- `run.py`: optional headless numerical pipeline; **does not create figures**.

## Run

From the project root:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/sensor_fidelity_analysis.ipynb
```

Run the notebook cells top-to-bottom. Choose `SOURCE_OVERRIDE = None` to use the `selected_source` in `config.json`, or set it to `"source_USB"`.

**Path resolution:** `data_dir` and `output_dir` are resolved relative to the directory containing `config.json`, never the Jupyter process working directory. If your project root is `/home/ubuntu/notebooks/Leak_Detection`, `data_dir: data/August_Records` resolves to `/home/ubuntu/notebooks/Leak_Detection/data/August_Records`.

Optional headless numerical run:

```bash
python run.py --source source
```

## Analysis conventions

`source(t)` versus `sensor(t+lag)`, using actual timestamp joins. Select one lag per sensor by maximizing mean Pearson correlation over all 27 frequencies. Compare zero and corrected lags on the same source-time interval. Individual frequency best lags are diagnostic only. Autocorrelation peaks can create multiple cross-correlation peaks; estimates are descriptive until validated independently.
