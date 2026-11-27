"""
Especificacoes das estrategias que a conta demo EXPERIMENTAL (Edge Function paper-bot, conta 2) sabe correr ao vivo.
A mesma logica existe em TypeScript em supabase/functions/paper-bot/engine.ts; tests/test_demo_spec.py garante que:
  1) para cada ideia em SPECS, o sinal de entrada desta especificacao e IGUAL ao da ideia em sr/swing_ideas.py (dados reais);
  2) o engine.ts da as mesmas entradas que este ficheiro (corre com node, se existir).
O agente escolhe sozinho qual destas corre na demo experimental (demo_pick.py). Ideia nova que caiba nestas familias ->
acrescentar aqui + correr pytest. Familias de entrada:
  breakout  fecho acima do maximo (long) / abaixo do minimo (short) das n velas anteriores
  rsi2      RSI(2) < lo (long) / > 100-lo (short); com signal_exit sai quando RSI > hi (long) / < 100-hi (short)
  lowclose  fecho e o mais baixo das ultimas n velas (long)
  above_sma fecho acima da media de n velas (long) / abaixo da media (short, side -1)
Filtro de volume opcional: vol_mult (volume da vela > vol_mult x media das n velas anteriores; n = entry.n).
Estilo (para as contas demo): scalping = velas de 5m/15m; day trade = 1h/4h com tempo maximo <= 24h; swing = o resto.
Filtros: trend_ema (fecho acima/abaixo da EMA de n velas, conforme o lado), btc ("bull"/"bear": BTC fechou o dia anterior
acima/abaixo da media de 200 dias).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TF_MIN = {"5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}

SPECS: dict[str, dict] = {
    "h-dc24-1h": {"num": "#131/#133", "tf": "1h", "side": 1, "entry": {"kind": "breakout", "n": 24}, "trend_ema": 200,
                  "btc": "bull", "stop_atr": 3.0, "tp_r": 2.0, "max_hold": 24, "signal_exit": False},
    "h-dc24-1h-short": {"num": "#134", "tf": "1h", "side": -1, "entry": {"kind": "breakout", "n": 24}, "trend_ema": 200,
                        "btc": "bear", "stop_atr": 3.0, "tp_r": 2.0, "max_hold": 24, "signal_exit": False},
    "h-rsi2-1h": {"num": "#129/#135", "tf": "1h", "side": 1, "entry": {"kind": "rsi2", "lo": 10, "hi": 70}, "trend_ema": 200,
                  "btc": "bull", "stop_atr": 3.0, "tp_r": 0.0, "max_hold": 24, "signal_exit": True},
    "h-low12-tp-1h": {"num": "#130", "tf": "1h", "side": 1, "entry": {"kind": "lowclose", "n": 12}, "trend_ema": 200,
                      "btc": "bull", "stop_atr": 3.0, "tp_r": 1.0, "max_hold": 24, "signal_exit": False},
    "k-sma600-4h-bull-bracket": {"num": "#138", "tf": "4h", "side": 1, "entry": {"kind": "above_sma", "n": 600}, "trend_ema": 0,
                                 "btc": "bull", "stop_atr": 3.0, "tp_r": 1.0, "max_hold": 0, "signal_exit": False},
    "k-sma100-d-bull-bracket": {"num": "#118", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 100}, "trend_ema": 0,
                                "btc": "bull", "stop_atr": 3.0, "tp_r": 1.0, "max_hold": 0, "signal_exit": False},
    "k-sma100-d-bull-bracket-mh10": {"num": "#139", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 100},
                                     "trend_ema": 0, "btc": "bull", "stop_atr": 3.0, "tp_r": 1.0, "max_hold": 10,
                                     "signal_exit": False},
    "k-sma100-d-bull-bracket-s2": {"num": "#141", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 100},
                                   "trend_ema": 0, "btc": "bull", "stop_atr": 2.0, "tp_r": 1.0, "max_hold": 0,
                                   "signal_exit": False},
    "k-sma100-d-bull-bracket-s2-mh10": {"num": "#143", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 100},
                                        "trend_ema": 0, "btc": "bull", "stop_atr": 2.0, "tp_r": 1.0, "max_hold": 10,
                                        "signal_exit": False},
    "k-sma50-d-bull-bracket-s2": {"num": "#144", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 50},
                                  "trend_ema": 0, "btc": "bull", "stop_atr": 2.0, "tp_r": 1.0, "max_hold": 0,
                                  "signal_exit": False},
    # ---- mercado em baixa (2026-11-23/26) ----
    "l-dc20-4h-bear-s2-tp2-mh12": {"num": "#191", "tf": "4h", "side": 1, "entry": {"kind": "breakout", "n": 20}, "trend_ema": 0,
                                   "btc": "bear", "stop_atr": 2.0, "tp_r": 2.0, "max_hold": 12, "signal_exit": False},
    "l-dc20-4h-bear-vol15-s2-tp2-mh12": {"num": "#197", "tf": "4h", "side": 1, "entry": {"kind": "breakout", "n": 20},
                                         "vol_mult": 1.5, "trend_ema": 0, "btc": "bear", "stop_atr": 2.0, "tp_r": 2.0,
                                         "max_hold": 12, "signal_exit": False},
    "l-dc24-1h-bear-vol15-s3-tp2-mh24": {"num": "#202", "tf": "1h", "side": 1, "entry": {"kind": "breakout", "n": 24},
                                         "vol_mult": 1.5, "trend_ema": 200, "btc": "bear", "stop_atr": 3.0, "tp_r": 2.0,
                                         "max_hold": 24, "signal_exit": False},
    "l-dc20-4h-bear-vol15-s2-tp1-mh6": {"num": "#204", "tf": "4h", "side": 1, "entry": {"kind": "breakout", "n": 20},
                                        "vol_mult": 1.5, "trend_ema": 0, "btc": "bear", "stop_atr": 2.0, "tp_r": 1.0,
                                        "max_hold": 6, "signal_exit": False},
    "h-rsi2-1h-short": {"num": "#136", "tf": "1h", "side": -1, "entry": {"kind": "rsi2", "lo": 10, "hi": 70}, "trend_ema": 200,
                        "btc": "bear", "stop_atr": 3.0, "tp_r": 0.0, "max_hold": 24, "signal_exit": True},
    # ---- scalping (15m) ----
    "s-rsi2-15m-long": {"num": "#124", "tf": "15m", "side": 1, "entry": {"kind": "rsi2", "lo": 5, "hi": 60}, "trend_ema": 200,
                        "btc": "", "stop_atr": 2.0, "tp_r": 0.0, "max_hold": 16, "signal_exit": True},
    "s-rsi2-15m-short": {"num": "#125", "tf": "15m", "side": -1, "entry": {"kind": "rsi2", "lo": 5, "hi": 60}, "trend_ema": 200,
                         "btc": "", "stop_atr": 2.0, "tp_r": 0.0, "max_hold": 16, "signal_exit": True},
    "k-sma50-d-bull-bracket-s2-mh3": {"num": "#163", "tf": "1d", "side": 1, "entry": {"kind": "above_sma", "n": 50},
                                      "trend_ema": 0, "btc": "bull", "stop_atr": 2.0, "tp_r": 1.0, "max_hold": 3,
                                      "signal_exit": False},
}


def ema(c: pd.Series, n: int) -> pd.Series:
    return c.ewm(span=n, adjust=False).mean()


def rsi(c: pd.Series, n: int = 2) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def btc_regime(index: pd.DatetimeIndex, btc_daily: pd.DataFrame, want: str) -> pd.Series:
    c = btc_daily["close"]
    m = c.rolling(200).mean()
    bull = (c > m).astype(float).where(m.notna())
    bull.index = bull.index + pd.Timedelta(days=1)
    r = bull.reindex(bull.index.union(index)).ffill().reindex(index).fillna(0).astype(bool)
    return r if want == "bull" else ~r


def entry_signal(b: pd.DataFrame, spec: dict, btc_daily: pd.DataFrame) -> pd.Series:
    """True na vela em que a demo entraria (na abertura da vela seguinte)."""
    c, e, side = b["close"], spec["entry"], spec["side"]
    if e["kind"] == "breakout":
        sig = (c > b["high"].rolling(e["n"]).max().shift(1)) if side == 1 else (c < b["low"].rolling(e["n"]).min().shift(1))
    elif e["kind"] == "rsi2":
        r = rsi(c, 2)
        sig = (r < e["lo"]) if side == 1 else (r > 100 - e["lo"])
    elif e["kind"] == "lowclose":
        sig = c <= c.rolling(e["n"]).min()
    elif e["kind"] == "above_sma":
        m = c.rolling(e["n"]).mean()
        sig = ((c > m) if side == 1 else (c < m)) & m.notna()
    else:
        raise ValueError(e["kind"])
    if spec.get("vol_mult") and "volume" in b:
        v = b["volume"]
        sig = sig & (v > spec["vol_mult"] * v.rolling(e["n"]).mean().shift(1))
    if spec.get("trend_ema"):
        t = ema(c, spec["trend_ema"])
        sig = sig & ((c > t) if side == 1 else (c < t))
    if spec.get("btc"):
        sig = sig & btc_regime(b.index, btc_daily, spec["btc"])
    return sig.fillna(False).astype(bool)


def exit_signal(b: pd.DataFrame, spec: dict) -> pd.Series:
    """So para signal_exit=True (rsi2): True quando a posicao aberta sai no fecho."""
    e, side = spec["entry"], spec["side"]
    if not spec.get("signal_exit"):
        return pd.Series(False, index=b.index)
    if e["kind"] == "rsi2":
        r = rsi(b["close"], 2)
        return ((r > e["hi"]) if side == 1 else (r < 100 - e["hi"])).fillna(False)
    raise ValueError(e["kind"])


def style(spec: dict) -> str:
    """scalp (5m/15m), day (1h/4h com saida em <= 24h) ou swing (o resto)."""
    tf = spec["tf"]
    if tf in ("5m", "15m"):
        return "scalp"
    hold_h = spec.get("max_hold", 0) * TF_MIN[tf] / 60
    return "day" if tf in ("1h", "4h") and 0 < hold_h <= 24 else "swing"
