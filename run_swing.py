"""
Corre uma ideia de prazo mais longo (sr/swing_ideas.py) nos 3 indices, com custos de CFD e de micro-futuros.
  python run_swing.py --idea trend-sma100-d
  python run_swing.py --idea ... --period holdout --unlock-holdout
O veredicto oficial usa custos de CFD (a conta que o Antonio tem). Se so passar com futuros, fica assinalado.
Criterio: >= 60 trades por indice (prazo longo tem menos trades), meanR > 0 em cada indice, t junto >= 3.0.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

import pandas as pd

import run as R
from sr import supa
from sr.data import PERIODS, SPEC
from sr.stats import by_year, summarize
from sr.swing import FUT_COST, load_tf, run_positions
from sr.swing_ideas import IDEAS

MIN_T, MIN_N = 3.0, 60


def verdict(per: dict, t: float) -> str:
    if any(s["n"] < MIN_N for s in per.values()):
        return f"REPROVADA (poucas trades, < {MIN_N})"
    if any(s["meanR"] <= 0 for s in per.values()):
        return "REPROVADA (negativa em pelo menos 1 indice)"
    if t < MIN_T:
        return f"REPROVADA (t < {MIN_T:g})"
    return "PASSA"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--idea", required=True, choices=sorted(IDEAS))
    ap.add_argument("--period", default="dev", choices=list(PERIODS))
    ap.add_argument("--unlock-holdout", action="store_true")
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()
    if a.period == "holdout" and not a.unlock_holdout:
        raise SystemExit("O holdout esta FECHADO. Ver CLAUDE.md.")
    fn, tf, stop_atr, tp_r, max_hold = IDEAS[a.idea]
    out = {}
    for model in ("cfd", "fut"):
        per, allt, yearly, curves, periods = {}, [], {}, {}, {}
        for key in ("nq", "es", "dow"):
            b = load_tf(key, tf, a.period)
            tr = run_positions(b, fn(b), stop_atr, SPEC[key]["cost_pts"], FUT_COST[key], tp_r, max_hold)
            if model == "fut" and len(tr):
                tr = tr.assign(R=tr["R_fut"])
            yrs = max((b.index[-1] - b.index[0]).days / 365.25, 0.1)
            per[key] = summarize(tr, yrs)
            yearly[key] = by_year(tr)
            curves[key] = R.equity_curve(tr)
            periods[key] = R.period_tables(tr)
            if len(tr):
                allt.append(tr)
        pooled = summarize(pd.concat(allt) if allt else None, 1.0)
        periods["all"] = R.period_tables(pd.concat(allt) if allt else None)
        out[model] = dict(per=per, pooled=pooled, yearly=yearly, curves=curves, periods=periods,
                          verdict=verdict(per, pooled["t"]))
    cfd, fut = out["cfd"], out["fut"]
    vd = cfd["verdict"]
    if not vd.startswith("PASSA") and fut["verdict"].startswith("PASSA"):
        vd += " - mas PASSA com micro-futuros"
    name = f"{a.idea}"
    print(f"Ideia: {name} ({tf}) | periodo: {a.period}")
    for model in ("cfd", "fut"):
        print(f"\n[{model}]")
        print(pd.DataFrame(out[model]["per"]).T.to_string())
        print(f"Junto: n={out[model]['pooled']['n']} meanR={out[model]['pooled']['meanR']} t={out[model]['pooled']['t']}"
              f" -> {out[model]['verdict']}")
    print(f"\nVEREDICTO: {vd}")
    if a.no_log:
        return
    os.makedirs(R.RUNS_DIR, exist_ok=True)
    doc = {"variant": name, "params": {"play": "swing", "levels": a.idea, "tf": tf, "stop_atr": stop_atr,
                                         "tp_r": tp_r, "max_hold": max_hold, "custos": "cfd (fut em markets_fut)"},
           "period": a.period, "date": datetime.now().astimezone().isoformat(timespec="minutes"), "verdict": vd,
           "pooled": cfd["pooled"], "markets": cfd["per"],
           "yearly": {k: {str(y): float(r) for y, r in s.items()} for k, s in cfd["yearly"].items()},
           "equity": cfd["curves"], "periods": cfd["periods"],
           "fut": {"markets": fut["per"], "pooled": fut["pooled"], "verdict": fut["verdict"]}}
    with open(os.path.join(R.RUNS_DIR, f"{name}__{a.period}.json"), "w") as f:
        json.dump(doc, f)
    cell = lambda k: f"{cfd['per'][k]['n']} / {cfd['per'][k]['meanR']:+.3f} / {cfd['per'][k]['t']:+.2f}"
    with open(R.RESULTS, "a") as f:
        f.write(f"| {datetime.now():%Y-%m-%d %H:%M} | `{name}` ({tf}) | {a.period} | {cell('nq')} | {cell('es')} | "
                f"{cell('dow')} | {cfd['pooled']['t']:+.2f} | {cfd['per']['nq']['R/mes']} | {vd} |\n")
    if supa.report_run(doc):
        print("(enviado para o dashboard)")


if __name__ == "__main__":
    main()
