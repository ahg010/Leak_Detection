import copy
import json
import random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from .data import verify_files, prepare_run, make_windows
from .model import CompactSpectralGRU
from .training import train_torch_regressor, metrics_physical

REFERENCE_RESULTS = [
    {"Model":"LSTM reference", "Embed_dim":np.nan,"Hidden_dim":np.nan,"MAE":8.177720,"RMSE":12.176184,"R2":0.939523,"Train_seconds":343.343762,"Parameters":35137},
    {"Model":"GRU 64/64 reference", "Embed_dim":64,"Hidden_dim":64,"MAE":8.540041,"RMSE":12.597369,"R2":0.935267,"Train_seconds":161.645009,"Parameters":26817},
]

def load_config(root):
    return json.loads((Path(root)/"config.json").read_text())

def load_data(root, cfg):
    verify_files(cfg, root)
    train = prepare_run(cfg["train_iteration"], cfg, root)
    val = prepare_run(cfg["validation_iteration"], cfg, root)
    Xtr, ytr = make_windows(train, cfg["window_size"])
    Xva, yva = make_windows(val, cfg["window_size"])
    return train, val, Xtr, ytr, Xva, yva

def run_search(root, cfg, Xtr, ytr, Xva, yva):
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    rows, models = [], {}
    for e in cfg["embed_dims"]:
        for h in cfg["hidden_dims"]:
            random.seed(cfg["seed"])
            np.random.seed(cfg["seed"])
            torch.manual_seed(cfg["seed"])
            if torch.cuda.is_available(): torch.cuda.manual_seed_all(cfg["seed"])
            model = CompactSpectralGRU(e,h)
            model, pred, history, seconds, params = train_torch_regressor(
                model,Xtr,ytr,Xva,yva,device=device,batch_size=cfg["batch_size"],
                epochs=cfg["epochs"],lr=cfg["learning_rate"],patience=cfg["patience"])
            result = metrics_physical(yva,pred,f"GRU e{e}/h{h}",seconds,params,cfg["reynolds_scale"])
            result.update(Embed_dim=e,Hidden_dim=h)
            rows.append(result)
            models[(e,h)] = copy.deepcopy(model).cpu()
    search = pd.DataFrame(rows)
    all_results = pd.concat([pd.DataFrame(REFERENCE_RESULTS),search],ignore_index=True)
    lstm = REFERENCE_RESULTS[0]
    all_results["MAE_vs_LSTM_%"] = 100*(all_results.MAE/lstm["MAE"]-1)
    all_results["RMSE_vs_LSTM_%"] = 100*(all_results.RMSE/lstm["RMSE"]-1)
    all_results["Param_ratio_vs_LSTM"] = all_results.Parameters/lstm["Parameters"]
    output = Path(root)/cfg["output_dir"]
    output.mkdir(parents=True,exist_ok=True)
    all_results.sort_values("RMSE").to_csv(output/"compact_gru_search.csv",index=False)
    selected = (cfg["selected_embed_dim"],cfg["selected_hidden_dim"])
    if selected not in models: raise ValueError("Selected dimensions are not in the search grid")
    model_dir=Path(root)/cfg["model_dir"]
    model_dir.mkdir(parents=True,exist_ok=True)
    path=model_dir/f"compact_gru_e{selected[0]}_h{selected[1]}_{cfg['train_iteration']}_to_{cfg['validation_iteration']}.pt"
    torch.save({"model_state_dict":models[selected].state_dict(),"embed_dim":selected[0],"hidden_dim":selected[1],
        "window_size":cfg["window_size"],"spectrum_scale":cfg["spectrum_scale"],
        "reynolds_scale":cfg["reynolds_scale"],"train_iteration":cfg["train_iteration"],
        "validation_iteration":cfg["validation_iteration"]},path)
    return search,all_results,path

def load_saved_model(path, device="cpu"):
    checkpoint=torch.load(path,map_location=device,weights_only=True)
    model=CompactSpectralGRU(checkpoint["embed_dim"],checkpoint["hidden_dim"])
    model.load_state_dict(checkpoint["model_state_dict"])
    return model.to(device).eval(),checkpoint

def predict_saved(path, X):
    model,checkpoint=load_saved_model(path)
    with torch.no_grad():
        pred=model(torch.as_tensor(X,dtype=torch.float32)).cpu().numpy()
    return pred*checkpoint["reynolds_scale"]
