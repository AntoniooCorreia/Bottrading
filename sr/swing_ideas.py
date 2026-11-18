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


def tom_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Viragem do mes: long do ultimo dia util do mes ate ao fecho do 3.o dia util do mes seguinte.
    Usa so o calendario de dias uteis (seg-sex), conhecido com antecedencia: no fecho do dia d o sinal e 1 se o
    proximo dia util for o ultimo do mes ou um dos 3 primeiros do mes."""
    from pandas.tseries.offsets import BDay
    idx = b.index.tz_localize(None) if b.index.tz is not None else b.index
    nxt = idx.normalize() + BDay(1)
    last = (nxt + BDay(1)).month != nxt.month
    first = nxt.to_period("M").to_timestamp()
    nfirst = np.array([len(pd.bdate_range(f, x)) for f, x in zip(first, nxt)])
    return pd.Series(np.where(last | (nfirst <= 3), 1, 0), index=b.index)


def overnight_us_1h(b: pd.DataFrame) -> pd.Series:
    """1h, horas de Nova Iorque. Long na vela das 16:00 (sinal no fecho da vela das 15:00) e sai no fecho da vela
    das 08:00 (09:00 NY, antes da abertura do cash). So para NQ/S&P/Dow."""
    h = b.index.tz_convert("America/New_York").hour if b.index.tz is not None else b.index.hour
    return pd.Series(np.where((h >= 15) | (h < 8), 1, 0), index=b.index)


def double7_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Connors 'Double 7s': long quando o fecho e o mais baixo dos ultimos 7 fechos e esta acima da media de
    200 dias; sai quando o fecho e o mais alto dos ultimos 7 fechos."""
    c = b["close"]
    lo7, hi7 = c.rolling(7).min(), c.rolling(7).max()
    return _enter_exit((c <= lo7) & (c > c.rolling(200).mean()), c >= hi7)


def _naive(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    return idx.tz_localize(None) if idx.tz is not None else idx


def opex_week_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Semana de vencimento das opcoes mensais (3.a sexta-feira): no fecho do dia d o sinal e 1 se o proximo
    dia util (seg-sex, calendario conhecido com antecedencia) estiver entre a segunda e a 3.a sexta dessa semana."""
    from pandas.tseries.offsets import BDay
    nxt = _naive(b.index).normalize() + BDay(1)
    # 3.a sexta do mes do proximo dia util: primeira sexta + 14 dias
    first = nxt.to_period("M").to_timestamp()
    fri3 = first + pd.to_timedelta((4 - first.dayofweek) % 7 + 14, unit="D")
    inwk = (nxt <= fri3) & (nxt >= fri3 - pd.Timedelta(days=4))
    return pd.Series(np.where(inwk, 1, 0), index=b.index)


def _weekdays(b: pd.DataFrame) -> pd.DataFrame:
    """So velas de segunda a sexta (a vela de domingo tem precos parados do fim de semana)."""
    return b[_naive(b.index).dayofweek < 5]


def nr7_up_d(b: pd.DataFrame) -> pd.Series:
    """Diario. NR7 (amplitude menor que a de cada um dos 6 dias anteriores) com fecho > media de 200 -> long durante
    os 5 dias de semana seguintes (sai no fecho do 5.o). Um novo NR7 prolonga a janela."""
    w = _weekdays(b)
    rng = w["high"] - w["low"]
    nr7 = rng < rng.shift(1).rolling(6).min()
    sig = (nr7 & (w["close"] > w["close"].rolling(200).mean())).astype(int)
    pos = sig.rolling(5, min_periods=1).max()      # dia do sinal + 4 dias seguintes em posicao no fecho
    return pos.reindex(b.index).ffill().fillna(0).astype(int)


def week_rev_d(b: pd.DataFrame) -> pd.Series:
    """Diario. No fecho de sexta: se o fecho < fecho do ultimo dia da semana anterior e fecho > media de 200 -> long
    ate ao fecho da sexta seguinte (reavaliado a cada sexta)."""
    w = _weekdays(b)
    c = w["close"]
    d = _naive(w.index)
    wk = d.to_period("W-FRI")
    last = c.groupby(wk).transform("last")
    prev_last = pd.Series(last.groupby(wk).first().shift(1).reindex(wk).to_numpy(), index=c.index)
    fri = pd.Series(d.dayofweek == 4, index=c.index)
    sig = ((c < prev_last) & (c > c.rolling(200).mean())).astype(float)
    pos = sig.where(fri).ffill().fillna(0)
    return pos.reindex(b.index).ffill().fillna(0).astype(int)


def donchian_long(n_in: int, n_out: int):
    """Rutura de n_in velas so long (spot nao permite short): entra ao fechar acima do maximo das n_in velas
    anteriores; sai ao fechar abaixo do minimo das n_out velas anteriores."""
    def f(b: pd.DataFrame) -> pd.Series:
        hi = b["high"].rolling(n_in).max().shift(1)
        lo = b["low"].rolling(n_out).min().shift(1)
        return _enter_exit(b["close"] > hi, b["close"] < lo)
    return f


def sma_long(n: int):
    """So long acima da media de n velas, fora abaixo."""
    def f(b: pd.DataFrame) -> pd.Series:
        sma = b["close"].rolling(n).mean()
        return pd.Series(np.where(b["close"] > sma, 1, 0), index=b.index).where(sma.notna(), 0)
    return f


# nome -> (funcao, timeframe, stop_atr, tp_r, max_hold)
def rsi2_pop_short_4h(b: pd.DataFrame) -> pd.Series:
    """4h. Espelho do rsi2-dip-4h do lado vendedor: short quando RSI(2) > 90 e fecho abaixo da media de 200 velas
    (tendencia de baixa); sai quando fecha abaixo da media de 5 velas. Short-only."""
    c = b["close"]
    r, sma200, sma5 = _rsi(c, 2), c.rolling(200).mean(), c.rolling(5).mean()
    return -_enter_exit((r > 90) & (c < sma200), c < sma5)


def ibs_bear_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Espelho de regime do ibs-dip-d: long quando IBS < 0.2 e fecho ABAIXO da media de 200 dias
    (reversao de curto prazo com volatilidade alta, Nagel 2012); sai quando IBS > 0.7."""
    rng = (b["high"] - b["low"]).replace(0, np.nan)
    ibs = (b["close"] - b["low"]) / rng
    sma200 = b["close"].rolling(200).mean()
    return _enter_exit((ibs < 0.2) & (b["close"] < sma200), ibs > 0.7)


def turnaround_tue_d(b: pd.DataFrame) -> pd.Series:
    """Diario. 'Turnaround Tuesday': no fecho de segunda (dia CME), se o fecho < fecho do dia de semana anterior
    (sexta) -> long durante a terca (entra na abertura seguinte, sai no fecho de terca). Sem filtro de tendencia."""
    w = _weekdays(b)
    c = w["close"]
    mon = pd.Series(_naive(w.index).dayofweek == 0, index=c.index)
    sig = (mon & (c < c.shift(1))).astype(int)
    return sig.reindex(b.index).fillna(0).astype(int)


def keyrev_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Dia de reversao: minimo do dia abaixo do minimo dos 10 dias de semana anteriores e fecho acima do fecho
    anterior -> long durante os 5 dias de semana seguintes (sai no fecho do 5.o). Um novo sinal prolonga a janela."""
    w = _weekdays(b)
    c = w["close"]
    sig = ((w["low"] < w["low"].shift(1).rolling(10).min()) & (c > c.shift(1))).astype(int)
    pos = sig.rolling(5, min_periods=1).max()      # dia do sinal + 4 dias seguintes em posicao no fecho
    return pos.reindex(b.index).ffill().fillna(0).astype(int)


def pullback20_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Recuo numa tendencia forte: fecho cruza abaixo da media de 20 dias com medias alinhadas
    (20 > 50 > 200) -> long; sai no primeiro fecho acima do maior fecho dos 10 dias anteriores."""
    w = _weekdays(b)
    c = w["close"]
    s20, s50, s200 = c.rolling(20).mean(), c.rolling(50).mean(), c.rolling(200).mean()
    enter = (c < s20) & (c.shift(1) >= s20.shift(1)) & (s20 > s50) & (s50 > s200)
    pos = _enter_exit(enter, c > c.shift(1).rolling(10).max())
    return pos.reindex(b.index).ffill().fillna(0).astype(int)


def calmhigh_d(b: pd.DataFrame) -> pd.Series:
    """Diario. Maximo novo numa subida calma: primeiro fecho acima do maior fecho dos 10 dias anteriores, fecho acima
    da media de 200 e media do true range de 5 dias < media de 50 -> long durante os 5 dias de semana seguintes
    (sai no fecho do 5.o). Um novo sinal prolonga a janela."""
    w = _weekdays(b)
    h, l, c = w["high"], w["low"], w["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    newhi = c > c.shift(1).rolling(10).max()
    sig = (newhi & ~newhi.shift(1, fill_value=False) & (c > c.rolling(200).mean())
           & (tr.rolling(5).mean() < tr.rolling(50).mean())).astype(int)
    pos = sig.rolling(5, min_periods=1).max()      # dia do sinal + 4 dias seguintes em posicao no fecho
    return pos.reindex(b.index).ffill().fillna(0).astype(int)


# Reunioes PROGRAMADAS do FOMC (dia do comunicado, 14:00 NY). Calendario publicado pela Fed com meses de antecedencia
# (sem lookahead). 2020: so as reunioes programadas que se realizaram (as de emergencia de 3 e 15 de marco ficam de fora).
FOMC_DATES = [
    "2012-01-25", "2012-03-13", "2012-04-25", "2012-06-20", "2012-08-01", "2012-09-13", "2012-10-24", "2012-12-12",
    "2013-01-30", "2013-03-20", "2013-05-01", "2013-06-19", "2013-07-31", "2013-09-18", "2013-10-30", "2013-12-18",
    "2014-01-29", "2014-03-19", "2014-04-30", "2014-06-18", "2014-07-30", "2014-09-17", "2014-10-29", "2014-12-17",
    "2015-01-28", "2015-03-18", "2015-04-29", "2015-06-17", "2015-07-29", "2015-09-17", "2015-10-28", "2015-12-16",
    "2016-01-27", "2016-03-16", "2016-04-27", "2016-06-15", "2016-07-27", "2016-09-21", "2016-11-02", "2016-12-14",
    "2017-02-01", "2017-03-15", "2017-05-03", "2017-06-14", "2017-07-26", "2017-09-20", "2017-11-01", "2017-12-13",
    "2018-01-31", "2018-03-21", "2018-05-02", "2018-06-13", "2018-08-01", "2018-09-26", "2018-11-08", "2018-12-19",
    "2019-01-30", "2019-03-20", "2019-05-01", "2019-06-19", "2019-07-31", "2019-09-18", "2019-10-30", "2019-12-11",
    "2020-01-29", "2020-04-29", "2020-06-10", "2020-07-29", "2020-09-16", "2020-11-05", "2020-12-16",
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
]


def _nyse_holidays(y0: int, y1: int) -> pd.DatetimeIndex:
    """Feriados programados da NYSE (regras fixas; fechos extraordinarios nao anunciados ficam de fora)."""
    from pandas.tseries.holiday import (AbstractHolidayCalendar, GoodFriday, Holiday, USLaborDay,
                                        USMartinLutherKingJr, USMemorialDay, USPresidentsDay, USThanksgivingDay,
                                        nearest_workday, sunday_to_monday)

    class _NYSE(AbstractHolidayCalendar):
        rules = [
            Holiday("NewYear", month=1, day=1, observance=sunday_to_monday),
            USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
            Holiday("Juneteenth", month=6, day=19, start_date="2022-01-01", observance=nearest_workday),
            Holiday("July4", month=7, day=4, observance=nearest_workday),
            USLaborDay, USThanksgivingDay,
            Holiday("Christmas", month=12, day=25, observance=nearest_workday),
        ]
    return _NYSE().holidays(f"{y0}-01-01", f"{y1}-12-31")


def fomc_holiday_1h(b: pd.DataFrame) -> pd.Series:
    """1h, horas de Nova Iorque. Dois efeitos de calendario conhecidos com antecedencia:
    (a) deriva antes do FOMC (Lucca & Moench 2015): long das 14:00 do dia util anterior ao comunicado ate as 14:00
        do dia do comunicado (sinal no fecho da vela das 13:00);
    (b) vespera de feriado (Ariel 1990): long do fecho das 16:00 do dia anterior a vespera ate ao fecho das 16:00 da
        vespera do feriado da NYSE (sinal no fecho da vela das 15:00)."""
    from pandas.tseries.offsets import CustomBusinessDay
    idx = b.index.tz_convert("America/New_York") if b.index.tz is not None else b.index
    naive = idx.tz_localize(None) if idx.tz is not None else idx
    hol = _nyse_holidays(naive.min().year - 1, naive.max().year + 1)
    bd = CustomBusinessDay(holidays=hol)
    t = pd.Series(naive, index=b.index)
    on = np.zeros(len(b), dtype=bool)
    for d in pd.to_datetime(FOMC_DATES):
        start = (d - bd) + pd.Timedelta(hours=13)
        on |= ((t >= start) & (t < d + pd.Timedelta(hours=13))).to_numpy()
    for h in hol:
        pre = h - bd                       # vespera (ultimo dia de bolsa antes do feriado)
        start = (pre - bd) + pd.Timedelta(hours=15)
        on |= ((t >= start) & (t < pre + pd.Timedelta(hours=15))).to_numpy()
    return pd.Series(on.astype(int), index=b.index)


def flush_1h(b: pd.DataFrame) -> pd.Series:
    """1h, horas de Nova Iorque. Vela de queda violenta a meio da sessao cash, em tendencia de alta (Nagel 2012):
    sinal no fecho de uma vela que comeca entre as 10:00 e as 14:00 com amplitude > 2 x ATR(14), fecho < abertura,
    fecho no quarto inferior da vela e fecho > media das ultimas 4600 velas. Long ate ao fecho da 6.a vela depois
    do sinal (um novo sinal prolonga a janela). Stop 3 ATR (motor)."""
    from .swing import atr
    h = b.index.tz_convert("America/New_York").hour if b.index.tz is not None else b.index.hour
    rng = b["high"] - b["low"]
    a = pd.Series(atr(b), index=b.index)
    loc = (b["close"] - b["low"]) / rng.replace(0, np.nan)
    sig = ((h >= 10) & (h <= 14) & (rng > 2 * a) & (b["close"] < b["open"]) & (loc < 0.25)
           & (b["close"] > b["close"].rolling(4600).mean())).to_numpy()
    on = np.zeros(len(b), dtype=int)
    for i in np.flatnonzero(sig):
        on[i:i + 6] = 1           # quer estar long nas velas i..i+5 -> sai no fecho da vela i+6
    return pd.Series(on, index=b.index)


def ibs_cash_1h(b: pd.DataFrame) -> pd.Series:
    """1h, horas de Nova Iorque. IBS da sessao cash (velas das 09:00 as 15:00 NY, ~09:00-16:00), medido no fecho da
    vela das 15:00 (= 16:00). Long quando IBS < 0.2 e o fecho das 16:00 esta acima da media dos ultimos 200 fechos das
    16:00; sai no fecho das 16:00 de um dia com IBS > 0.7 ou ao fim de 115 velas (~5 dias). Stop 3 ATR de 1h (motor)."""
    ny = b.index.tz_convert("America/New_York") if b.index.tz is not None else b.index
    h = np.asarray(ny.hour)
    day = np.asarray(ny.normalize().asi8)
    cash = (h >= 9) & (h <= 15)
    hi = b["high"].where(cash).groupby(day).cummax()
    lo = b["low"].where(cash).groupby(day).cummin()
    ibs = ((b["close"] - lo) / (hi - lo).replace(0, np.nan)).to_numpy()
    last = h == 15
    c16 = b["close"][last]
    sma = pd.Series(np.nan, index=b.index)
    sma[last] = c16.rolling(200).mean().to_numpy()
    sma = sma.to_numpy()
    c = b["close"].to_numpy()
    pos, cur, held = np.zeros(len(b), dtype=int), 0, 0
    for i in range(len(b)):
        if cur == 1:
            held += 1
            if (last[i] and ibs[i] > 0.7) or held >= 115:
                cur = 0
        elif last[i] and ibs[i] < 0.2 and c[i] > sma[i]:
            cur, held = 1, 0
        pos[i] = cur
    return pd.Series(pos, index=b.index)


def rsi2_cash_1h(b: pd.DataFrame) -> pd.Series:
    """1h, horas de Nova Iorque. RSI(2) de Connors na serie dos fechos das 16:00 (fecho da vela das 15:00 NY).
    Long quando RSI(2) < 10 e o fecho das 16:00 esta acima da media dos ultimos 200 fechos das 16:00; sai no fecho das
    16:00 de um dia com fecho > media dos ultimos 5 fechos das 16:00 ou ao fim de 115 velas (~5 dias). Stop 3 ATR de 1h."""
    ny = b.index.tz_convert("America/New_York") if b.index.tz is not None else b.index
    last = np.asarray(ny.hour) == 15
    c16 = b["close"][last]
    r = np.full(len(b), np.nan)
    s200 = np.full(len(b), np.nan)
    s5 = np.full(len(b), np.nan)
    r[last] = _rsi(c16, 2).to_numpy()
    s200[last] = c16.rolling(200).mean().to_numpy()
    s5[last] = c16.rolling(5).mean().to_numpy()
    c = b["close"].to_numpy()
    pos, cur, held = np.zeros(len(b), dtype=int), 0, 0
    for i in range(len(b)):
        if cur == 1:
            held += 1
            if (last[i] and c[i] > s5[i]) or held >= 115:
                cur = 0
        elif last[i] and r[i] < 10 and c[i] > s200[i]:
            cur, held = 1, 0
        pos[i] = cur
    return pd.Series(pos, index=b.index)


IDEAS = {
    "trend-sma100-d": (trend_sma100, "1d", 3.0, 0.0, 0),
    "rsi2-dip-d": (rsi2_dip, "1d", 3.0, 0.0, 10),
    "donchian20-d": (donchian20, "1d", 3.0, 0.0, 0),
    "rsi2-dip-4h": (rsi2_dip_4h, "4h", 3.0, 0.0, 30),
    "ibs-dip-d": (ibs_dip_d, "1d", 3.0, 0.0, 10),
    "down3-d": (down3_d, "1d", 3.0, 0.0, 10),
    "tom-d": (tom_d, "1d", 3.0, 0.0, 6),
    "overnight-us-1h": (overnight_us_1h, "1h", 3.0, 0.0, 24),
    "double7-d": (double7_d, "1d", 3.0, 0.0, 10),
    "opex-week-d": (opex_week_d, "1d", 3.0, 0.0, 0),
    "nr7-up-d": (nr7_up_d, "1d", 3.0, 0.0, 0),
    "week-rev-d": (week_rev_d, "1d", 3.0, 0.0, 0),
    "rsi2-pop-short-4h": (rsi2_pop_short_4h, "4h", 3.0, 0.0, 30),
    "ibs-bear-d": (ibs_bear_d, "1d", 3.0, 0.0, 10),
    "turnaround-tue-d": (turnaround_tue_d, "1d", 3.0, 0.0, 0),
    "keyrev-d": (keyrev_d, "1d", 3.0, 0.0, 0),
    "pullback20-d": (pullback20_d, "1d", 3.0, 0.0, 20),
    "calmhigh-d": (calmhigh_d, "1d", 3.0, 0.0, 0),
    "fomc-holiday-1h": (fomc_holiday_1h, "1h", 3.0, 0.0, 0),
    "flush-1h": (flush_1h, "1h", 3.0, 0.0, 0),
    "ibs-cash-1h": (ibs_cash_1h, "1h", 3.0, 0.0, 0),
    "rsi2-cash-1h": (rsi2_cash_1h, "1h", 3.0, 0.0, 0),
    # crypto (2026-11-18, registadas antes de correr): tendencia so long, para spot na Kraken
    "k-donchian20-d": (donchian_long(20, 10), "1d", 3.0, 0.0, 0),
    "k-sma100-d": (sma_long(100), "1d", 3.0, 0.0, 0),
    "k-donchian55-4h": (donchian_long(55, 20), "4h", 3.0, 0.0, 0),
    "k-sma200-4h": (sma_long(200), "4h", 3.0, 0.0, 0),
}
