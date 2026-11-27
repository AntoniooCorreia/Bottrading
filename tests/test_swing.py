import numpy as np
import pandas as pd
import pytest

from sr.swing import run_positions
from sr.swing_ideas import EXITS, IDEAS


# Ideias de calendario com datas fixas (ex.: FOMC desde 2012) precisam de velas sinteticas nesses anos e mais longas
CAL = {"l-dc96-15m-bear-vol15-s3-tp2-mh32": ("2000-01-03", 30000), "fomc-holiday-1h": ("2019-01-02", 12000), "flush-1h": ("2000-01-03", 40000), "ibs-cash-1h": ("2000-01-03", 30000),
       "rsi2-cash-1h": ("2000-01-03", 60000), "h-squeeze-1h": ("2000-01-03", 30000), "r-hi10-dd-d": ("1950-01-03", 20000), "r-hi10-dd-4h": ("1950-01-03", 40000), "r-capit-d": ("1950-01-03", 20000), "r-btc-reclaim20-d": ("1950-01-03", 20000),
       "l-rsi2-4h-bear-ema200-s2-tp1-mh6": ("2000-01-03", 12000)}


def synth_d(n=3000, seed=0, tf="1d", start="2000-01-03"):
    rng = np.random.default_rng(seed)
    if tf in ("5m", "15m") or start == "1950-01-03":   # cripto 24/7 (scalping; e ideias de crash/recuperacao com vol de cripto)
        freq = {"1d": "D", "4h": "4h"}.get(tf, tf.replace("m", "min"))
        vol = {"1d": 0.04, "4h": 0.016}.get(tf, 0.002)
        idx = pd.date_range(start, periods=n, freq=freq, tz="UTC")
        c = 10000 * np.exp(np.cumsum(rng.standard_normal(n) * vol))
        o = np.r_[c[0], c[:-1]] * (1 + rng.standard_normal(n) * 0.0003)
        h = np.maximum(o, c) * (1 + np.abs(rng.standard_normal(n)) * 0.0007)
        l = np.minimum(o, c) * (1 - np.abs(rng.standard_normal(n)) * 0.0007)
        return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)
    if tf == "1h":   # velas horarias seg-sex (ideias que dependem da hora do dia)
        idx = pd.date_range(start, periods=n * 2, freq="h", tz="America/New_York")
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
        st0, n0 = CAL.get(name, ("2000-01-03", 12000 if tf in ("5m", "15m") else 3000))
        b = synth_d(n=n0, seed=s, tf=tf, start=st0)
        tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, min_risk_cost=0.0, **EXITS.get(name, {}))
        rs.append(tr["gross_R"].to_numpy())
    r = np.concatenate(rs)
    assert len(r) > 50
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    assert abs(t) < 3.0, f"t={t:.2f}"


@pytest.mark.parametrize("name", sorted(IDEAS))
def test_swing_no_lookahead(name):
    fn, tf, st, tp, mh = IDEAS[name]
    st0, n0 = CAL.get(name, ("2000-01-03", 12000 if tf in ("5m", "15m") else 3000))
    b = synth_d(n=n0, seed=9, tf=tf, start=st0)
    cut = b.index[len(b) // 2]
    a = run_positions(b, fn(b), st, 1.0, 1.0, tp, mh, 0.0, **EXITS.get(name, {}))
    bb = b[b.index <= cut]
    c = run_positions(bb, fn(bb), st, 1.0, 1.0, tp, mh, 0.0, **EXITS.get(name, {}))
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


def test_flush_window_and_hours():
    from sr.swing_ideas import flush_1h
    b = synth_d(n=40000, seed=3, tf="1h")
    p = flush_1h(b)
    starts = p.index[(p == 1) & (p.shift(1, fill_value=0) == 0)]
    assert len(starts) > 0
    assert set(starts.hour) <= {10, 11, 12, 13, 14}
    runs = (p != p.shift()).cumsum()[p == 1]
    assert runs.value_counts().min() >= 6


def test_ibs_cash_enters_at_1500_bar():
    from sr.swing_ideas import ibs_cash_1h
    b = synth_d(n=30000, seed=4, tf="1h")
    p = ibs_cash_1h(b)
    starts = p.index[(p == 1) & (p.shift(1, fill_value=0) == 0)]
    assert len(starts) > 20
    assert set(starts.hour) == {15}


def test_rsi2_cash_enters_and_exits_at_1500_bar():
    from sr.swing_ideas import rsi2_cash_1h
    b = synth_d(n=60000, seed=5, tf="1h")
    p = rsi2_cash_1h(b)
    starts = p.index[(p == 1) & (p.shift(1, fill_value=0) == 0)]
    assert len(starts) > 20
    assert set(starts.hour) == {15}
    ends = p.index[(p == 0) & (p.shift(1, fill_value=0) == 1)]
    assert len(ends) > 20


def test_btc_bull_regime_no_lookahead():
    """O regime do BTC (media de 200 dias) so pode usar dias ja fechados: cortar os dados depois de uma data nao muda nada antes."""
    import os
    from sr.swing import load_tf
    from sr.swing_ideas import btc_bull_regime
    if not os.path.exists(os.path.join("data", "crypto", "BTCUSDT_1h.csv.gz")):
        pytest.skip("sem dados do BTC")
    d = load_tf("btc", "1d", None)
    idx = load_tf("eth", "4h", "dev").index
    full = btc_bull_regime(idx, d)
    cut = pd.Timestamp("2022-03-15", tz="UTC")
    part = btc_bull_regime(idx[idx < cut], d[d.index < cut])
    pd.testing.assert_series_equal(full[idx < cut], part)
    # o valor de um dia e o fecho do dia ANTERIOR
    day = pd.Timestamp("2021-06-10", tz="UTC")
    c = d["close"]
    exp = bool(c.loc[day - pd.Timedelta(days=1)] > c.rolling(200).mean().loc[day - pd.Timedelta(days=1)])
    assert bool(full[idx >= day].iloc[0]) == exp


def test_partial_and_breakeven_accounting():
    """Metade no alvo de 1R e resto parado em breakeven -> +0.5R bruto; so breakeven -> 0R; sem nada -> sai no sinal."""
    idx = pd.date_range("2020-01-01", periods=40, freq="D", tz="UTC")
    c = np.full(40, 100.0)
    b = pd.DataFrame({"open": c, "high": c + 1, "low": c - 1, "close": c}, index=idx)   # ATR(14) = 2
    b.iloc[20, b.columns.get_loc("high")] = 110.0     # toca +1R (risco = 3 x 2 = 6 -> alvo 106)
    b.iloc[20, b.columns.get_loc("low")] = 105.0      # sem tocar o breakeven na mesma vela
    b.iloc[22, b.columns.get_loc("low")] = 95.0       # (as velas normais ja tocam 99 < entrada 100: o resto sai na vela 21)
    pos = pd.Series(0, index=idx)
    pos.iloc[16:30] = 1                               # entra na abertura da vela 17
    tr = run_positions(b, pos, 3.0, 0.0, 0.0, 1.0, 0, 0.0, partial=0.5)
    assert abs(tr["gross_R"][0] - 0.5) < 1e-9
    tr = run_positions(b, pos, 3.0, 0.0, 0.0, 1.0, 0, 0.0, be=True)
    assert abs(tr["gross_R"][0]) < 1e-9 and tr["exit"][0] == idx[21]
    tr = run_positions(b, pos, 3.0, 0.0, 0.0, 1.0, 0, 0.0)
    assert abs(tr["gross_R"][0] - 1.0) < 1e-9


def test_signal_exit_false_ignores_signal():
    """signal_exit=False: o sinal a 0 nao fecha a trade; so o stop/alvo. Com o sinal ligado sai no sinal."""
    idx = pd.date_range("2020-01-01", periods=40, freq="D", tz="UTC")
    c = np.full(40, 100.0)
    b = pd.DataFrame({"open": c, "high": c + 1, "low": c - 1, "close": c}, index=idx)   # ATR(14) = 2, risco 6
    b.iloc[30, b.columns.get_loc("high")] = 110.0     # toca o alvo de 1R (106) na vela 30
    pos = pd.Series(0, index=idx)
    pos.iloc[16:20] = 1                               # entra na abertura da vela 17; sinal desliga no fecho da vela 20
    tr = run_positions(b, pos, 3.0, 0.0, 0.0, 1.0, 0, 0.0)
    assert tr["exit"][0] == idx[20] and abs(tr["gross_R"][0]) < 1e-9
    tr = run_positions(b, pos, 3.0, 0.0, 0.0, 1.0, 0, 0.0, signal_exit=False)
    assert len(tr) == 1 and tr["exit"][0] == idx[30] and abs(tr["gross_R"][0] - 1.0) < 1e-9


def test_lose_hold_and_exit_fn():
    """#152/#154: lose_hold so fecha trades a perder; exit_fn fecha no fecho da vela marcada. Desligados = igual ao de sempre."""
    b = synth_d(800, seed=3)
    pos = pd.Series(1, index=b.index)
    base = run_positions(b, pos, 2.0, 0.0, 0.0, 1.0, 0, 0.0, signal_exit=False)
    same = run_positions(b, pos, 2.0, 0.0, 0.0, 1.0, 0, 0.0, signal_exit=False, lose_hold=0, exit_fn=None)
    pd.testing.assert_frame_equal(base, same)
    lh = run_positions(b, pos, 2.0, 0.0, 0.0, 1.0, 0, 0.0, signal_exit=False, lose_hold=7)
    early = lh[(lh["gross_R"] > -0.999) & (lh["gross_R"] < 0.999)]
    assert len(early) > 0 and (early["gross_R"] < 0).all()      # saidas fora do alvo/stop sao so a perder
    xm = pd.Series(False, index=b.index); xm.iloc[::50] = True
    xf = run_positions(b, pos, 2.0, 0.0, 0.0, 1.0, 0, 0.0, signal_exit=False, exit_fn=lambda _b: xm)
    assert len(xf) > len(base)
    assert set(xf["exit"]) & set(b.index[::50])
