"""O bot da demo (live/c5_live.py) tem de tomar as MESMAS decisoes que o backtest da carteira.
Repete os dias um a um com velas diarias do NQ (sem domingos, como no MT5) e compara as entradas com o backtest."""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from live import c5_live as L  # noqa: E402
from sr.data import SPEC, m5_path  # noqa: E402
from sr.swing import FUT_COST, load_tf, run_positions  # noqa: E402
from sr.swing_ideas import IDEAS  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(m5_path("nq")), reason="sem dados")


def _bars():
    b = load_tf("nq", "1d", "dev")
    b = b[b.index.tz_localize(None).dayofweek < 5]
    b.index = b.index.tz_localize(None)
    return b.loc[:"2021-12-31"]


def _backtest(b):
    """Mesmo filtro que portfolio.py so com o NQ: 1 trade de cada vez, paragem mensal a -3R."""
    rows = []
    for ideia in L.IDEIAS:
        fn, tf, st, tp, mh = IDEAS[ideia]
        tr = run_positions(b, fn(b), st, SPEC["nq"]["cost_pts"], FUT_COST["nq"], tp, mh)
        for t in tr.itertuples():
            rows.append((t.time, L.IDEIAS.index(ideia), ideia, t.exit, t.R))
    rows.sort(key=lambda r: (r[0], r[1]))
    keep, aberta, fechadas = [], None, []
    for t0, _, ideia, t1, r in rows:
        if aberta and aberta[0] < t0:
            fechadas.append(aberta)
            aberta = None
        if aberta:
            continue
        if sum(x[1] for x in fechadas if (x[0].year, x[0].month) == (t0.year, t0.month)) <= -3:
            continue
        aberta = (t1, r)
        keep.append((t0.strftime("%Y-%m-%d"), ideia))
    return keep, {(t0.strftime("%Y-%m-%d"), ideia): (t1, r) for t0, _, ideia, t1, r in rows}


def test_bot_igual_ao_backtest():
    b = _bars()
    esperado, info = _backtest(b)
    pos, feitas, fechadas = [], [], []
    for i in range(300, len(b)):
        dia = b.index[i].strftime("%Y-%m-%d")
        est = {("nq", ideia): L.motor_agora(b.iloc[:i], ideia, "nq", float(b["open"].iloc[i])) for ideia in L.IDEIAS}
        mes = sum(r for t1, r in fechadas if (t1.year, t1.month) == (b.index[i].year, b.index[i].month))
        for a in L.decidir(est, pos, mes, ["nq"]):
            if a[0] == "fechar":
                pos.remove(a[1])
                fechadas.append(info[(a[1]["dia"], a[1]["ideia"])])
            elif a[0] == "abrir":
                pos.append({"mk": "nq", "ideia": a[2], "dia": dia})
                feitas.append((dia, a[2]))
    inicio = b.index[300].strftime("%Y-%m-%d")
    esperado = [e for e in esperado if e[0] >= inicio]
    assert len(feitas) > 20
    assert feitas == esperado


def test_lotes_nunca_arrisca_mais_de_1pct():
    assert L.lotes(100.0, 30.0, 0.01, 0.01, 100) == 3.33
    assert L.lotes(100.0, 300.0, 1.0, 1.0, 100) == 0.0          # minimo arriscaria mais de 1%: nao entra
    assert L.lotes(100.0, 7.0, 0.1, 0.1, 100) * 7.0 <= 100.0


def test_regras_de_risco():
    nova = {"nova": True, "dia": "hoje", "risk": 10.0}
    est = {(mk, "rsi2-dip-d"): nova for mk in ("nq", "es", "dax", "ftse", "nikkei")}
    acoes = L.decidir(est, [], 0.0, ["nq", "es", "dax", "ftse", "nikkei"])
    abre = [a[1] for a in acoes if a[0] == "abrir"]
    assert abre == ["nq", "dax", "nikkei"]                      # 1 por regiao, max 3
    acoes = L.decidir(est, [], -3.2, ["nq"])
    assert [a[0] for a in acoes] == ["saltar"]                   # paragem mensal
