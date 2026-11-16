import numpy as np
import pandas as pd
import pytest

from sr.antonio import backtest_antonio


def synth1m(days=90, seed=0, vol=1.2):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-03-01", periods=days * 1440, freq="1min", tz="UTC")
    idx = idx[idx.dayofweek < 5]
    c = 15000 + np.cumsum(rng.standard_normal(len(idx)) * vol)
    o = np.r_[c[0], c[:-1]]
    w = np.abs(rng.standard_normal(len(idx))) * vol * 0.5
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + w, "low": np.minimum(o, c) - w, "close": c}, index=idx)


@pytest.mark.parametrize("tp", [1.0, 2.0, 3.0])
def test_antonio_random_walk_no_edge(tp):
    rs = []
    for s in range(3):
        tr = backtest_antonio(synth1m(seed=s), tp, cost_pts=0.0, min_risk_cost=0.0)
        if len(tr):
            rs.append(tr["gross_R"].to_numpy())
    r = np.concatenate(rs)
    assert len(r) > 50
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    assert abs(t) < 3.0, f"t={t:.2f} n={len(r)}"


def test_antonio_no_lookahead():
    df = synth1m(days=60, seed=5)
    cut = df.index[len(df) // 2]
    a = backtest_antonio(df, 2.0, 0.0, 0.0)
    b = backtest_antonio(df[df.index <= cut], 2.0, 0.0, 0.0)
    lim = cut - pd.Timedelta(days=1)
    a = a[a["exit"] < lim].reset_index(drop=True)
    b = b[b["exit"] < lim].reset_index(drop=True)
    assert len(a) > 5
    pd.testing.assert_frame_equal(a, b)


def test_antonio_max_3_per_day():
    tr = backtest_antonio(synth1m(seed=2), 2.0, 0.0, 0.0)
    d = pd.DatetimeIndex(tr["time"]).tz_convert("Europe/Lisbon").normalize()
    assert tr.groupby(d).size().max() <= 3
