"""
Motor para ideias de prazo mais longo (15m, 1h, diario): trades de horas a dias, stops maiores.

Uma ideia e uma funcao que recebe as velas e devolve a posicao desejada (+1 long, -1 short, 0 fora) no FECHO de cada
vela, usando so informacao ate esse fecho. O motor executa na ABERTURA da vela seguinte.
  * stop de catastrofe: entrada -/+ stop_atr x ATR(14) da vela de sinal (define o R)
  * saida: sinal muda, stop tocado (se abrir para la do stop, sai na abertura), alvo opcional (tp_r), max_hold velas
  * custos em dois modelos, sempre os dois reportados:
      cfd: spread SPEC (sr/data.py) + financiamento por noite (long paga taxa+2.5%/ano, short paga 2.5%-taxa)
      fut: micro-futuros (MNQ/MES/MYM): comissao + 1 tick de slippage por lado, sem financiamento
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import TZ, load_m5

# custo ida-e-volta em pontos para micro-futuros: comissao ~1.2 USD ida-e-volta + 1 tick de slippage por lado
FUT_COST = {"nq": 1.2 / 2 + 2 * 0.25, "es": 1.2 / 5 + 2 * 0.25, "dow": 1.2 / 0.5 + 2 * 1.0}
# outros indices: sem micro-futuro simples equivalente -> usa o custo de CFD (sem financiamento)
FUT_COST.update({k: v for k, v in {"dax": 2.0, "ftse": 2.0, "nikkei": 12.0, "estx": 2.5, "cac": 2.0,
                                    "asx": 2.5, "hsi": 12.0}.items()})
CFD_MARKUP = 0.025
RF = {2018: 1.8, 2019: 2.2, 2020: 0.4, 2021: 0.1, 2022: 1.7, 2023: 5.0, 2024: 5.1, 2025: 4.2, 2026: 3.7}
TF = {"15m": "15min", "1h": "1h", "4h": "4h", "1d": "1d"}


def load_tf(key: str, tf: str, period: str | None = None) -> pd.DataFrame:
    m5 = load_m5(key, period)
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if tf == "1d":   # dia de negociacao CME (18:00 NY -> 17:00 NY)
        day = (m5.index + pd.Timedelta(hours=6)).normalize()
        out = m5.groupby(day).agg(agg)
        out.index = pd.DatetimeIndex(out.index)
        return out.dropna()
    return m5.resample(TF[tf], label="left", closed="left").agg(agg).dropna()


def atr(b: pd.DataFrame, n: int = 14) -> np.ndarray:
    h, l, c = b["high"], b["low"], b["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().to_numpy()


def run_positions(b: pd.DataFrame, pos: pd.Series, stop_atr: float, cfd_cost: float, fut_cost: float,
                  tp_r: float = 0.0, max_hold: int = 0, min_risk_cost: float = 4.0, return_open: bool = False):
    o, h, l, c = (b[k].to_numpy() for k in ("open", "high", "low", "close"))
    want = pos.reindex(b.index).fillna(0).to_numpy()
    a = atr(b)
    idx = b.index
    nyday = np.asarray(idx.tz_convert("America/New_York").normalize().asi8) if idx.tz is not None else np.asarray(idx.normalize().asi8)
    n = len(b)
    trades, cur = [], None

    def close_trade(i, px):
        nonlocal cur
        d = cur["d"]
        g = (px - cur["entry"]) * d / cur["risk"]
        nights = int(len(np.unique(nyday[cur["i"]:i + 1])) - 1)
        rf = RF.get(idx[i].year, 2.0) / 100
        rate = (rf + CFD_MARKUP) if d == 1 else (CFD_MARKUP - rf)
        fin = nights * cur["entry"] * rate / 365 / cur["risk"]
        trades.append({"time": cur["t"], "exit": idx[i], "dir": d, "gross_R": g,
                       "R": g - cfd_cost / cur["risk"] - fin, "R_fut": g - fut_cost / cur["risk"],
                       "risk_pts": cur["risk"], "nights": nights, "play": "swing", "level": ""})
        cur = None

    for i in range(1, n):
        # 1) gerir posicao aberta durante a vela i
        if cur is not None:
            d, st = cur["d"], cur["stop"]
            if (d == 1 and o[i] <= st) or (d == -1 and o[i] >= st):
                close_trade(i, o[i])
            elif (d == 1 and l[i] <= st) or (d == -1 and h[i] >= st):
                close_trade(i, st)
            elif tp_r > 0 and ((d == 1 and h[i] >= cur["tp"]) or (d == -1 and l[i] <= cur["tp"])):
                close_trade(i, cur["tp"])
        # 2) sinal no fecho da vela i: sair no fecho, entrar na abertura de i+1
        if i + 1 >= n:
            break
        w = int(np.sign(want[i]))
        if cur is not None:
            held = i - cur["i"]
            if w != cur["d"] or (max_hold and held >= max_hold):
                close_trade(i, c[i])   # sai no fecho da vela i (~ abertura da seguinte)
        if cur is None and w != 0 and np.isfinite(a[i]) and a[i] > 0:
            entry = o[i + 1]
            risk = stop_atr * a[i]
            if risk >= min_risk_cost * cfd_cost:
                cur = {"d": w, "entry": entry, "stop": entry - w * risk, "risk": risk,
                       "tp": entry + w * tp_r * risk, "i": i + 1, "t": idx[i + 1]}
                # a posicao so vive a partir da vela i+1: gerida na proxima iteracao
    if return_open:   # usado pelo bot da demo: devolve a trade ainda aberta no fim (sem a fechar)
        return pd.DataFrame(trades), (dict(cur) if cur is not None else None)
    if cur is not None:
        close_trade(n - 1, c[n - 1])
    return pd.DataFrame(trades)
