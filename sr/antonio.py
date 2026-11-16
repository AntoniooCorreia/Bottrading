"""
Setup do Antonio (pre-registado por ele em 2026-11-16), em velas de 1m.

Niveis de suporte/resistencia (so com velas ja fechadas):
  * maximo/minimo do dia anterior e da semana anterior (dia de negociacao CME, comeca as 18:00 NY)
  * maximo/minimo da sessao asiatica (00:00-06:00 Lisboa) e de Londres (07:00-12:00 Lisboa), depois de fecharem
  * topos/fundos de swing de 1h (5 velas de cada lado), ultimos 3 de cada lado
  * FVG por preencher em 15m, 30m e 1h (ultimos 3 de cada lado por timeframe, max 5 dias)
Entrada (long; short e o espelho):
  1. o preco toca/fura um suporte vindo de cima (low <= nivel, fecho anterior acima) -> "armado" durante 30 velas
  2. FVG bearish de 1m formados desde 15 velas antes do toque sao guardados
  3. vela de displacement: altista, corpo >= 2x a media dos corpos das 20 velas anteriores, e fecha acima do topo
     de um desses FVG (inversao = IFVG)
  4. ordem limite no topo do IFVG (reteste), valida 20 velas; stop no extremo do sweep
Gestao: alvo tp_r * R; se tp_r > 1 o stop passa para break-even quando o preco chega a +1R.
Sessoes de entrada (Lisboa): Asia 01:00-05:00, Londres 08:00-10:00, NY 14:30-17:00. Asia fecha tudo as 07:59,
Londres/NY as 21:00. Maximo 3 trades por dia (Lisboa). Cada nivel so dispara uma vez.
Conservador: na vela de entrada so conta o stop; stop e alvo na mesma vela = stop.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LIS = "Europe/Lisbon"


def _trading_day(idx):
    return (idx.tz_convert("America/New_York") + pd.Timedelta(hours=6)).normalize()


def _resample(m1, rule):
    return m1.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def level_events(m1: pd.DataFrame) -> list:
    """Lista de (instante_ns, tipo, payload). tipo: 'set:<grupo>' substitui os niveis desse grupo."""
    ev = []
    # dia / semana anteriores
    day = _trading_day(m1.index)
    g = m1.groupby(day)
    hi, lo = g["high"].max(), g["low"].min()
    first = pd.Series(m1.index, index=m1.index).groupby(day).first()
    days = list(hi.index)
    for k in range(1, len(days)):
        p = days[k - 1]
        ev.append((first[days[k]].value, "set:pd", [(f"pdh{p.date()}", float(hi[p]), -1), (f"pdl{p.date()}", float(lo[p]), 1)]))
    wk = day.tz_localize(None).to_period("W-FRI")
    gw = m1.groupby(wk)
    whi, wlo = gw["high"].max(), gw["low"].min()
    wfirst = pd.Series(m1.index, index=m1.index).groupby(wk).first()
    wks = list(whi.index)
    for k in range(1, len(wks)):
        p = wks[k - 1]
        ev.append((wfirst[wks[k]].value, "set:pw", [(f"pwh{p}", float(whi[p]), -1), (f"pwl{p}", float(wlo[p]), 1)]))
    # sessoes asia / londres (hora de Lisboa)
    loc = m1.index.tz_convert(LIS)
    mins = loc.hour * 60 + loc.minute
    dkey = loc.normalize()
    for name, a, b in (("as", 0, 6 * 60), ("ld", 7 * 60, 12 * 60)):
        msk = (mins >= a) & (mins < b)
        sub = m1[msk]
        if not len(sub):
            continue
        gs = sub.groupby(dkey[msk])
        shi, slo = gs["high"].max(), gs["low"].min()
        for d in shi.index:
            avail = (d + pd.Timedelta(minutes=b)).tz_convert("UTC")
            ev.append((avail.value, f"set:{name}", [(f"{name}h{d.date()}", float(shi[d]), -1), (f"{name}l{d.date()}", float(slo[d]), 1)]))
    # swings 1h
    h1 = _resample(m1, "1h")
    hs, ls, t1 = h1["high"].to_numpy(), h1["low"].to_numpy(), h1.index
    sh, sl = [], []
    for i in range(5, len(h1) - 5):
        ch = False
        if hs[i] == hs[i - 5:i + 6].max():
            sh = (sh + [(f"swh{t1[i]}", float(hs[i]), -1)])[-3:]
            ch = True
        if ls[i] == ls[i - 5:i + 6].min():
            sl = (sl + [(f"swl{t1[i]}", float(ls[i]), 1)])[-3:]
            ch = True
        if ch:
            ev.append(((t1[i + 5] + pd.Timedelta(hours=1)).value, "set:sw", sh + sl))
    # FVG em 15m/30m/1h: (instante, 'fvg', (id, baixo, cima, lado, tf_minutos))
    for rule, tfm in (("15min", 15), ("30min", 30), ("1h", 60)):
        b = _resample(m1, rule)
        bh, bl, bt = b["high"].to_numpy(), b["low"].to_numpy(), b.index
        for i in range(2, len(b)):
            avail = (bt[i] + pd.Timedelta(minutes=tfm)).value
            if bl[i] > bh[i - 2]:      # bullish -> suporte
                ev.append((avail, "fvg", (f"fu{tfm}{bt[i]}", float(bh[i - 2]), float(bl[i]), 1)))
            elif bh[i] < bl[i - 2]:    # bearish -> resistencia
                ev.append((avail, "fvg", (f"fd{tfm}{bt[i]}", float(bh[i]), float(bl[i - 2]), -1)))
    ev.sort(key=lambda e: e[0])
    return ev


def sessions(idx: pd.DatetimeIndex):
    loc = idx.tz_convert(LIS)
    m = np.asarray(loc.hour * 60 + loc.minute)
    asia = (m >= 60) & (m < 300)
    london = (m >= 480) & (m < 600)
    ny = (m >= 870) & (m < 1020)
    can = asia | london | ny
    # fim forcado: asia as 07:59, resto as 21:00
    flat_asia = m >= 479
    flat_day = m >= 1260
    day = np.asarray(loc.normalize().asi8)
    return can, asia, flat_asia, flat_day, day


def backtest_antonio(m1: pd.DataFrame, tp_r: float, cost_pts: float, min_risk_cost: float = 4.0,
                     max_per_day: int = 3) -> pd.DataFrame:
    o, h, l, c = (m1[k].to_numpy() for k in ("open", "high", "low", "close"))
    idx = m1.index
    times = idx.as_unit("ns").asi8
    n = len(m1)
    body = np.abs(c - o)
    avg_body = pd.Series(body).rolling(20).mean().shift(1).to_numpy()
    can, asia_ses, flat_asia, flat_day, day = sessions(idx)
    events = level_events(m1)
    ep = 0
    groups = {}            # grupo -> lista de (id, preco, lado)
    fvgs = []              # (id, baixo, cima, lado, t_ns)
    used = set()
    trades = []
    per_day = {}
    armed = {1: None, -1: None}      # lado -> dict
    small = []                       # FVG de 1m recentes: (i, baixo, cima, lado)
    pend = None
    pos = None
    five_days = 5 * 86400 * 10 ** 9

    for i in range(2, n):
        t = times[i]
        while ep < len(events) and events[ep][0] <= t:
            _, kind, pay = events[ep]
            if kind == "fvg":
                fvgs.append((*pay, events[ep][0]))
            else:
                groups[kind] = pay
            ep += 1
        # FVG de 1m (vela i-1 acabou de fechar: usa i-3..i-1)
        if h[i - 1] < l[i - 3] if i >= 3 else False:
            small.append((i - 1, h[i - 1], l[i - 3], -1))
        elif (l[i - 1] > h[i - 3]) if i >= 3 else False:
            small.append((i - 1, h[i - 3], l[i - 1], 1))
        if len(small) > 60:
            small = small[-60:]

        # gerir posicao
        if pos is not None:
            d = pos["d"]
            r = None
            if (d == 1 and l[i] <= pos["stop"]) or (d == -1 and h[i] >= pos["stop"]):
                r = (pos["stop"] - pos["entry"]) * d / pos["risk"]
            elif (d == 1 and h[i] >= pos["tp"]) or (d == -1 and l[i] <= pos["tp"]):
                r = tp_r
            elif (pos["asia"] and flat_asia[i] and not asia_ses[i]) or flat_day[i]:
                r = (c[i] - pos["entry"]) * d / pos["risk"]
            if r is not None:
                trades.append({"time": pos["t"], "exit": idx[i], "dir": d, "R": r - cost_pts / pos["risk"],
                               "gross_R": r, "risk_pts": pos["risk"], "play": "antonio", "level": pos["lvl"]})
                pos = None
            else:
                if tp_r > 1 and not pos["be"] and ((d == 1 and h[i] >= pos["entry"] + pos["risk"]) or
                                                  (d == -1 and l[i] <= pos["entry"] - pos["risk"])):
                    pos["stop"], pos["be"] = pos["entry"], True
            continue

        # ordem limite pendente
        if pend is not None:
            if i > pend["until"] or not can[i]:
                pend = None
            elif (pend["d"] == 1 and l[i] <= pend["entry"]) or (pend["d"] == -1 and h[i] >= pend["entry"]):
                d = pend["d"]
                entry = min(o[i], pend["entry"]) if d == 1 else max(o[i], pend["entry"])
                risk = (entry - pend["stop"]) * d
                pend = None
                if risk > 0 and risk >= min_risk_cost * cost_pts:
                    per_day[day[i]] = per_day.get(day[i], 0) + 1
                    pos = {"d": d, "entry": entry, "stop": entry - d * risk, "tp": entry + d * tp_r * risk, "risk": risk,
                           "t": idx[i], "lvl": pend_lvl, "be": False, "asia": bool(asia_ses[i])}
                    if (d == 1 and l[i] <= pos["stop"]) or (d == -1 and h[i] >= pos["stop"]):
                        trades.append({"time": idx[i], "exit": idx[i], "dir": d, "R": -1.0 - cost_pts / risk,
                                       "gross_R": -1.0, "risk_pts": risk, "play": "antonio", "level": pos["lvl"]})
                        pos = None
                continue
            else:
                continue

        if not can[i] or per_day.get(day[i], 0) >= max_per_day:
            armed = {1: None, -1: None}
            continue

        # niveis ativos (linhas + FVG por preencher)
        fvgs = [f for f in fvgs if t - f[4] <= five_days and not (f[3] == 1 and c[i - 1] < f[1]) and not (f[3] == -1 and c[i - 1] > f[2])]
        lv = [x for g in groups.values() for x in g]
        pc = c[i - 1]
        # armar
        for lid, price, side in lv:
            if lid in used:
                continue
            if side == 1 and pc > price and l[i] <= price and armed[1] is None:
                armed[1] = {"lvl": lid, "ext": l[i], "i": i}
                used.add(lid)
            elif side == -1 and pc < price and h[i] >= price and armed[-1] is None:
                armed[-1] = {"lvl": lid, "ext": h[i], "i": i}
                used.add(lid)
        for f in fvgs:
            lid, lo_, hi_, side, _ = f
            if lid in used:
                continue
            if side == 1 and pc > hi_ and l[i] <= hi_ and armed[1] is None:
                armed[1] = {"lvl": lid, "ext": l[i], "i": i}
                used.add(lid)
            elif side == -1 and pc < lo_ and h[i] >= lo_ and armed[-1] is None:
                armed[-1] = {"lvl": lid, "ext": h[i], "i": i}
                used.add(lid)
        # displacement + IFVG
        for d in (1, -1):
            a = armed[d]
            if a is None:
                continue
            if i - a["i"] > 30:
                armed[d] = None
                continue
            a["ext"] = min(a["ext"], l[i]) if d == 1 else max(a["ext"], h[i])
            if not np.isfinite(avg_body[i]) or avg_body[i] <= 0:
                continue
            disp = (c[i] - o[i]) * d >= 2.0 * avg_body[i]
            if not disp:
                continue
            cand = [s for s in small if s[3] == -d and s[0] >= a["i"] - 15 and s[0] < i]
            hit = None
            for s in reversed(cand):
                if (d == 1 and c[i] > s[2]) or (d == -1 and c[i] < s[1]):
                    hit = s
                    break
            if hit is None:
                continue
            entry = hit[2] if d == 1 else hit[1]
            stop = a["ext"]
            if (entry - stop) * d <= 0:
                continue
            pend = {"d": d, "entry": entry, "stop": stop, "until": i + 20}
            pend_lvl = a["lvl"]
            armed = {1: None, -1: None}
            break
    return pd.DataFrame(trades)
