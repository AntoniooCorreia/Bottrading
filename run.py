"""
Corre UMA variante de suporte/resistencia nos 3 indices e regista o resultado em results/RESULTS.md

  python run.py --play bounce --levels pdhl --tp 2 --stop-atr 0.5
  python run.py --play fake --levels swing1h --tp 1.5 --fake-atr 0.3 --session all
  python run.py ... --period holdout --unlock-holdout      # SO depois de passar no dev (ver CLAUDE.md)

Criterio de aprovacao no periodo dev (fixo, nao mexer):
  * >= 100 trades em CADA indice
  * meanR > 0 em CADA indice (depois de custos)
  * t-stat dos 3 indices juntos >= 2.5
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

import pandas as pd

from sr.data import INSTR, PERIODS, SPEC, load_m5
from sr.engine import Variant, backtest
from sr.stats import by_year, summarize

RESULTS = os.path.join("results", "RESULTS.md")
HOLDOUT_LOG = "HOLDOUT_LOG.md"
HEADER = ("| data | variante | periodo | NQ n / meanR / t | ES n / meanR / t | Dow n / meanR / t | "
          "junto t | R/mes (NQ) | veredicto |\n|---|---|---|---|---|---|---|---|---|\n")


def verdict(per: dict, pooled_t: float) -> str:
    if any(s["n"] < 100 for s in per.values()):
        return "REPROVADA (poucas trades)"
    if any(s["meanR"] <= 0 for s in per.values()):
        return "REPROVADA (negativa em pelo menos 1 indice)"
    if pooled_t < 2.5:
        return "REPROVADA (t < 2.5)"
    return "PASSA"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--play", default="bounce", choices=["bounce", "break", "fake"])
    ap.add_argument("--levels", default="pdhl", choices=["pdhl", "pwhl", "swing1h", "round"])
    ap.add_argument("--tp", type=float, default=2.0)
    ap.add_argument("--stop-atr", type=float, default=0.5)
    ap.add_argument("--fake-atr", type=float, default=0.3)
    ap.add_argument("--session", default="rth", choices=["rth", "all"])
    ap.add_argument("--period", default="dev", choices=list(PERIODS))
    ap.add_argument("--unlock-holdout", action="store_true")
    ap.add_argument("--markets", default="nq,es,dow")
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()

    if a.period == "holdout" and not a.unlock_holdout:
        raise SystemExit("O holdout esta FECHADO. Ver regras em CLAUDE.md antes de usar --unlock-holdout.")

    v = Variant(play=a.play, levels=a.levels, tp_r=a.tp, stop_atr=a.stop_atr, fake_atr=a.fake_atr, session=a.session)
    per, all_tr, yearly = {}, [], {}
    for key in a.markets.split(","):
        m5 = load_m5(key, a.period)
        yrs = max((m5.index[-1] - m5.index[0]).days / 365.25, 0.1)
        tr = backtest(m5, v, SPEC[key]["cost_pts"], SPEC[key]["round"])
        per[key] = summarize(tr, yrs)
        yearly[key] = by_year(tr)
        if len(tr):
            all_tr.append(tr.assign(market=key))
    pooled = summarize(pd.concat(all_tr) if all_tr else None, 1.0)
    vd = verdict(per, pooled["t"])

    print(f"Variante: {v.name()}  |  periodo: {a.period}")
    print(pd.DataFrame(per).T.to_string())
    print(f"\nJunto: n={pooled['n']} meanR={pooled['meanR']} t={pooled['t']}")
    print("\nR por ano:")
    print(pd.DataFrame(yearly).fillna(0).to_string())
    print(f"\nVEREDICTO: {vd}")

    if a.no_log:
        return
    os.makedirs("results", exist_ok=True)
    if not os.path.exists(RESULTS):
        with open(RESULTS, "w") as f:
            f.write("# Resultados (gerado por run.py - nao editar a mao)\n\n" + HEADER)
    cell = lambda k: (f"{per[k]['n']} / {per[k]['meanR']:+.3f} / {per[k]['t']:+.2f}" if k in per else "-")
    with open(RESULTS, "a") as f:
        f.write(f"| {datetime.now():%Y-%m-%d %H:%M} | `{v.name()}` | {a.period} | {cell('nq')} | {cell('es')} | "
                f"{cell('dow')} | {pooled['t']:+.2f} | {per.get('nq', {}).get('R/mes', 0)} | {vd} |\n")
    if a.period == "holdout":
        with open(HOLDOUT_LOG, "a") as f:
            f.write(f"- {datetime.now():%Y-%m-%d %H:%M} `{v.name()}` -> {vd} | {json.dumps(per)}\n")


if __name__ == "__main__":
    main()
