"""CLI entry point. Example: python run.py --source source_USB"""
import argparse
from pathlib import Path
from src.sensor_fidelity.config import load_config
from src.sensor_fidelity.pipeline import run_analysis

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",choices=["source","source_USB"],default=None)
    parser.add_argument("--config",default=str(Path(__file__).resolve().parent/"config.json"))
    args=parser.parse_args()
    result=run_analysis(load_config(args.config,args.source))
    print(result["best_sensor_lags"].to_string(index=False))
    print("Results:",result["results_dir"])
