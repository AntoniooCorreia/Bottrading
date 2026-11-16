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


LEVELS = {"pdhl": prior_day_hl, "pwhl": prior_week_hl, "swing1h": swing_1h}
