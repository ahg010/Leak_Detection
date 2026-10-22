import json
from pathlib import Path
from src.sensor_fidelity.config import load_config

def test_paths_are_relative_to_config_not_cwd(tmp_path):
    project = tmp_path / "Leak_Detection"
    project.mkdir()
    conf = {"data_dir":"data/August_Records","output_dir":"results","selected_source":"source",
            "files":{"source":"s.csv","Thing01":"a.csv"},"sensors":["Thing01"],
            "lag_analysis":{"selection_metric":"mean_pearson","common_lag_per_sensor":True}}
    (project/"config.json").write_text(json.dumps(conf))
    result = load_config(project/"config.json")
    assert result["data_path"] == project/"data/August_Records"
    assert result["results_path"] == project/"results/source"
