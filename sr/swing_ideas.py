"""
Registo de ideias de prazo mais longo. Cada ideia: funcao(velas) -> Series de posicao desejada (+1/-1/0) no fecho.
So informacao ate ao fecho da propria vela (usar .rolling/.shift, nunca valores futuros).
Para acrescentar uma ideia: regista-a primeiro em IDEAS.md, depois escreve a funcao aqui e poe-a em IDEAS.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def trend_sma100(b: pd.DataFrame) -> pd.Series:
    """Diario. Long quando o fecho esta acima da media de 100 dias, fora quando abaixo (filtro de tendencia classico)."""
    sma = b["close"].rolling(100).mean()
    return pd.Series(np.where(b["close"] > sma, 1, 0), index=b.index).where(sma.notna(), 0)


def rsi2_dip(b: pd.DataFrame) -> pd.Series:
    """Diario. Compra quedas curtas em tendencia: entra long quando RSI(2) < 10 e fecho > media 200 dias;
    sai quando o fecho passa acima da media de 5 dias (Connors)."""
    c = b["close"]
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 2, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 2, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    sma200, sma5 = c.rolling(200).mean(), c.rolling(5).mean()
    pos, cur = [], 0
    for i in range(len(c)):
        if cur == 0 and rsi.iloc[i] < 10 and c.iloc[i] > sma200.iloc[i]:
            cur = 1
        elif cur == 1 and c.iloc[i] > sma5.iloc[i]:
            cur = 0
        pos.append(cur)
    return pd.Series(pos, index=b.index)


def donchian20(b: pd.DataFrame) -> pd.Series:
    """Diario. Rutura de 20 dias (tartarugas): long ao fechar acima do maximo dos 20 dias anteriores, short abaixo do
    minimo; sai ao fechar do lado oposto do canal de 10 dias."""
    hi20, lo20 = b["high"].rolling(20).max().shift(1), b["low"].rolling(20).min().shift(1)
    hi10, lo10 = b["high"].rolling(10).max().shift(1), b["low"].rolling(10).min().shift(1)
    c = b["close"]
    pos, cur = [], 0
    for i in range(len(c)):
        if cur == 1 and c.iloc[i] < lo10.iloc[i]:
            cur = 0
        elif cur == -1 and c.iloc[i] > hi10.iloc[i]:
            cur = 0
        if cur == 0:
            if c.iloc[i] > hi20.iloc[i]:
                cur = 1
            elif c.iloc[i] < lo20.iloc[i]:
                cur = -1
        pos.append(cur)
    return pd.Series(pos, index=b.index)


def _rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def _enter_exit(enter: pd.Series, exit_: pd.Series) -> pd.Series:
    pos, cur = [], 0
    for e, x in zip(enter.to_numpy(), exit_.to_numpy()):
        if cur == 0 and e:
            cur = 1
        elif cur == 1 and x:
            cur = 0
        pos.append(cur)
    return pd.Series(pos, index=enter.index)


def rsi2_dip_4h(b: pd.DataFrame) -> pd.Series:
    """4h. A mesma ideia do rsi2-dip-d em velas de 4h: long quando RSI(2) < 10 e fecho acima da media de 200 velas
    (~6 semanas); sai quando fecha acima da media de 5 velas. Mais trades que o diario."""
    c = b["close"]
    r, sma200, sma5 = _rsi(c, 2), c.rolling(200).mean(), c.rolling(5).mean()
    return _enter_exit((r < 10) & (c > sma200), c > sma5)


def ibs_dip_d(b: pd.DataFrame) -> pd.Series:
    """Diario. IBS (onde fecha dentro da vela: (fecho-minimo)/(maximo-minimo)). Long quando IBS < 0.2 e fecho acima
    da media de 200 dias; sai quando IBS > 0.7. Efeito de reversao de curto prazo documentado em indices."""
    rng = (b["high"] - b["low"]).replace(0, np.nan)
    ibs = (b["close"] - b["low"]) / rng
    sma200 = b["close"].rolling(200).mean()
    return _enter_exit((ibs < 0.2) & (b["close"] > sma200), ibs > 0.7)


def down3_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Tres fechos seguidos em queda acima da media de 200 dias -> long; sai no primeiro fecho acima do maximo
    do dia anterior. Variante simples de comprar quedas em tendencia."""
    c = b["close"]
    dn3 = (c < c.shift(1)) & (c.shift(1) < c.shift(2)) & (c.shift(2) < c.shift(3))
    return _enter_exit(dn3 & (c > c.rolling(200).mean()), c > b["high"].shift(1))


# nome -> (funcao, timeframe, stop_atr, tp_r, max_hold)
IDEAS = {
    "trend-sma100-d": (trend_sma100, "1d", 3.0, 0.0, 0),
    "rsi2-dip-d": (rsi2_dip, "1d", 3.0, 0.0, 10),
    "donchian20-d": (donchian20, "1d", 3.0, 0.0, 0),
    "rsi2-dip-4h": (rsi2_dip_4h, "4h", 3.0, 0.0, 30),
    "ibs-dip-d": (ibs_dip_d, "1d", 3.0, 0.0, 10),
    "down3-d": (down3_d, "1d", 3.0, 0.0, 10),
}
