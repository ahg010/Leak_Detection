import json
from pathlib import Path


def load_config(path, source_override=None):
    path = Path(path).expanduser().resolve()
    with path.open(encoding="utf-8") as f:
        config = json.load(f)
    root = path.parent  # config.json lives at project root
    source = source_override or config["selected_source"]
    if source not in config["files"] or source in config["sensors"]:
        raise ValueError(f"Invalid source {source!r}")
    config["selected_source"] = source
    config["project_root"] = root
    config["data_path"] = (root / config["data_dir"]).resolve()
    config["results_path"] = (root / config["output_dir"] / source).resolve()
    if config["lag_analysis"]["selection_metric"] != "mean_pearson":
        raise ValueError("Only mean_pearson lag selection is implemented")
    if not config["lag_analysis"]["common_lag_per_sensor"]:
        raise ValueError("One common lag per sensor is required")
    return config
