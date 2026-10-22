import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from .matching import match_recordings
from .lag_analysis import scan_lags, align_comparison, source_autocorrelation
from .metrics import all_fidelity_metrics, all_trend_metrics, nonlinear_metrics


def run_analysis(config):
    out=Path(config["results_path"])
    tables=out/"tables";data_out=out/"data"
    for p in (tables,data_out):p.mkdir(parents=True,exist_ok=True)
    freqs=config["freq_cols"];sensors=config["sensors"]
    lag_cfg=config["lag_analysis"];min_pairs=lag_cfg["min_pairs"]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=RuntimeWarning,message="invalid value encountered in cast")
        matched,input_summary=match_recordings(config)
        matched.to_csv(data_out/"matched_unshifted.csv",index=False)
        input_summary.to_csv(tables/"input_summary.csv",index=False)
        scan,curves,best=scan_lags(matched,freqs,sensors,lag_cfg["min_lag_seconds"],lag_cfg["max_lag_seconds"],min_pairs)
        scan.to_csv(tables/"lag_scan_per_frequency.csv",index=False)
        curves.to_csv(tables/"sensor_lag_curves.csv",index=False)
        best.to_csv(tables/"best_sensor_lags.csv",index=False)
        delays=dict(zip(best.sensor,best.lag_seconds.astype(int)))
        # Frequency-level best lags are diagnostic, NOT the chosen correction.
        per_freq=scan.loc[scan.groupby(["sensor","frequency"]).pearson_r.idxmax()]
        per_freq.to_csv(tables/"frequency_best_lags_diagnostic.csv",index=False)
        per_freq.groupby(["sensor","lag_seconds"]).size().unstack(fill_value=0).to_csv(tables/"frequency_lag_counts.csv")
        acf=source_autocorrelation(matched,freqs,lag_cfg["max_lag_seconds"],min_pairs)
        acf.to_csv(tables/"source_autocorrelation.csv",index=False)
        zero,corrected=align_comparison(matched,freqs,sensors,delays,min_pairs)
        zero.to_csv(data_out/"matched_zero_lag_same_window.csv",index=False)
        corrected.to_csv(data_out/"matched_sensor_delay_corrected.csv",index=False)
        metrics=all_fidelity_metrics(zero,corrected,freqs,sensors,delays,min_pairs,config["eda"]["amplitude_units"])
        metrics.to_csv(tables/"fidelity_metrics_zero_vs_corrected.csv",index=False)
        overall=metrics.groupby(["condition","sensor"],as_index=False).agg(
            valid_frequencies=("pearson_r","count"),mean_pearson_r=("pearson_r","mean"),
            median_pearson_r=("pearson_r","median"),mean_diff_r=("diff_r","mean"),
            median_residual_nrmse=("residual_nrmse","median"))
        overall.to_csv(tables/"overall_zero_vs_corrected.csv",index=False)
        wide=metrics.pivot(index=["frequency","sensor"],columns="condition",values=["pearson_r","diff_r","residual_nrmse"])
        wide.columns=[f"{metric}_{condition}" for metric,condition in wide.columns]
        wide["pearson_improvement"]=wide.pearson_r_corrected-wide.pearson_r_lag_0
        wide["diff_improvement"]=wide.diff_r_corrected-wide.diff_r_lag_0
        wide.reset_index().to_csv(tables/"frequency_sensor_improvement.csv",index=False)
        for condition in ("lag_0","corrected"):
            m=metrics[metrics.condition.eq(condition)]
            for metric in ("pearson_r","diff_r"):
                arr=m.pivot(index="frequency",columns="sensor",values=metric).reindex(index=freqs,columns=sensors)
                arr["winner"]=arr.idxmax(axis=1)
                arr["best_r"]=arr[sensors].max(axis=1)
                arr.to_csv(tables/f"frequency_winners_{metric}_{condition}.csv")
        corrected_metrics=metrics[metrics.condition.eq("corrected")].copy()
        corrected_metrics["rank_within_frequency"]=corrected_metrics.groupby("frequency").pearson_r.rank(ascending=False,method="min")
        corrected_metrics.sort_values(["frequency","rank_within_frequency"]).to_csv(tables/"ranked_sensors_corrected.csv",index=False)
        quality=corrected_metrics.pivot(index="frequency",columns="sensor",values="pearson_r").reindex(index=freqs,columns=sensors)
        quality["median_r"]=quality[sensors].median(axis=1)
        quality["mean_r"]=quality[sensors].mean(axis=1)
        quality["quality"]=pd.cut(quality.median_r,[-np.inf,.3,.5,.7,np.inf],labels=["Poor","Weak","Moderate","Strong"],right=False)
        quality.sort_values("median_r").to_csv(tables/"frequency_tracking_quality_corrected.csv")
        trends=all_trend_metrics(zero,corrected,freqs,sensors,config["eda"]["smoothing_window"],min_pairs)
        trends.to_csv(tables/"temporal_trends_zero_vs_corrected.csv",index=False)
        trends.groupby(["condition","sensor"])[["trend_corr","direction_agreement","smoothed_diff_corr"]].mean().to_csv(tables/"temporal_trend_summary.csv")
        nonlinear=nonlinear_metrics(zero,corrected,freqs,sensors,min_pairs)
        nonlinear.to_csv(tables/"nonlinear_zero_vs_corrected.csv",index=False)
        metadata={"selected_source":config["selected_source"],"estimated_lags_seconds":delays,
                  "matched_rows":len(matched),"comparison_rows":len(zero),
                  "comparison_start":str(zero.timestamp.min()),"comparison_end":str(zero.timestamp.max()),
                  "lag_search_note":"In-sample selection; descriptive improvement, not a formal significance test",
                  "configuration":{k:v for k,v in config.items() if k not in ("data_path","results_path","project_root")}}
        (out/"run_metadata.json").write_text(json.dumps(metadata,indent=2,default=str))
    return {"matched":matched,"lag_results":scan,"sensor_lag_curves":curves,"best_sensor_lags":best,
            "zero_df":zero,"lagged_df":corrected,"all_metrics":metrics,"overall":overall,
            "frequency_quality":quality,"trend_results":trends,"nonlinear_results":nonlinear,
            "source_acf":acf,"results_dir":out}
