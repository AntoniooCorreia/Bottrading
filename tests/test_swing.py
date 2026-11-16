import numpy as np
import pandas as pd
import pytest

from sr.swing import run_positions
from sr.swing_ideas import IDEAS


def synth_d(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2000-01-03", periods=n, tz="America/New_York")
    c = 10000 * np.exp(np.cumsum(rng.standard_normal(n) * 0.012))
    o = np.r_[c[0], c[:-1]] * (1 + rng.standard_normal(n) * 0.002)
    h = np.maximum(o, c) * (1 + np.abs(rng.standard_normal(n)) * 0.004)
    l = np.minimum(o, c) * (1 - np.abs(rng.standard_normal(n)) * 0.004)
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


@pytest.mark.parametrize("name", sorted(IDEAS))
def test_swing_random_walk_no_edge(name):
    fn, tf, st, tp, mh = IDEAS[name]
    rs = []
    for s in range(6):
        b = synth_d(seed=s)
        tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, min_risk_cost=0.0)
        rs.append(tr["gross_R"].to_numpy())
    r = np.concatenate(rs)
    assert len(r) > 50
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    assert abs(t) < 3.0, f"t={t:.2f}"


@pytest.mark.parametrize("name", sorted(IDEAS))
def test_swing_no_lookahead(name):
    fn, tf, st, tp, mh = IDEAS[name]
    b = synth_d(seed=9)
    cut = b.index[len(b) // 2]
    a = run_positions(b, fn(b), st, 1.0, 1.0, tp, mh, 0.0)
    bb = b[b.index <= cut]
    c = run_positions(bb, fn(bb), st, 1.0, 1.0, tp, mh, 0.0)
    lim = cut - pd.Timedelta(days=5)
    a, c = a[a["exit"] < lim].reset_index(drop=True), c[c["exit"] < lim].reset_index(drop=True)
    assert len(a) > 3
    pd.testing.assert_frame_equal(a, c)
