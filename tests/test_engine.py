import numpy as np
import pandas as pd
import pytest

from sr.engine import Variant, backtest

TZ = "America/New_York"


def synth(days=260, seed=0, vol=3.0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-04 00:00", periods=days * 288, freq="5min", tz=TZ)
    idx = idx[idx.dayofweek < 5]
    steps = rng.standard_normal(len(idx)) * vol
    c = 15000 + np.cumsum(steps)
    o = np.r_[c[0], c[:-1]]
    wig = np.abs(rng.standard_normal(len(idx))) * vol * 0.6
    h = np.maximum(o, c) + wig
    l = np.minimum(o, c) - wig
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


VARIANTS = [Variant(play=p, levels=lv) for p in ("bounce", "break", "fake") for lv in ("pdhl", "swing1h", "round")]
# ideias do agente (2026-11-16)
VARIANTS += [Variant(play="gapfill", levels="pdc"), Variant(play="fake", levels="onhl"),
             Variant(play="break", levels="nr4")]


@pytest.mark.parametrize("v", VARIANTS, ids=lambda v: v.name())
def test_random_walk_has_no_edge(v):
    """Num passeio aleatorio, sem custos, nao pode haver edge (senao ha batota/bug)."""
    rs = []
    for seed in range(3):
        tr = backtest(synth(seed=seed), v, cost_pts=0.0, round_step=50.0)
        if len(tr):
            rs.append(tr["gross_R"].to_numpy())
    r = np.concatenate(rs)
    assert len(r) > 50
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    assert abs(t) < 3.0, f"t={t:.2f} n={len(r)}"


@pytest.mark.parametrize("v", VARIANTS, ids=lambda v: v.name())
def test_no_lookahead(v):
    """Trades que fecham antes do corte nao podem mudar quando se apagam os dados depois do corte."""
    df = synth(days=120, seed=7)
    cut = df.index[len(df) // 2]
    full = backtest(df, v, 0.0, 50.0)
    part = backtest(df[df.index <= cut], v, 0.0, 50.0)
    a = full[full["exit"] < cut - pd.Timedelta(days=1)].reset_index(drop=True)
    b = part[part["exit"] < cut - pd.Timedelta(days=1)].reset_index(drop=True)
    assert len(a) > 5
    pd.testing.assert_frame_equal(a, b)


def test_costs_reduce_r():
    v = Variant(play="bounce", levels="pdhl")
    df = synth(seed=1)
    a = backtest(df, v, 0.0, 50.0)
    b = backtest(df, v, 0.2, 50.0)
    assert len(a) > 20 and len(b) > 20
    assert b["R"].mean() < a["R"].mean()


def test_gapfill_fills_gap_up():
    """Gap para cima de 0.3% que fecha durante a manha -> short com +1R bruto."""
    idx = pd.date_range("2021-01-04 09:30", "2021-01-05 16:00", freq="5min", tz=TZ)
    df = pd.DataFrame({"open": 1000.0, "high": 1000.5, "low": 999.5, "close": 1000.0}, index=idx)
    d2 = idx >= pd.Timestamp("2021-01-04 16:00", tz=TZ)
    df.loc[d2, ["open", "high", "low", "close"]] = [1003.0, 1003.5, 1002.5, 1003.0]
    t = pd.Timestamp("2021-01-05 10:30", tz=TZ)
    df.loc[t, "low"] = 999.0
    tr = backtest(df, Variant(play="gapfill", levels="pdc"), 0.0, 50.0)
    assert len(tr) == 1
    assert tr.iloc[0]["dir"] == -1 and tr.iloc[0]["gross_R"] == 1.0
    assert tr.iloc[0]["exit"] == t
