"""
Definicoes de nivel de suporte/resistencia.

Cada funcao devolve uma lista de (activo_desde, [(id, preco), ...]):
a partir do instante activo_desde, o conjunto de niveis activos passa a ser esse.
Os niveis so usam velas JA FECHADAS antes de activo_desde (sem espreitar o futuro).
Os numeros redondos sao dinamicos e tratados no motor (kind="round").
"""
from __future__ import annotations

import pandas as pd


def _trading_day(idx: pd.DatetimeIndex) -> pd.Index:
    # dia de negociacao estilo CME: comeca as 18:00 de NY
    return (idx + pd.Timedelta(hours=6)).normalize()


def prior_day_hl(m5: pd.DataFrame):
    day = _trading_day(m5.index)
    g = m5.groupby(day)
    hi, lo, first = g["high"].max(), g["low"].min(), g.apply(lambda x: x.index[0])
    out = []
    days = list(hi.index)
    for k in range(1, len(days)):
        p = days[k - 1]
        out.append((first[days[k]], [(f"pdh:{p.date()}", float(hi[p])), (f"pdl:{p.date()}", float(lo[p]))]))
    return out


def prior_week_hl(m5: pd.DataFrame):
    day = _trading_day(m5.index)
    week = day.tz_localize(None).to_period("W-FRI")
    g = m5.groupby(week)
    hi, lo = g["high"].max(), g["low"].min()
    first = pd.Series(m5.index, index=m5.index).groupby(week).first()
    out = []
    wks = list(hi.index)
    for k in range(1, len(wks)):
        p = wks[k - 1]
        out.append((first[wks[k]], [(f"pwh:{p}", float(hi[p])), (f"pwl:{p}", float(lo[p]))]))
    return out


def swing_1h(m5: pd.DataFrame, k: int = 5, keep: int = 3):
    """Topos/fundos de swing em 1h (k velas de cada lado). Confirmado k horas depois."""
    h1 = m5.resample("1h", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    hs, ls, times = h1["high"].to_numpy(), h1["low"].to_numpy(), h1.index
    highs, lows, out = [], [], []
    for i in range(k, len(h1) - k):
        changed = False
        win_h, win_l = hs[i - k:i + k + 1], ls[i - k:i + k + 1]
        if hs[i] == win_h.max():
            highs.append((f"swh:{times[i]}", float(hs[i])))
            changed = True
        if ls[i] == win_l.min():
            lows.append((f"swl:{times[i]}", float(ls[i])))
            changed = True
        if changed:
            highs, lows = highs[-keep:], lows[-keep:]
            # a vela i+k fecha no inicio da vela i+k+1
            avail = times[i + k] + pd.Timedelta(hours=1)
            out.append((avail, highs + lows))
    return out


def prior_rth_close(m5: pd.DataFrame):
    """Fecho RTH do dia anterior (fecho da ultima vela antes das 16:00 NY), activo a partir das 16:00."""
    mins = m5.index.hour * 60 + m5.index.minute
    rth = m5[(mins >= 9 * 60 + 30) & (mins < 16 * 60)]
    if len(rth) == 0:
        return []
    last = rth.groupby(rth.index.normalize()).tail(1)
    out = []
    for t, row in last.iterrows():
        out.append((t + pd.Timedelta(minutes=5), [(f"pdc:{t.date()}", float(row["close"]))]))
    return out


def overnight_hl(m5: pd.DataFrame):
    """Maxima/minima overnight (18:00 do dia anterior ate a vela das 09:25), activas a partir das 09:30."""
    idx = m5.index
    mins = idx.hour * 60 + idx.minute
    on = (mins >= 18 * 60) | (mins < 9 * 60 + 30)
    sub = m5[on]
    tday = _trading_day(sub.index)
    g = sub.groupby(tday)
    hi, lo = g["high"].max(), g["low"].min()
    out = []
    for d in hi.index:
        if hi[d] <= lo[d]:
            continue          # feriado / sem dados reais
        avail = d + pd.Timedelta(hours=9, minutes=30)
        out.append((avail, [(f"onh:{d.date()}", float(hi[d])), (f"onl:{d.date()}", float(lo[d]))]))
    return out


def nr4_day_hl(m5: pd.DataFrame):
    """Maxima/minima do dia anterior so se esse dia teve a menor amplitude dos ultimos 4 (NR4).
    Dias com amplitude 0 (feriados) ignorados. Nos outros dias o conjunto de niveis fica vazio."""
    day = _trading_day(m5.index)
    g = m5.groupby(day)
    hi, lo = g["high"].max(), g["low"].min()
    first = pd.Series(m5.index, index=m5.index).groupby(day).first()
    rng = hi - lo
    valid = [d for d in hi.index if rng[d] > 0]
    out = []
    for k in range(1, len(valid)):
        p = valid[k - 1]
        lv = []
        if k - 1 >= 3:
            last4 = [rng[valid[j]] for j in range(k - 4, k)]
            if rng[p] <= min(last4):
                lv = [(f"nr4h:{p.date()}", float(hi[p])), (f"nr4l:{p.date()}", float(lo[p]))]
        out.append((first[valid[k]], lv))
    return out


def _rth(m5: pd.DataFrame) -> pd.DataFrame:
    mins = m5.index.hour * 60 + m5.index.minute
    return m5[(mins >= 9 * 60 + 30) & (mins < 16 * 60)]


def lunch_hl(m5: pd.DataFrame):
    """Maxima/minima das velas 12:00-13:25 NY, activas das 13:30 as 16:00 do mesmo dia."""
    mins = m5.index.hour * 60 + m5.index.minute
    sub = m5[(mins >= 12 * 60) & (mins < 13 * 60 + 30)]
    g = sub.groupby(sub.index.normalize())
    hi, lo = g["high"].max(), g["low"].min()
    out = []
    for d in hi.index:
        if hi[d] > lo[d]:
            out.append((d + pd.Timedelta(hours=13, minutes=30),
                        [(f"lnh:{d.date()}", float(hi[d])), (f"lnl:{d.date()}", float(lo[d]))]))
        out.append((d + pd.Timedelta(hours=16), []))
    return out


def monday_hl(m5: pd.DataFrame):
    """Maxima/minima RTH de segunda-feira, activas de terca 09:30 ate ao fim da semana."""
    rth = _rth(m5)
    g = rth.groupby(rth.index.normalize())
    hi, lo = g["high"].max(), g["low"].min()
    out = []
    for d in hi.index:
        if d.dayofweek == 0:
            out.append((d, []))                      # limpa os niveis da semana anterior
            if hi[d] > lo[d]:
                avail = d + pd.Timedelta(days=1, hours=9, minutes=30)
                out.append((avail, [(f"mnh:{d.date()}", float(hi[d])), (f"mnl:{d.date()}", float(lo[d]))]))
    return out


LEVELS = {"pdhl": prior_day_hl, "pwhl": prior_week_hl, "swing1h": swing_1h,
          "pdc": prior_rth_close, "onhl": overnight_hl, "nr4": nr4_day_hl,
          "lunchhl": lunch_hl, "monhl": monday_hl}
