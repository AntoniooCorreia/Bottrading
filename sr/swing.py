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


CRYPTO = {"btc": "BTCUSDT", "eth": "ETHUSDT", "sol": "SOLUSDT",
          # moedas de confirmacao (detetor de sorte): um edge real deve aparecer na maioria delas
          "xrp": "XRPUSDT", "ada": "ADAUSDT", "doge": "DOGEUSDT", "link": "LINKUSDT", "avax": "AVAXUSDT"}
MAIN_COINS = ("btc", "eth", "sol")
CONFIRM_COINS = ("xrp", "ada", "doge", "link", "avax")
KRAKEN_FEE = 0.0026          # taker spot da Kraken por lado (0.26%); ida-e-volta = 0.52% do preco + 0.05% slippage


def load_crypto(key: str, period: str | None = None) -> pd.DataFrame:
    import os
    from .data import PERIODS
    df = pd.read_csv(os.path.join("data", "crypto", f"{CRYPTO[key]}_1h.csv.gz"))
    idx = pd.DatetimeIndex(pd.to_datetime(df["ts"], unit="ms", utc=True))
    out = df[["open", "high", "low", "close"]].astype(float).set_index(idx)
    if period:
        a, b = PERIODS[period]
        a = "2017-01-01" if period == "pre" else a       # crypto: 'pre' = 2017-2018 (antes nao ha dados)
        out = out[(out.index >= pd.Timestamp(a, tz="UTC")) & (out.index < pd.Timestamp(b, tz="UTC") + pd.Timedelta(days=1))]
    return out


def load_tf(key: str, tf: str, period: str | None = None) -> pd.DataFrame:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if key in CRYPTO:
        h1 = load_crypto(key, period)
        return h1 if tf == "1h" else h1.resample({"4h": "4h", "1d": "1D", "15m": "15min"}[tf], label="left",
                                                  closed="left").agg(agg).dropna()
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
                  tp_r: float = 0.0, max_hold: int = 0, min_risk_cost: float = 4.0,
                  cost_pct: float = 0.0, financing: bool = True, return_open: bool = False,
                  partial: float = 0.0, be: bool = False):
    """partial > 0 (com tp_r > 0): fecha essa fracao no alvo e o resto continua (stop do resto em breakeven se be=True).
    be=True sem partial e com tp_r > 0: nao fecha nada no alvo, so passa o stop para breakeven quando toca o alvo.
    Breakeven = entrada x (1 + cost_pct) (o resto ja nao perde depois de custos). Sem partial/be: igual ao de sempre."""
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
        if cur.get("done") is not None:        # parte ja fechada no alvo
            g = cur["frac"] * cur["done"] + (1 - cur["frac"]) * g
        nights = int(len(np.unique(nyday[cur["i"]:i + 1])) - 1)
        rf = RF.get(idx[i].year, 2.0) / 100
        rate = (rf + CFD_MARKUP) if d == 1 else (CFD_MARKUP - rf)
        fin = nights * cur["entry"] * rate / 365 / cur["risk"] if financing else 0.0
        pc = cur["entry"] * cost_pct / cur["risk"]
        trades.append({"time": cur["t"], "exit": idx[i], "dir": d, "gross_R": g,
                       "R": g - cfd_cost / cur["risk"] - fin - pc, "R_fut": g - fut_cost / cur["risk"] - pc,
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
            elif tp_r > 0 and not cur.get("hit") and ((d == 1 and h[i] >= cur["tp"]) or (d == -1 and l[i] <= cur["tp"])):
                if partial > 0 or be:
                    cur["hit"] = True
                    if partial > 0:
                        cur["done"], cur["frac"] = tp_r, partial
                    if be or partial > 0:
                        bel = cur["entry"] * (1 + d * cost_pct)
                        cur["stop"] = bel
                        if (d == 1 and l[i] <= bel) or (d == -1 and h[i] >= bel):   # conservador: tocou os dois na mesma vela
                            close_trade(i, bel)
                else:
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
            if risk >= min_risk_cost * cfd_cost and risk >= min_risk_cost * entry * cost_pct:
                cur = {"d": w, "entry": entry, "stop": entry - w * risk, "risk": risk,
                       "tp": entry + w * tp_r * risk, "i": i + 1, "t": idx[i + 1]}
                # a posicao so vive a partir da vela i+1: gerida na proxima iteracao
    if return_open:   # usado pelo bot da demo: devolve a trade ainda aberta no fim (sem a fechar)
        return pd.DataFrame(trades), (dict(cur) if cur is not None else None)
    if cur is not None:
        close_trade(n - 1, c[n - 1])
    return pd.DataFrame(trades)
