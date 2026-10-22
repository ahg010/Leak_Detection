import numpy as np
import pandas as pd
from .lag_analysis import safe_corr


def evaluate_one(x, y, timestamps, min_pairs=20, amplitude_units="unknown"):
    frame = pd.DataFrame({"x": np.asarray(x, float), "y": np.asarray(y, float),
                          "timestamp": pd.to_datetime(timestamps)}).dropna().sort_values("timestamp")
    x, y = frame.x.to_numpy(), frame.y.to_numpy()
    result = {"n_pairs":len(frame), "pearson_r":safe_corr(x,y,min_pairs)}
    keys = ["diff_r","slope","intercept","r2","residual_rmse","residual_nrmse","ratio_cv","difference_sd"]
    if len(x)<min_pairs or np.std(x)<1e-12 or np.std(y)<1e-12:
        return {**result, **{k:np.nan for k in keys}}
    slope, intercept = np.polyfit(x,y,1)
    residual = y - (intercept+slope*x)
    rmse = float(np.sqrt(np.mean(residual**2)))
    consecutive = frame.timestamp.diff().dt.total_seconds().to_numpy()[1:] == 1
    dx,dy = np.diff(x)[consecutive],np.diff(y)[consecutive]
    ratio_cv = np.nan
    if amplitude_units == "linear":
        valid = np.abs(x)>1e-10
        if valid.sum()>=min_pairs:
            ratio = y[valid]/x[valid]
            if abs(ratio.mean())>1e-12:
                ratio_cv=float(np.std(ratio)/abs(ratio.mean()))
    return {**result,"diff_r":safe_corr(dx,dy,5),"slope":float(slope),"intercept":float(intercept),
            "r2":float(1-np.sum(residual**2)/np.sum((y-y.mean())**2)),
            "residual_rmse":rmse,"residual_nrmse":float(rmse/np.std(y)),
            "ratio_cv":ratio_cv,"difference_sd":float(np.std(y-x))}


def all_fidelity_metrics(zero, corrected, freqs, sensors, delays, min_pairs=20, amplitude_units="unknown"):
    rows=[]
    for condition,frame in [("lag_0",zero),("corrected",corrected)]:
        for f in freqs:
            for s in sensors:
                m=evaluate_one(frame[f"{f}_source"],frame[f"{f}_{s}"],frame.timestamp,min_pairs,amplitude_units)
                rows.append({"condition":condition,"frequency":f,"sensor":s,
                             "applied_lag_s":0 if condition=="lag_0" else int(delays[s]),**m})
    return pd.DataFrame(rows)


def trend_metrics(frame, f, sensor, window=5, min_pairs=20):
    pair=frame.set_index("timestamp")[[f"{f}_source",f"{f}_{sensor}"]].sort_index()
    full_idx=pd.date_range(pair.index.min(),pair.index.max(),freq="1s",tz="UTC")
    smooth=pair.reindex(full_idx).rolling(window,center=True,min_periods=window).mean().dropna()
    if len(smooth)<min_pairs:
        return {"trend_corr":np.nan,"direction_agreement":np.nan,"smoothed_diff_corr":np.nan}
    changes=smooth.diff()
    changes=changes.loc[smooth.index.to_series().diff().dt.total_seconds().eq(1)].dropna()
    dx,dy=changes.iloc[:,0],changes.iloc[:,1]
    nz=dx.ne(0)&dy.ne(0)
    return {"trend_corr":safe_corr(smooth.iloc[:,0],smooth.iloc[:,1],min_pairs),
            "direction_agreement":float((np.sign(dx[nz])==np.sign(dy[nz])).mean()) if nz.any() else np.nan,
            "smoothed_diff_corr":safe_corr(dx,dy,5)}


def all_trend_metrics(zero,corrected,freqs,sensors,window,min_pairs):
    rows=[]
    for condition,frame in [("lag_0",zero),("corrected",corrected)]:
        for f in freqs:
            for s in sensors:
                rows.append({"condition":condition,"frequency":f,"sensor":s,
                             **trend_metrics(frame,f,s,window,min_pairs)})
    return pd.DataFrame(rows)


def nonlinear_metrics(zero,corrected,freqs,sensors,min_pairs=20):
    from scipy.stats import spearmanr
    from scipy.spatial.distance import pdist,squareform
    rows=[]
    for condition,frame in [("lag_0",zero),("corrected",corrected)]:
        for f in freqs:
            for s in sensors:
                pair=frame[[f"{f}_source",f"{f}_{s}"]].dropna()
                x,y=pair.iloc[:,0].to_numpy(),pair.iloc[:,1].to_numpy()
                if len(x)<min_pairs or np.std(x)<1e-12 or np.std(y)<1e-12:continue
                A,B=squareform(pdist(x[:,None])),squareform(pdist(y[:,None]))
                A=A-A.mean(axis=0)-A.mean(axis=1)[:,None]+A.mean()
                B=B-B.mean(axis=0)-B.mean(axis=1)[:,None]+B.mean()
                dxy,dxx,dyy=np.mean(A*B),np.mean(A*A),np.mean(B*B)
                dcor=float(np.sqrt(max(dxy,0)/np.sqrt(dxx*dyy))) if dxx>0 and dyy>0 else np.nan
                rows.append({"condition":condition,"frequency":f,"sensor":s,
                             "pearson_r":safe_corr(x,y,min_pairs),"spearman_r":float(spearmanr(x,y).statistic),"distance_corr":dcor})
    return pd.DataFrame(rows)
