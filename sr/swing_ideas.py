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


# ---- cripto 2026-11-19 (registadas em IDEAS.md antes de correr) ----
def btc_bull_regime(index: pd.DatetimeIndex, btc_daily: pd.DataFrame | None = None, n: int = 200) -> pd.Series:
    """True quando o BTC FECHOU o dia (UTC) anterior acima da media de 200 dias. So usa dias ja fechados:
    o valor do dia D vale a partir das 00:00 de D+1. Fora do intervalo dos dados do BTC (ex.: velas sinteticas dos testes)
    devolve None para a ideia usar o regime da propria serie."""
    if len(index) == 0:      # moeda sem dados no periodo (ex.: SOL em 2017-2018)
        return pd.Series(False, index=index, dtype=bool)
    if btc_daily is None:
        try:
            from .swing import load_tf
            btc_daily = load_tf("btc", "1d", None)
        except Exception:
            return None
    if index.tz is None or len(btc_daily) < n + 1 or index[-1] < btc_daily.index[0] + pd.Timedelta(days=n):
        return None
    c = btc_daily["close"]
    bull = (c > c.rolling(n).mean()).astype(float).where(c.rolling(n).mean().notna())
    bull.index = bull.index + pd.Timedelta(days=1)          # conhecido so no fim do dia -> vale no dia seguinte
    out = bull.reindex(bull.index.union(index)).ffill().reindex(index)
    return out.fillna(0).astype(bool)


def _regime(b: pd.DataFrame, n_own: int, n_btc: int = 200) -> pd.Series:
    r = btc_bull_regime(b.index, n=n_btc)
    if r is None:   # sem dados do BTC para estas datas: regime da propria serie (so passado)
        c = b["close"]
        r = (c > c.rolling(n_own).mean()).shift(1).fillna(False).astype(bool)
    return r


def sma_persist(n: int, k: int):
    """So long quando os ultimos k fechos estao todos acima da media de n velas; sai quando os ultimos k estao todos abaixo."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        above = (c > sma).astype(int).rolling(k).sum() == k
        below = (c < sma).astype(int).rolling(k).sum() == k
        return _enter_exit(above & sma.notna(), below)
    return f


def donchian_long_bull(n_in: int, n_out: int):
    """donchian_long, mas so entra com o BTC acima da media de 200 dias (dia anterior fechado). Saida igual."""
    def f(b: pd.DataFrame) -> pd.Series:
        hi = b["high"].rolling(n_in).max().shift(1)
        lo = b["low"].rolling(n_out).min().shift(1)
        return _enter_exit((b["close"] > hi) & _regime(b, 200), b["close"] < lo)
    return f


def dip_hold(n_trend: int, n_low: int, hold: int):
    """Recuo dentro da tendencia: BTC em alta (media 200 dias) e moeda acima da media de n_trend velas e fecho = minimo
    das ultimas n_low velas -> long durante 'hold' velas (sai no fecho da vela hold depois da entrada)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n_trend).mean()
        low = c <= c.rolling(n_low).min()
        trig = (_regime(b, 200) & (c > sma) & low & sma.notna()).to_numpy()
        pos, left = np.zeros(len(c), dtype=int), 0
        for i in range(len(c)):
            if left > 0:
                pos[i] = 1
                left -= 1
            elif trig[i]:
                pos[i] = 1
                left = hold   # posicao vive da vela i+1 a i+hold; sai no fecho da vela i+hold
        return pd.Series(pos, index=b.index)
    return f


def sma_persist_bull(n: int, k: int):
    """sma_persist, mas so ENTRA com o BTC acima da media de 200 dias (dia anterior fechado). Saida igual (k fechos abaixo)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        above = (c > sma).astype(int).rolling(k).sum() == k
        below = (c < sma).astype(int).rolling(k).sum() == k
        return _enter_exit(above & sma.notna() & _regime(b, 200), below)
    return f


# ---- cripto sessao 4 (2026-11-19 :30), registadas em IDEAS.md antes de correr ----
def _own_regime(b: pd.DataFrame, n: int) -> pd.Series:
    """True quando a propria serie fechou a vela ANTERIOR acima da media de n velas (so passado)."""
    c = b["close"]
    sma = c.rolling(n).mean()
    return ((c > sma) & sma.notna()).shift(1, fill_value=False).astype(bool)


def donchian_long_own(n_in: int, n_out: int, n_reg: int):
    """donchian_long, mas so entra com a propria moeda acima da media de n_reg velas (vela anterior fechada)."""
    def f(b: pd.DataFrame) -> pd.Series:
        hi = b["high"].rolling(n_in).max().shift(1)
        lo = b["low"].rolling(n_out).min().shift(1)
        return _enter_exit((b["close"] > hi) & _own_regime(b, n_reg), b["close"] < lo)
    return f


def sma_long_bull(n: int, n_btc: int = 200):
    """Entra ao fechar acima da media de n velas com o BTC acima da media de n_btc dias; sai ao fechar abaixo da media."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        return _enter_exit((c > sma) & sma.notna() & _regime(b, n_btc, n_btc), c < sma)
    return f


def sma_slope_bull(n: int, k: int):
    """sma_long_bull, mas so entra com a media de n velas a subir (media de hoje acima da de ha k velas). Saida igual."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        up = sma > sma.shift(k)
        return _enter_exit((c > sma) & sma.notna() & up & _regime(b, 200), c < sma)
    return f


def sma_bull_entry(n: int):
    """Condicao de entrada da #113 (moeda acima da media de n velas e BTC acima da media de 200 dias), vela a vela.
    Usada com signal_exit=False: so serve para entrar; a saida e so por alvo/stop."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        return ((c > sma) & sma.notna() & _regime(b, 200)).astype(int)
    return f


def sma_own_entry(n: int):
    """Como sma_bull_entry mas sem o filtro do BTC: so a moeda acima da sua media de n velas (vela a vela)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        return ((c > sma) & sma.notna()).astype(int)
    return f


def btc_ema_regime(index: pd.DatetimeIndex, n: int = 200) -> pd.Series | None:
    """Como btc_bull_regime mas com a EMA de n dias do BTC (so dias ja fechados: vale a partir do dia seguinte)."""
    if len(index) == 0:
        return pd.Series(False, index=index, dtype=bool)
    try:
        from .swing import load_tf
        btc_daily = load_tf("btc", "1d", None)
    except Exception:
        return None
    if index.tz is None or len(btc_daily) < n + 1 or index[-1] < btc_daily.index[0] + pd.Timedelta(days=n):
        return None
    c = btc_daily["close"]
    bull = (c > c.ewm(span=n, adjust=False).mean()).astype(float)
    bull.index = bull.index + pd.Timedelta(days=1)
    out = bull.reindex(bull.index.union(index)).ffill().reindex(index)
    return out.fillna(0).astype(bool)


def ema_bull_entry(n: int, n_btc: int = 200):
    """#145: moeda acima da EMA de n velas e BTC acima da EMA de n_btc dias (dia anterior fechado), vela a vela.
    Sem dados do BTC para as datas: EMA de n_btc da propria serie (so passado)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        e = c.ewm(span=n, adjust=False).mean()
        r = btc_ema_regime(b.index, n_btc)
        if r is None:
            r = (c > c.ewm(span=n_btc, adjust=False).mean()).shift(1).fillna(False).astype(bool)
        return ((c > e) & r).astype(int)
    return f


def sma_bull2_entry(n: int, n_btc_fast: int = 50):
    """#146: como sma_bull_entry, mas o BTC tem de estar acima da media de 200 dias E da media de n_btc_fast dias."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        return ((c > sma) & sma.notna() & _regime(b, 200) & _regime(b, n_btc_fast, n_btc_fast)).astype(int)
    return f


def sma_bull2_extra_entry(n: int, extra: str, n_btc_fast: int = 50):
    """#149/#150: condicoes da #146 + um filtro diario extra (so passado, fecho da vela).
    extra='mom7': fecho acima do fecho de 7 velas antes; extra='red': fecho abaixo do fecho anterior."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        base = sma_bull2_entry(n, n_btc_fast)(b).astype(bool)
        if extra == "mom7":
            x = c > c.shift(7)
        elif extra == "red":
            x = c < c.shift(1)
        else:
            raise ValueError(extra)
        return (base & x.fillna(False)).astype(int)
    return f


def sma_btc50_entry(n: int, n_btc: int = 50):
    """#151: moeda acima da media de n velas e BTC acima SO da media de n_btc dias (dia anterior fechado), vela a vela."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        return ((c > sma) & sma.notna() & _regime(b, n_btc, n_btc)).astype(int)
    return f


def sma_up_bull2_entry(n: int, k: int = 5, n_btc_fast: int = 50):
    """#153: condicoes da #147 (sma_bull2_entry) + media de n velas da moeda acima da de k velas antes (a subir)."""
    def f(b: pd.DataFrame) -> pd.Series:
        sma = b["close"].rolling(n).mean()
        base = sma_bull2_entry(n, n_btc_fast)(b).astype(bool)
        return (base & (sma > sma.shift(k)).fillna(False)).astype(int)
    return f


def btc_regime_off(n_btc_fast: int = 50):
    """#154: mascara de saida: True quando o regime do BTC (dia anterior acima das medias de 200 e n_btc_fast) esta desligado."""
    def f(b: pd.DataFrame) -> pd.Series:
        return ~(_regime(b, 200) & _regime(b, n_btc_fast, n_btc_fast)).astype(bool)
    return f


def btc_sma_up_regime(index: pd.DatetimeIndex, n: int = 50, k: int = 10) -> pd.Series | None:
    """#156: True quando, no dia anterior fechado, o BTC fechou acima da media de n dias E essa media estava acima da de k dias antes."""
    if len(index) == 0:
        return pd.Series(False, index=index, dtype=bool)
    try:
        from .swing import load_tf
        btc_daily = load_tf("btc", "1d", None)
    except Exception:
        return None
    if index.tz is None or len(btc_daily) < n + k + 1 or index[-1] < btc_daily.index[0] + pd.Timedelta(days=n + k):
        return None
    c = btc_daily["close"]
    sma = c.rolling(n).mean()
    ok = ((c > sma) & (sma > sma.shift(k))).astype(float).where(sma.shift(k).notna())
    ok.index = ok.index + pd.Timedelta(days=1)
    out = ok.reindex(ok.index.union(index)).ffill().reindex(index)
    return out.fillna(0).astype(bool)


def sma_btc50up_entry(n: int, n_btc: int = 50, k: int = 10):
    """#156: moeda acima da media de n velas; BTC acima da media de n_btc dias com essa media a subir (vs k dias antes).
    Sem dados do BTC: o mesmo na propria serie (so passado)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n).mean()
        r = btc_sma_up_regime(b.index, n_btc, k)
        if r is None:
            s2 = c.rolling(n_btc).mean()
            r = ((c > s2) & (s2 > s2.shift(k))).shift(1).fillna(False).astype(bool)
        return ((c > sma) & sma.notna() & r).astype(int)
    return f


def btc50_off(n_btc: int = 50):
    """#155: mascara de saida: True quando o regime da #151 (BTC fechou o dia anterior acima da media de n_btc) esta desligado."""
    def f(b: pd.DataFrame) -> pd.Series:
        return ~_regime(b, n_btc, n_btc).astype(bool)
    return f


def pullback_bull(n_trend: int, n_dip: int, n_hi: int):
    """Recuo na tendencia: BTC em alta, moeda acima da media de n_trend e fecho abaixo dos n_dip fechos anteriores.
    Sai ao fechar acima do maximo das n_hi velas anteriores (tendencia retomada)."""
    def f(b: pd.DataFrame) -> pd.Series:
        c = b["close"]
        sma = c.rolling(n_trend).mean()
        dip = c < c.rolling(n_dip).min().shift(1)
        hi = b["high"].rolling(n_hi).max().shift(1)
        return _enter_exit(_regime(b, 200) & (c > sma) & sma.notna() & dip, c > hi)
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
    # cripto 2026-11-19 (win rate): registadas em IDEAS.md antes de correr
    "k-sma200-4h-persist": (sma_persist(200, 6), "4h", 3.0, 0.0, 0),
    "k-dc55-4h-btcbull": (donchian_long_bull(55, 20), "4h", 3.0, 0.0, 0),
    "k-dc55-4h-wide": (donchian_long(55, 20), "4h", 6.0, 0.0, 0),
    "k-dip-hold-4h": (dip_hold(600, 30, 42), "4h", 6.0, 0.0, 0),
    # cripto sessao 2 (2026-11-19 :30): regime BTC + stop largo + alvo 1R (registadas em IDEAS.md antes de correr)
    "k-dc55-4h-bw-tp1": (donchian_long_bull(55, 20), "4h", 6.0, 1.0, 0),
    "k-persist-bw": (sma_persist_bull(200, 6), "4h", 6.0, 0.0, 0),
    "k-persist-bw-tp1": (sma_persist_bull(200, 6), "4h", 6.0, 1.0, 0),
    "k-dc20-d-bull-tp1": (donchian_long_bull(20, 10), "1d", 3.0, 1.0, 0),
    # cripto sessao 3 (2026-11-19 :00): saida parcial / breakeven e rutura 20 velas de 4h (registadas em IDEAS.md antes de correr)
    "k-persist-bw-half": (sma_persist_bull(200, 6), "4h", 6.0, 1.0, 0),
    "k-dc20-4h-bw-tp1": (donchian_long_bull(20, 10), "4h", 6.0, 1.0, 0),
    "k-dc20-4h-bw-half": (donchian_long_bull(20, 10), "4h", 6.0, 1.0, 0),
    "k-dc20-4h-bw-be": (donchian_long_bull(20, 10), "4h", 6.0, 1.0, 0),
    # cripto sessao 4 (2026-11-19 :30): diario, regime proprio, brackets de 1R, recuo com alvo (registadas antes de correr)
    "k-dc20-d-own-tp1": (donchian_long_own(20, 10, 200), "1d", 3.0, 1.0, 0),
    "k-sma100-d-bull-tp1": (sma_long_bull(100), "1d", 3.0, 1.0, 0),
    "k-pb-d-bull-tp1": (pullback_bull(100, 5, 20), "1d", 3.0, 1.0, 0),
    "k-dc20-d-own-be": (donchian_long_own(20, 10, 200), "1d", 3.0, 1.0, 0),
    # cripto sessao 5 (2026-11-19 :00): variantes da #113 (registadas em IDEAS.md antes de correr)
    "k-sma100-d-b100-tp1": (sma_long_bull(100, 100), "1d", 3.0, 1.0, 0),
    "k-sma600-4h-bull-tp1": (sma_long_bull(600), "4h", 6.0, 1.0, 0),
    "k-sma100-d-bull-bracket": (sma_bull_entry(100), "1d", 3.0, 1.0, 0),
    "k-sma100-d-slope-tp1": (sma_slope_bull(100, 20), "1d", 3.0, 1.0, 0),
    # cripto 2026-11-21 sessao :00 19h (registada em IDEAS.md antes de correr): #118 em 4h, stop 3 ATR de 4h
    "k-sma600-4h-bull-bracket": (sma_bull_entry(600), "4h", 3.0, 1.0, 0),
    # cripto 2026-11-22 sessao :00 00h (registadas em IDEAS.md antes de correr): variantes da #118
    "k-sma100-d-bull-bracket-mh10": (sma_bull_entry(100), "1d", 3.0, 1.0, 10),
    "k-sma100-d-own-bracket": (sma_own_entry(100), "1d", 3.0, 1.0, 0),
    "k-sma100-d-bull-bracket-s2": (sma_bull_entry(100), "1d", 2.0, 1.0, 0),
    # cripto 2026-11-22 sessao :30 00h30 (registadas em IDEAS.md antes de correr): variantes da #141
    "k-sma100-d-bull-bracket-s2-mh10": (sma_bull_entry(100), "1d", 2.0, 1.0, 10),
    "k-sma50-d-bull-bracket-s2": (sma_bull_entry(50), "1d", 2.0, 1.0, 0),
    "k-ema100-d-bull-bracket-s2": (ema_bull_entry(100), "1d", 2.0, 1.0, 0),
    "k-sma100-d-bull50-bracket-s2": (sma_bull2_entry(100), "1d", 2.0, 1.0, 0),
    # cripto 2026-11-22 sessao :00 (01h), base #146 (registadas antes de correr)
    "k-sma50-d-bull50-bracket-s2": (sma_bull2_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma100-d-bull50-bracket-s2-tp075": (sma_bull2_entry(100), "1d", 2.0, 0.75, 0),
    "k-sma100-d-bull50-mom7-bracket-s2": (sma_bull2_extra_entry(100, "mom7"), "1d", 2.0, 1.0, 0),
    "k-sma100-d-bull50-red-bracket-s2": (sma_bull2_extra_entry(100, "red"), "1d", 2.0, 1.0, 0),
    # cripto 2026-11-22 sessao :30 (01h30), base #147 (registadas antes de correr)
    "k-sma50-d-btc50-bracket-s2": (sma_btc50_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma50-d-bull50-bracket-s2-lose7": (sma_bull2_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma50up-d-bull50-bracket-s2": (sma_up_bull2_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma50-d-bull50-bracket-s2-rx": (sma_bull2_entry(50), "1d", 2.0, 1.0, 0),
    # cripto 2026-11-22 sessao :00 (02h), base #151 (registadas antes de correr)
    "k-sma50-d-btc50-bracket-s2-rx": (sma_btc50_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma50-d-btc50up-bracket-s2": (sma_btc50up_entry(50), "1d", 2.0, 1.0, 0),
    "k-sma50-d-btc50-bracket-s15": (sma_btc50_entry(50), "1d", 1.5, 1.0, 0),
    "k-sma20-d-btc50-bracket-s2": (sma_btc50_entry(20), "1d", 2.0, 1.0, 0),
}

# saidas extra por ideia (argumentos de run_positions): partial = fracao fechada no alvo tp_r (resto com stop em breakeven);
# be = so passa o stop para breakeven ao tocar tp_r (nao fecha nada)
EXITS = {
    "k-persist-bw-half": {"partial": 0.5},
    "k-dc20-4h-bw-half": {"partial": 0.5},
    "k-dc20-4h-bw-be": {"be": True},
    "k-dc20-d-own-be": {"be": True},
    "k-sma100-d-bull-bracket": {"signal_exit": False},
    "k-sma600-4h-bull-bracket": {"signal_exit": False},
    "k-sma100-d-bull-bracket-mh10": {"signal_exit": False},
    "k-sma100-d-own-bracket": {"signal_exit": False},
    "k-sma100-d-bull-bracket-s2": {"signal_exit": False},
    "k-sma100-d-bull-bracket-s2-mh10": {"signal_exit": False},
    "k-sma50-d-bull-bracket-s2": {"signal_exit": False},
    "k-ema100-d-bull-bracket-s2": {"signal_exit": False},
    "k-sma100-d-bull50-bracket-s2": {"signal_exit": False},
    "k-sma50-d-bull50-bracket-s2": {"signal_exit": False},
    "k-sma100-d-bull50-bracket-s2-tp075": {"signal_exit": False},
    "k-sma100-d-bull50-mom7-bracket-s2": {"signal_exit": False},
    "k-sma100-d-bull50-red-bracket-s2": {"signal_exit": False},
    "k-sma50-d-btc50-bracket-s2": {"signal_exit": False},
    "k-sma50-d-bull50-bracket-s2-lose7": {"signal_exit": False, "lose_hold": 7},
    "k-sma50up-d-bull50-bracket-s2": {"signal_exit": False},
    "k-sma50-d-bull50-bracket-s2-rx": {"signal_exit": False, "exit_fn": btc_regime_off(50)},
    "k-sma50-d-btc50-bracket-s2-rx": {"signal_exit": False, "exit_fn": btc50_off(50)},
    "k-sma50-d-btc50up-bracket-s2": {"signal_exit": False},
    "k-sma50-d-btc50-bracket-s15": {"signal_exit": False},
    "k-sma20-d-btc50-bracket-s2": {"signal_exit": False},
}


# ---------------- SCALPING CRIPTO (2026-11-21, pedido do Antonio: trades de minutos a poucas horas, varias por semana) ----------------
# Todas com versao long e short (o Antonio quer shorts). Long = +1, short = -1. Sem filtro de risco minimo (ver SCALP_EXITS):
# o custo em R aparece todo no resultado.

def _ema(c: pd.Series, n: int) -> pd.Series:
    return c.ewm(span=n, adjust=False).mean()


def _side(sig_long: pd.Series, sig_short: pd.Series, side: str) -> pd.Series:
    if side == "long":
        return sig_long.astype(float)
    return -sig_short.astype(float)


def scalp_bb_rev(side: str):
    """Reversao a media em 5m: fecho fora da banda de Bollinger (20, 2.5 desvios) a favor da tendencia de 1h (EMA 600 de 5m
    ~ 50h). Long: fecho < banda de baixo e fecho > EMA600. Sai quando volta a media de 20 (sinal desliga) ou ao fim de 2h."""
    def f(b):
        c = b["close"]
        m, sd = c.rolling(20).mean(), c.rolling(20).std()
        tr = _ema(c, 600)
        lo = (c < m - 2.5 * sd) & (c > tr)
        hi = (c > m + 2.5 * sd) & (c < tr)
        # posicao mantida ate o fecho cruzar a media de 20
        L = _enter_exit(lo, c >= m)
        S = _enter_exit(hi, c <= m)
        return _side(L > 0, S > 0, side)
    return f


def scalp_orb_us(side: str):
    """Abertura de Nova Iorque em 15m: maximo/minimo das 9:30-10:30 NY. Long no 1.o fecho acima do maximo depois das 10:30,
    short no 1.o fecho abaixo do minimo. Uma entrada por dia e por lado. Sai no stop, no alvo 2R ou ao fim de 22 velas (~16:00 NY)."""
    def f(b):
        ny = b.index.tz_convert("America/New_York")
        hm = ny.hour * 60 + ny.minute
        day = pd.Series(ny.normalize(), index=b.index)
        win = (hm >= 570) & (hm < 630)
        hi = b["high"].where(win).groupby(day.values).transform("max")
        lo = b["low"].where(win).groupby(day.values).transform("min")
        after = (hm >= 630) & (hm < 945)
        up = after & (b["close"] > hi)
        dn = after & (b["close"] < lo)
        first_up = up & (up.groupby(day.values).cumsum() == 1)
        first_dn = dn & (dn.groupby(day.values).cumsum() == 1)
        return _side(first_up, first_dn, side)
    return f


def scalp_rsi2(side: str):
    """RSI(2) em 15m a favor da tendencia (EMA 200 de 15m ~ 2 dias). Long: RSI(2) < 5 e fecho > EMA200; sai com RSI(2) > 60
    ou ao fim de 16 velas (4h). Short espelho: RSI(2) > 95 e fecho < EMA200; sai com RSI(2) < 40."""
    def f(b):
        c = b["close"]
        r = _rsi(c, 2)
        tr = _ema(c, 200)
        L = _enter_exit((r < 5) & (c > tr), r > 60)
        S = _enter_exit((r > 95) & (c < tr), r < 40)
        return _side(L > 0, S > 0, side)
    return f


def scalp_burst(side: str):
    """Explosao de momentum em 15m: vela com amplitude > 2.5x ATR(14) que fecha no quarto de cima (long) ou de baixo (short),
    a favor da EMA 200. Entra na abertura seguinte; alvo 1.5R, stop 1.5 ATR, maximo 8 velas (2h)."""
    def f(b):
        h, l, c = b["high"], b["low"], b["close"]
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        a = tr.rolling(14).mean().shift()
        rng = h - l
        pos = (c - l) / rng.replace(0, np.nan)
        e = _ema(c, 200)
        up = (rng > 2.5 * a) & (pos > 0.75) & (c > e)
        dn = (rng > 2.5 * a) & (pos < 0.25) & (c < e)
        return _side(up, dn, side)
    return f


SCALP = {
    # nome: (funcao, timeframe, stop em ATR, alvo R, max velas)
    "s-bb-rev-5m": (scalp_bb_rev, "5m", 2.0, 0.0, 24),
    "s-orb-us-15m": (scalp_orb_us, "15m", 1.5, 2.0, 22),
    "s-rsi2-15m": (scalp_rsi2, "15m", 2.0, 0.0, 16),
    "s-burst-15m": (scalp_burst, "15m", 1.5, 1.5, 8),
}
for _n, (_fn, _tf, _st, _tp, _mh) in SCALP.items():
    for _sd in ("long", "short"):
        IDEAS[f"{_n}-{_sd}"] = (_fn(_sd), _tf, _st, _tp, _mh)
        # pulsos (orb, burst) so servem para entrar
        if _n in ("s-orb-us-15m", "s-burst-15m"):
            EXITS[f"{_n}-{_sd}"] = {"signal_exit": False}
# o motor por defeito exige stop >= 4x custos (apagaria quase todos os scalps): nos scalps o custo entra todo no resultado
NO_MIN_RISK = {f"{_n}-{_sd}" for _n in SCALP for _sd in ("long", "short")}


# ---------------- SHORTS DA K1 (2026-11-21, pedido do Antonio: a demo abrir shorts) ----------------
def mirror(fn):
    """Estrategia ao espelho: corre a regra long sobre o preco invertido (1/preco) e devolve -1 onde ela compraria.
    Rutura de maximo -> rutura de minimo, acima da media -> abaixo da media."""
    def f(b):
        inv = pd.DataFrame({"open": 1 / b["open"], "high": 1 / b["low"], "low": 1 / b["high"], "close": 1 / b["close"]},
                           index=b.index)
        return -fn(inv).clip(lower=0)
    return f


for _k in ("k-donchian20-d", "k-sma100-d", "k-donchian55-4h", "k-sma200-4h"):
    _fn, _tf, _st, _tp, _mh = IDEAS[_k]
    IDEAS[_k + "-short"] = (mirror(_fn), _tf, _st, _tp, _mh)


def bear_only(fn):
    """So mantem o short enquanto o BTC fechou o dia anterior abaixo da media de 200 dias (espelho do regime dos longs)."""
    def f(b):
        s = fn(b)
        bull = _regime(b, 200)
        return s.where(~bull.reindex(s.index).fillna(True).astype(bool), 0.0)
    return f


for _k in ("k-donchian20-d", "k-sma100-d", "k-donchian55-4h", "k-sma200-4h"):
    _fn, _tf, _st, _tp, _mh = IDEAS[_k + "-short"]
    IDEAS[_k + "-short-bear"] = (bear_only(_fn), _tf, _st, _tp, _mh)


# ---------------- INTRADAY 1h-1 DIA (2026-11-21, pedido do Antonio: 3-4 trades por semana, sem ficar dias em trade) ----------------
def _bull_1h(b):
    c = b["close"]
    return (c > _ema(c, 200)) & _regime(b, 200).reindex(b.index).fillna(False).astype(bool)


def h_rsi2():
    def f(b):
        r = _rsi(b["close"], 2)
        return _enter_exit((r < 10) & _bull_1h(b), r > 70).astype(float)
    return f


def h_low12():
    def f(b):
        c = b["close"]
        return ((c <= c.rolling(12).min()) & _bull_1h(b)).astype(float)
    return f


def h_dc24():
    def f(b):
        c = b["close"]
        return ((c > b["high"].rolling(24).max().shift(1)) & _bull_1h(b)).astype(float)
    return f


def h_squeeze():
    def f(b):
        c = b["close"]
        m, sd = c.rolling(20).mean(), c.rolling(20).std()
        w = (4 * sd / m)
        sq = w.shift(1) <= w.shift(1).rolling(120).min()
        return ((c > m + 2 * sd) & sq & _bull_1h(b)).astype(float)
    return f


INTRADAY = {
    "h-rsi2-1h": (h_rsi2(), "1h", 3.0, 0.0, 24),
    "h-low12-tp-1h": (h_low12(), "1h", 3.0, 1.0, 24),
    "h-dc24-1h": (h_dc24(), "1h", 3.0, 2.0, 24),
    "h-squeeze-1h": (h_squeeze(), "1h", 3.0, 2.0, 24),
}
IDEAS.update(INTRADAY)
for _n in ("h-low12-tp-1h", "h-dc24-1h", "h-squeeze-1h"):
    EXITS[_n] = {"signal_exit": False}      # pulsos: so servem para entrar
NO_MIN_RISK |= set(INTRADAY)


# ---------------- PERPETUOS: SHORTS INTRADAY (2026-11-21) ----------------
def _bear_1h(b):
    c = b["close"]
    bull = _regime(b, 200).reindex(b.index).fillna(True).astype(bool)
    return (c < _ema(c, 200)) & ~bull


def h_dc24_short():
    def f(b):
        c = b["close"]
        return -((c < b["low"].rolling(24).min().shift(1)) & _bear_1h(b)).astype(float)
    return f


def h_rsi2_short():
    def f(b):
        r = _rsi(b["close"], 2)
        return -_enter_exit((r > 90) & _bear_1h(b), r < 30).astype(float)
    return f


IDEAS["h-dc24-1h-short"] = (h_dc24_short(), "1h", 3.0, 2.0, 24)
IDEAS["h-rsi2-1h-short"] = (h_rsi2_short(), "1h", 3.0, 0.0, 24)
EXITS["h-dc24-1h-short"] = {"signal_exit": False}
NO_MIN_RISK |= {"h-dc24-1h-short", "h-rsi2-1h-short"}


# ---------------- ENTRAR NOS LONGS MAIS CEDO (2026-11-22, pedido do Antonio) ----------------
def _atr_s(b, n=14):
    h, l, c = b["high"], b["low"], b["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def r_hi_dd(n_hi: int, n_max: int, dd: float = 0.30):
    def f(b):
        c = b["close"]
        brk = c > b["high"].rolling(n_hi).max().shift(1)
        deep = c <= (1 - dd) * b["high"].rolling(n_max).max()
        return (brk & deep).astype(float)
    return f


def r_btc_reclaim20():
    def f(b):
        c = b["close"]
        bull200 = btc_bull_regime(b.index, n=200)
        bull20 = btc_bull_regime(b.index, n=20)
        if bull200 is None or bull20 is None:
            bull200 = (c > c.rolling(200).mean()).shift(1).fillna(False)
            bull20 = (c > c.rolling(20).mean()).shift(1).fillna(False)
        return ((~bull200.astype(bool)) & bull20.astype(bool) & (c > c.rolling(20).mean())).astype(float)
    return f


def r_capit():
    def f(b):
        c, h = b["close"], b["high"]
        a = _atr_s(b).shift(1)
        crash = (c.shift(1) - c) > 3 * a          # dia que caiu mais de 3 ATR
        hi_crash = h.where(crash).ffill(limit=5)
        recent = crash.rolling(5).max().shift(1).fillna(0).astype(bool)
        return (recent & (c > hi_crash.shift(1))).astype(float)
    return f


for _n, _v in {
    "r-hi10-dd-d": (r_hi_dd(10, 100), "1d", 3.0, 1.0, 10),
    "r-btc-reclaim20-d": (r_btc_reclaim20(), "1d", 2.0, 1.0, 10),
    "r-hi10-dd-4h": (r_hi_dd(60, 600), "4h", 3.0, 1.0, 60),
    "r-capit-d": (r_capit(), "1d", 3.0, 1.0, 5),
}.items():
    IDEAS[_n] = _v
    EXITS[_n] = {"signal_exit": False}


# ---------------- TRADES MAIS CURTAS (2026-11-22) ----------------
IDEAS["k-sma50-d-bull-bracket-s2-mh3"] = (sma_bull_entry(50), "1d", 2.0, 1.0, 3)
IDEAS["k-sma600-4h-bull-bracket-mh12"] = (sma_bull_entry(600), "4h", 3.0, 1.0, 12)
EXITS["k-sma50-d-bull-bracket-s2-mh3"] = dict(EXITS.get("k-sma50-d-bull-bracket-s2", {}))
EXITS["k-sma600-4h-bull-bracket-mh12"] = dict(EXITS.get("k-sma600-4h-bull-bracket", {}))


# ---------------- MERCADO EM BAIXA: SHORTS (2026-11-23, prioridade da noite) ----------------
def _btc_bear(b):
    """BTC fechou o dia anterior abaixo da media de 200 dias (o contrario de _regime; sem dados conta como baixa, como a demo)."""
    return ~_regime(b, 200).reindex(b.index).fillna(False).astype(bool)


def sma_bear_entry(n: int):
    """Espelho de sma_bull_entry: fecho abaixo da media de n velas e BTC em baixa -> -1 (short). So para entrar."""
    def f(b):
        c = b["close"]
        sma = c.rolling(n).mean()
        return -((c < sma) & sma.notna() & _btc_bear(b)).astype(float)
    return f


def dc_bear_entry(n: int):
    """Fecho abaixo do minimo das n velas anteriores e BTC em baixa -> -1 (short). So para entrar."""
    def f(b):
        c = b["close"]
        return -((c < b["low"].rolling(n).min().shift(1)) & _btc_bear(b)).astype(float)
    return f


for _n, _v in {
    "s-sma50-d-bear-bracket-s2-mh3": (sma_bear_entry(50), "1d", 2.0, 1.0, 3),
    "s-sma100-d-bear-bracket-mh10": (sma_bear_entry(100), "1d", 3.0, 1.0, 10),
    "s-sma600-4h-bear-bracket": (sma_bear_entry(600), "4h", 3.0, 1.0, 0),
    "s-dc20-d-bear-bracket-s2-mh5": (dc_bear_entry(20), "1d", 2.0, 1.0, 5),
}.items():
    IDEAS[_n] = _v
    EXITS[_n] = {"signal_exit": False}


# ---------------- MERCADO EM BAIXA: RESSALTOS EM LONG (2026-11-23, prioridade da noite) ----------------
def rsi2_bear_entry(lo: float):
    """RSI(2) < lo e BTC em baixa -> 1 (long). So para entrar (igual a familia rsi2 da demo, btc "bear")."""
    def f(b):
        r = _rsi(b["close"], 2)
        return ((r < lo) & _btc_bear(b)).astype(float)
    return f


def low_bear_entry(n: int):
    """Fecho e o mais baixo das ultimas n velas e BTC em baixa -> 1 (long). So para entrar (familia lowclose)."""
    def f(b):
        c = b["close"]
        return ((c <= c.rolling(n).min()) & _btc_bear(b)).astype(float)
    return f


for _n, _v in {
    "l-rsi2-d-bear-s2-tp05-mh2": (rsi2_bear_entry(10), "1d", 2.0, 0.5, 2),
    "l-low10-d-bear-s2-tp1-mh3": (low_bear_entry(10), "1d", 2.0, 1.0, 3),
    "l-rsi2-4h-bear-s2-tp1-mh6": (rsi2_bear_entry(10), "4h", 2.0, 1.0, 6),
    "l-low30-4h-bear-s3-tp05-mh12": (low_bear_entry(30), "4h", 3.0, 0.5, 12),
}.items():
    IDEAS[_n] = _v
    EXITS[_n] = {"signal_exit": False}


# ---------------- BAIXA SEPARADA PELA INCLINACAO DA MEDIA 200 DO BTC (2026-11-23, sessao 01h) ----------------
def btc_sma_slope_up(index: pd.DatetimeIndex, n: int = 200, k: int = 20) -> pd.Series | None:
    """True quando, no dia anterior fechado, a media de n dias do BTC estava acima do valor de k dias antes."""
    if len(index) == 0:
        return pd.Series(False, index=index, dtype=bool)
    try:
        from .swing import load_tf
        btc_daily = load_tf("btc", "1d", None)
    except Exception:
        return None
    if index.tz is None or len(btc_daily) < n + k + 1 or index[-1] < btc_daily.index[0] + pd.Timedelta(days=n + k):
        return None
    sma = btc_daily["close"].rolling(n).mean()
    up = (sma > sma.shift(k)).astype(float).where(sma.shift(k).notna())
    up.index = up.index + pd.Timedelta(days=1)
    out = up.reindex(up.index.union(index)).ffill().reindex(index)
    return out.fillna(0).astype(bool)


def _slope_up(b, n: int = 200, k: int = 20):
    r = btc_sma_slope_up(b.index, n, k)
    if r is None:   # sem dados do BTC: inclinacao da propria serie (so passado)
        s = b["close"].rolling(n).mean()
        r = (s > s.shift(k)).shift(1).fillna(False).astype(bool)
    return r.reindex(b.index).fillna(False).astype(bool)


def with_slope(entry_fn, want_up: bool):
    """Mantem o sinal de entry_fn so quando a media 200 do BTC esta a subir (want_up) ou a descer (not want_up)."""
    def f(b):
        s = entry_fn(b)
        up = _slope_up(b)
        mask = up if want_up else ~up
        return s.where(mask, 0.0)
    return f


for _n, _v in {
    "s-sma50-d-bear200dn-bracket-s2-mh3": (with_slope(sma_bear_entry(50), False), "1d", 2.0, 1.0, 3),
    "s-sma600-4h-bear200dn-bracket": (with_slope(sma_bear_entry(600), False), "4h", 3.0, 1.0, 0),
    "l-rsi2-4h-bear200up-s2-tp1-mh6": (with_slope(rsi2_bear_entry(10), True), "4h", 2.0, 1.0, 6),
    "l-low30-4h-bear200up-s3-tp05-mh12": (with_slope(low_bear_entry(30), True), "4h", 3.0, 0.5, 12),
}.items():
    IDEAS[_n] = _v
    EXITS[_n] = {"signal_exit": False}


# ---------------- MERCADO EM BAIXA: VENDER RESSALTOS (2026-11-23, sessao 01h30) ----------------
def rsi2hi_bear_entry(hi: float, trend_ema: int = 0):
    """RSI(2) > hi e BTC em baixa -> -1 (short). Com trend_ema: tambem fecho abaixo da EMA(trend_ema) da propria moeda.
    Igual a familia rsi2 da demo com side -1 (r > 100 - lo) e btc "bear"."""
    def f(b):
        c = b["close"]
        sig = (_rsi(c, 2) > hi) & _btc_bear(b)
        if trend_ema:
            sig = sig & (c < _ema(c, trend_ema))
        return -sig.astype(float)
    return f


for _n, _v in {
    "s-rsi2hi-d-bear-s2-tp1-mh3": (rsi2hi_bear_entry(90), "1d", 2.0, 1.0, 3),
    "s-rsi2hi-4h-bear-s2-tp1-mh6": (rsi2hi_bear_entry(90), "4h", 2.0, 1.0, 6),
    "s-rsi2hi-4h-bear-s3-tp05-mh12": (rsi2hi_bear_entry(90), "4h", 3.0, 0.5, 12),
    "s-rsi2hi-4h-bear-ema200-s2-tp1-mh6": (rsi2hi_bear_entry(90, 200), "4h", 2.0, 1.0, 6),
}.items():
    IDEAS[_n] = _v
    EXITS[_n] = {"signal_exit": False}
