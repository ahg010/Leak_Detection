from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm


def save_lag_curves(curves, sensors, out):
    fig,axes=plt.subplots(1,len(sensors),figsize=(5*len(sensors),4),sharey=True,squeeze=False)
    for ax,s in zip(axes.flat,sensors):
        g=curves[curves.sensor.eq(s)]
        ax.plot(g.lag_seconds,g.mean_corr,label="Mean")
        ax.plot(g.lag_seconds,g.median_corr,label="Median")
        ax.axvline(0,color="gray",ls="--");ax.axhline(0,color="gray",lw=.7)
        ax.set(title=s,xlabel="Sensor delay (seconds)");ax.legend();ax.grid(alpha=.2)
    axes.flat[0].set_ylabel("Correlation across frequencies")
    fig.tight_layout();fig.savefig(out,dpi=160);plt.close(fig)


def save_acf(acf,out):
    g=acf.groupby("lag_seconds").autocorr.agg(["mean","median"])
    fig,ax=plt.subplots(figsize=(10,4));g.plot(ax=ax)
    ax.set(xlabel="Source autocorrelation lag (seconds)",ylabel="Correlation")
    ax.axhline(0,color="gray",lw=.7);fig.tight_layout();fig.savefig(out,dpi=160);plt.close(fig)


def save_heatmaps(metrics,freqs,sensors,out,metric="pearson_r"):
    zero=metrics[metrics.condition.eq("lag_0")].pivot(index="frequency",columns="sensor",values=metric).reindex(index=freqs,columns=sensors)
    corrected=metrics[metrics.condition.eq("corrected")].pivot(index="frequency",columns="sensor",values=metric).reindex(index=freqs,columns=sensors)
    fig,axes=plt.subplots(1,3,figsize=(16,10),sharey=True)
    for ax,arr,title in zip(axes,[zero,corrected,corrected-zero],["Lag 0","Corrected","Improvement"]):
        im=ax.imshow(arr.to_numpy(float),cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
        ax.set_xticks(range(len(sensors)),sensors,rotation=35)
        ax.set_yticks(range(len(freqs)),freqs)
        ax.set_title(f"{metric}: {title}")
        fig.colorbar(im,ax=ax,shrink=.6)
    fig.tight_layout();fig.savefig(out,dpi=160,bbox_inches="tight");plt.close(fig)


def save_ranked_heatmap(metrics,freqs,sensors,out):
    arr=metrics[metrics.condition.eq("corrected")].pivot(index="frequency",columns="sensor",values="pearson_r").reindex(index=freqs,columns=sensors)
    arr=arr.loc[arr.median(axis=1).sort_values().index]
    fig,ax=plt.subplots(figsize=(8,11))
    im=ax.imshow(arr.to_numpy(float),cmap="RdBu_r",norm=TwoSlopeNorm(vmin=-1,vcenter=0,vmax=1),aspect="auto")
    ax.set_xticks(range(len(sensors)),sensors);ax.set_yticks(range(len(arr)),arr.index)
    for i in range(len(arr)):
        for j in range(len(sensors)):
            v=arr.iloc[i,j]
            if np.isfinite(v):ax.text(j,i,f"{v:.2f}",ha="center",va="center",fontsize=8,color="white" if abs(v)>.65 else "black")
    fig.colorbar(im,ax=ax,label="Pearson r");ax.set(title="Corrected correlation (worst → best)",ylabel="Frequency")
    fig.tight_layout();fig.savefig(out,dpi=160,bbox_inches="tight");plt.close(fig)


def save_frequency_plots(zero,corrected,freqs,sensors,delays,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for f in freqs:
        fig,axes=plt.subplots(len(sensors),2,figsize=(13,3.2*len(sensors)),sharex=True,squeeze=False)
        for i,s in enumerate(sensors):
            for j,(label,frame) in enumerate([("Lag 0",zero),("Corrected",corrected)]):
                ax=axes[i,j]
                for col,title in [(f"{f}_source","Source"),(f"{f}_{s}",s)]:
                    v=frame[col]
                    sd=v.std()
                    z=(v-v.mean())/sd if np.isfinite(sd) and sd>0 else v*float("nan")
                    ax.plot(frame.timestamp,z,label=title,lw=1.4)
                ax.set_title(f"{f} / {s} / {label}"+(f" ({delays[s]}s)" if j else ""))
                ax.grid(alpha=.2)
                if i==0:ax.legend()
        fig.tight_layout();fig.savefig(out/f"{f}_timeseries.png",dpi=150,bbox_inches="tight");plt.close(fig)


def save_lowess_comparison(nonlinear,zero,corrected,out):
    from statsmodels.nonparametric.smoothers_lowess import lowess
    top=nonlinear[nonlinear.condition.eq("corrected")].nlargest(3,"distance_corr")
    if top.empty:return
    fig,axes=plt.subplots(len(top),2,figsize=(12,4*len(top)),squeeze=False)
    for i,(_,record) in enumerate(top.iterrows()):
        for ax,(condition,frame) in zip(axes[i],[('lag_0',zero),('corrected',corrected)]):
            pair=frame[[f"{record.frequency}_source",f"{record.frequency}_{record.sensor}"]].dropna()
            x,y=pair.iloc[:,0].to_numpy(),pair.iloc[:,1].to_numpy()
            ax.scatter(x,y,s=12,alpha=.35)
            fit=lowess(y,x,frac=.35,return_sorted=True)
            ax.plot(fit[:,0],fit[:,1],color="red",lw=2)
            ax.set(title=f"{record.frequency}/{record.sensor}/{condition}",xlabel="Source",ylabel="Sensor")
    fig.tight_layout();fig.savefig(out,dpi=160);plt.close(fig)
