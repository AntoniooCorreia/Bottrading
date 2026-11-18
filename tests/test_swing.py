import numpy as np
import pandas as pd
import pytest

from sr.swing import run_positions
from sr.swing_ideas import IDEAS


def synth_d(n=3000, seed=0, tf="1d"):
    rng = np.random.default_rng(seed)
    if tf == "1h":   # velas horarias seg-sex (ideias que dependem da hora do dia)
        idx = pd.date_range("2000-01-03", periods=n * 2, freq="h", tz="America/New_York")
        idx = idx[idx.dayofweek < 5][:n]
    else:
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
        b = synth_d(seed=s, tf=tf)
        tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, min_risk_cost=0.0)
        rs.append(tr["gross_R"].to_numpy())
    r = np.concatenate(rs)
    assert len(r) > 50
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    assert abs(t) < 3.0, f"t={t:.2f}"


@pytest.mark.parametrize("name", sorted(IDEAS))
def test_swing_no_lookahead(name):
    fn, tf, st, tp, mh = IDEAS[name]
    b = synth_d(seed=9, tf=tf)
    cut = b.index[len(b) // 2]
    a = run_positions(b, fn(b), st, 1.0, 1.0, tp, mh, 0.0)
    bb = b[b.index <= cut]
    c = run_positions(bb, fn(bb), st, 1.0, 1.0, tp, mh, 0.0)
    lim = cut - pd.Timedelta(days=5)
    a, c = a[a["exit"] < lim].reset_index(drop=True), c[c["exit"] < lim].reset_index(drop=True)
    assert len(a) > 3
    pd.testing.assert_frame_equal(a, c)


def test_overnight_us_hours():
    from sr.swing_ideas import overnight_us_1h
    b = synth_d(n=200, seed=1, tf="1h")
    tr = run_positions(b, overnight_us_1h(b), 3.0, 0.0, 0.0, 0.0, 24, 0.0)
    ok = tr[tr["exit"] < b.index[-1]]
    assert len(ok) > 3
    h = pd.DatetimeIndex(ok["time"]).hour
    # entra as 16:00; so volta a entrar a outra hora se o stop for tocado a meio da noite (regra comum do motor)
    assert (h == 16).mean() > 0.8 and set(h) <= set(range(16, 24)) | set(range(0, 8))
    assert set(pd.DatetimeIndex(ok["exit"]).hour) <= {8} | set(range(16, 24)) | set(range(0, 8))


def test_tom_window():
    from sr.swing_ideas import tom_d
    b = synth_d(n=300, seed=2)
    tr = run_positions(b, tom_d(b), 30.0, 0.0, 0.0, 0.0, 6, 0.0)
    t0 = pd.DatetimeIndex(tr["time"])
    # entra no ultimo dia util do mes
    assert all((t + pd.offsets.BDay(1)).month != t.month for t in t0)
    # sai no fecho do 3.o dia util do mes seguinte
    for t in pd.DatetimeIndex(tr["exit"])[:-1]:
        assert len(pd.bdate_range(t.replace(day=1).tz_localize(None), t.tz_localize(None))) == 3


def test_rsi2_pop_short_only_short():
    from sr.swing_ideas import rsi2_pop_short_4h
    b = synth_d(n=3000, seed=2)
    p = rsi2_pop_short_4h(b)
    assert set(p.unique()) <= {0, -1} and (p == -1).sum() > 50


def test_keyrev_signal_rule():
    from sr.swing_ideas import keyrev_d, _weekdays
    b = synth_d(n=1500, seed=3)
    p = keyrev_d(b)
    assert set(p.unique()) <= {0, 1} and (p == 1).sum() > 0
    w = _weekdays(b)
    c = w["close"]
    sig = (w["low"] < w["low"].shift(1).rolling(10).min()) & (c > c.shift(1))
    # cada dia com sinal fica em posicao no fecho; sem sinal nos ultimos 5 dias -> fora
    pw = p.reindex(w.index)
    assert (pw[sig] == 1).all()
    recent = sig.astype(int).rolling(5, min_periods=1).max()
    assert ((pw == 1) == (recent == 1)).all()
