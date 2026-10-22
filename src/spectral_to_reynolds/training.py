import copy
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def metrics_physical(y_true_norm, y_pred_norm, name, train_seconds, params, reynolds_scale):
    yt = np.asarray(y_true_norm) * reynolds_scale
    yp = np.asarray(y_pred_norm) * reynolds_scale
    return {
        "Model": name,
        "MAE": mean_absolute_error(yt, yp),
        "RMSE": np.sqrt(mean_squared_error(yt, yp)),
        "R2": r2_score(yt, yp),
        "Train_seconds": train_seconds,
        "Parameters": params,
    }

def train_torch_regressor(model, Xtr, ytr, Xva, yva, device,
                          batch_size=128, epochs=120, lr=1e-3, patience=15):
    train_loader = DataLoader(
        TensorDataset(torch.tensor(Xtr), torch.tensor(ytr)),
        batch_size=batch_size, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        TensorDataset(torch.tensor(Xva), torch.tensor(yva)),
        batch_size=batch_size, shuffle=False, num_workers=0
    )

    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.L1Loss()

    best_state = None
    best_val = float("inf")
    best_epoch = 0
    stale = 0
    history = {"train": [], "val": []}

    start = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        train_sum = 0.0
        n = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            train_sum += loss.item() * len(yb)
            n += len(yb)

        model.eval()
        val_sum = 0.0
        nv = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb)
                val_sum += loss_fn(pred, yb).item() * len(yb)
                nv += len(yb)

        tr = train_sum / n
        va = val_sum / nv
        history["train"].append(tr)
        history["val"].append(va)

        if va < best_val:
            best_val = va
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1

        if epoch == 1 or epoch % 10 == 0:
            print(f"Epoch {epoch:03d} | train={tr:.5f} | val={va:.5f}")

        if stale >= patience:
            print("Early stopping at", epoch)
            break

    seconds = time.perf_counter() - start
    model.load_state_dict(best_state)

    preds = []
    model.eval()
    with torch.no_grad():
        for xb, _ in val_loader:
            preds.append(model(xb.to(device)).cpu().numpy())
    pred = np.concatenate(preds)

    params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Best epoch: {best_epoch} | parameters: {params:,} | time: {seconds:.1f}s")
    return model, pred, history, seconds, params
