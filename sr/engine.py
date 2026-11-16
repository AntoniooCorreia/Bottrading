"""
Motor de backtest de suporte e resistencia em velas de 5m.

Jogadas:
  bounce : ordem limite NO nivel (compra no suporte / vende na resistencia), stop a stop_atr*ATR para la do nivel
  break  : vela de 5m fecha para la do nivel -> entra na abertura seguinte a favor da rutura, stop do outro lado do nivel
  fake   : preco passa o nivel em >= fake_atr*ATR mas a vela fecha de volta -> entra contra, stop no extremo da vela
  gapfill: (so com niveis pdc) na abertura da vela das 09:30, se GAP_MIN <= |abertura - pdc|/pdc <= GAP_MAX,
           entra contra o gap; alvo = pdc, stop = mesma distancia do outro lado (1R). Ignora tp_r e stop_atr.

Regras comuns (conservadoras):
  * cada nivel so dispara uma vez (1o toque); numeros redondos: 1 vez por dia
  * 1 posicao de cada vez; flat no fim da sessao
  * se stop e TP cabem na mesma vela conta como STOP; na vela de entrada por limite so se verifica o stop
  * ATR(14) de 5m calculado so com velas fechadas
  * custo ida-e-volta em pontos convertido em R e descontado em todas as trades
  * trades com risco < min_risk_cost * custo sao ignoradas (o custo comeria o R)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from .levels import LEVELS


@dataclass
class Variant:
    play: str = "bounce"          # bounce | break | fake | gapfill
    levels: str = "pdhl"          # pdhl | pwhl | swing1h | round | pdc | onhl | nr4
    tp_r: float = 2.0
    stop_atr: float = 0.5
    fake_atr: float = 0.3
    session: str = "rth"          # rth (09:30-16:00 NY) | all
    min_risk_cost: float = 4.0

    def name(self) -> str:
        return (f"{self.play}-{self.levels}-tp{self.tp_r:g}-sl{self.stop_atr:g}"
                + (f"-fk{self.fake_atr:g}" if self.play == "fake" else "") + f"-{self.session}")

    def to_dict(self) -> dict:
        return asdict(self)


GAP_MIN, GAP_MAX = 0.001, 0.006     # gapfill: gap entre 0.10% e 0.60% do pdc (fixo, pre-registado)


def atr14(m5: pd.DataFrame) -> np.ndarray:
    h, l, c = m5["high"], m5["low"], m5["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean().shift(1).to_numpy()      # so velas fechadas


def session_masks(idx: pd.DatetimeIndex, session: str):
    mins = idx.hour * 60 + idx.minute
    if session == "rth":
        can_enter = (mins >= 9 * 60 + 30) & (mins < 15 * 60 + 55)
        in_sess = (mins >= 9 * 60 + 30) & (mins < 16 * 60)
        key = idx.normalize()
    else:
        trading_day = (idx + pd.Timedelta(hours=6)).normalize()
        can_enter = ~((mins >= 16 * 60 + 50) & (mins < 18 * 60))
        in_sess = np.ones(len(idx), bool)
        key = trading_day
    key = np.asarray(key.asi8)
    last = np.ones(len(idx), bool)
    last[:-1] = key[:-1] != key[1:]
    # ultima vela da sessao = ultima vela dentro da sessao antes de sair dela
    nxt_in = np.append(np.asarray(in_sess)[1:], False)
    last_in_sess = np.asarray(in_sess) & (last | ~nxt_in)
    return np.asarray(can_enter), np.asarray(in_sess), last_in_sess, key


def backtest(m5: pd.DataFrame, v: Variant, cost_pts: float, round_step: float) -> pd.DataFrame:
    o, h, l, c = (m5[k].to_numpy() for k in ("open", "high", "low", "close"))
    idx = m5.index
    n = len(m5)
    atr = atr14(m5)
    can_enter, in_sess, last_in_sess, daykey = session_masks(idx, v.session)

    if v.levels == "round":
        events = []
    else:
        events = LEVELS[v.levels](m5)
    ev_t = np.array([pd.Timestamp(e[0]).as_unit("ns").value for e in events], dtype=np.int64) if events else np.array([], np.int64)
    times = idx.as_unit("ns").asi8
    ev_ptr, active = 0, []
    used: set = set()
    trades = []
    pos = None            # dict
    pending = None        # (dir, stop, play, lvl_id)

    for i in range(1, n):
        while ev_ptr < len(ev_t) and ev_t[ev_ptr] <= times[i]:
            active = events[ev_ptr][1]
            ev_ptr += 1

        # 1) entrada pendente na abertura
        if pending is not None:
            d, stop, play, lid = pending
            pending = None
            entry = o[i]
            risk = (entry - stop) * d
            if in_sess[i] and risk > 0 and risk >= v.min_risk_cost * cost_pts:
                pos = {"d": d, "entry": entry, "stop": stop, "tp": entry + d * v.tp_r * risk,
                       "risk": risk, "t": idx[i], "play": play, "lvl": lid, "fresh": False}

        # 2) gerir posicao aberta
        if pos is not None:
            d, r = pos["d"], None
            if (d == 1 and l[i] <= pos["stop"]) or (d == -1 and h[i] >= pos["stop"]):
                r = -1.0
            elif not pos["fresh"] and ((d == 1 and h[i] >= pos["tp"]) or (d == -1 and l[i] <= pos["tp"])):
                r = pos.get("tp_r", v.tp_r)
            elif last_in_sess[i] or not in_sess[i]:
                r = (c[i] - pos["entry"]) * d / pos["risk"]
            pos["fresh"] = False
            if r is not None:
                trades.append({"time": pos["t"], "exit": idx[i], "dir": d, "R": r - cost_pts / pos["risk"],
                               "gross_R": r, "risk_pts": pos["risk"], "play": pos["play"], "level": pos["lvl"]})
                pos = None
            continue

        # 3) procurar sinal
        if not can_enter[i] or last_in_sess[i] or not np.isfinite(atr[i]) or atr[i] <= 0:
            continue
        if v.levels == "round":
            base = np.floor(c[i - 1] / round_step) * round_step
            lv = [(f"rn:{base}:{daykey[i]}", base), (f"rn:{base + round_step}:{daykey[i]}", base + round_step)]
        else:
            lv = active
        a = atr[i]
        if v.play == "gapfill":
            if idx[i].hour != 9 or idx[i].minute != 30:
                continue
            for lid, L in lv:
                if lid in used or L <= 0:
                    continue
                used.add(lid)
                gap = o[i] - L
                if not (GAP_MIN <= abs(gap) / L <= GAP_MAX):
                    break
                d = -1 if gap > 0 else 1
                entry, risk = o[i], abs(gap)
                if risk < v.min_risk_cost * cost_pts:
                    break
                pos = {"d": d, "entry": entry, "stop": entry - d * risk, "tp": L, "risk": risk,
                       "t": idx[i], "play": "gapfill", "lvl": lid, "fresh": False, "tp_r": 1.0}
                # na vela de entrada: stop e alvo na mesma vela conta como stop
                hit_s = (d == 1 and l[i] <= pos["stop"]) or (d == -1 and h[i] >= pos["stop"])
                hit_t = (d == 1 and h[i] >= L) or (d == -1 and l[i] <= L)
                if hit_s or hit_t:
                    rr = -1.0 if hit_s else 1.0
                    trades.append({"time": idx[i], "exit": idx[i], "dir": d, "R": rr - cost_pts / risk,
                                   "gross_R": rr, "risk_pts": risk, "play": "gapfill", "level": lid})
                    pos = None
                break
            continue
        for lid, L in lv:
            if lid in used:
                continue
            pc = c[i - 1]
            if v.play == "bounce":
                if pc > L and l[i] <= L:            # toca suporte por cima -> long
                    d = 1
                elif pc < L and h[i] >= L:          # toca resistencia por baixo -> short
                    d = -1
                else:
                    continue
                used.add(lid)
                entry = min(o[i], L) if d == 1 else max(o[i], L)
                stop = L - d * v.stop_atr * a
                risk = (entry - stop) * d
                if risk <= 0 or risk < v.min_risk_cost * cost_pts:
                    break
                pos = {"d": d, "entry": entry, "stop": stop, "tp": entry + d * v.tp_r * risk, "risk": risk,
                       "t": idx[i], "play": "bounce", "lvl": lid, "fresh": False}
                # na propria vela so o stop conta
                if (d == 1 and l[i] <= stop) or (d == -1 and h[i] >= stop):
                    trades.append({"time": idx[i], "exit": idx[i], "dir": d, "R": -1.0 - cost_pts / risk,
                                   "gross_R": -1.0, "risk_pts": risk, "play": "bounce", "level": lid})
                    pos = None
                break
            if v.play == "break":
                if pc <= L < c[i]:
                    d = 1
                elif pc >= L > c[i]:
                    d = -1
                else:
                    continue
                used.add(lid)
                pending = (d, L - d * v.stop_atr * a, "break", lid)
                break
            if v.play == "fake":
                if pc < L and h[i] >= L + v.fake_atr * a and c[i] < L:
                    used.add(lid)
                    pending = (-1, max(h[i], L) + 0.1 * a, "fake", lid)
                    break
                if pc > L and l[i] <= L - v.fake_atr * a and c[i] > L:
                    used.add(lid)
                    pending = (1, min(l[i], L) - 0.1 * a, "fake", lid)
                    break
    return pd.DataFrame(trades)
