import numpy as np
import pandas as pd
from src.sensor_fidelity.lag_analysis import scan_lags,align_comparison


def test_common_lag_recovered_and_comparison_window():
    rng=np.random.default_rng(8)
    n=160
    source=rng.normal(size=n)
    sensor=np.r_[np.zeros(6),source[:-6]]
    df=pd.DataFrame({"timestamp":pd.date_range("2026-01-01",periods=n,freq="s",tz="UTC"),
                     "f25_source":source,"f25_Thing01":sensor,
                     "f50_source":source*2+1,"f50_Thing01":sensor*2+1})
    scan,curves,best=scan_lags(df,["f25","f50"],["Thing01"],0,15,20)
    assert int(best.iloc[0].lag_seconds)==6
    zero,corrected=align_comparison(df,["f25","f50"],["Thing01"],{"Thing01":6})
    assert zero.timestamp.equals(corrected.timestamp)
    assert len(zero)==n-6
    assert np.corrcoef(corrected.f25_source,corrected.f25_Thing01)[0,1]>.99
