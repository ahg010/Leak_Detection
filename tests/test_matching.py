import pandas as pd
from src.sensor_fidelity.matching import load_recording


def test_skip_floor_and_duplicate_aggregation(tmp_path):
    p=tmp_path/"raw.csv"
    pd.DataFrame({"receipt_time":["2026-01-01T00:00:00Z","2026-01-01T00:00:01.100Z","2026-01-01T00:00:01.900Z"],"f25":[999,10,20]}).to_csv(p,index=False)
    frame=load_recording(p,"Thing01",["f25"],skip_first_rows=1)
    assert len(frame)==1
    assert frame.iloc[0]["f25_Thing01"]==15
