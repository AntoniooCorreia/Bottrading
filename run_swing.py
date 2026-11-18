"""
Corre uma ideia de prazo mais longo (sr/swing_ideas.py) nos 3 indices, com custos de CFD e de micro-futuros.
  python run_swing.py --idea trend-sma100-d
  python run_swing.py --idea ... --period holdout --unlock-holdout
Desde 2026-11-18 (decisao do Antonio: vai operar FUTUROS, nao CFDs) o veredicto oficial usa custos de micro-futuros
(--custos fut, por defeito; o nome da variante leva '-fut'). --custos cfd repete o modelo antigo.
Mostra tambem quanto arrisca 1 micro-contrato no stop (MNQ/MES/MYM) e a conta minima para isso ser 1%.
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
MICRO_RISK: dict = {}   # stop mediano em pontos por indice (preenchido na corrida)


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
    ap.add_argument("--custos", default="fut", choices=["fut", "cfd"], help="modelo de custos do veredicto oficial")
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
            if len(tr):
                MICRO_RISK[key] = float(tr["risk_pts"].median())
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
    if a.custos == "fut":     # o modelo oficial passa a ser o de futuros; o outro fica guardado como alternativa
        cfd, fut = fut, cfd
    vd = cfd["verdict"]
    name = f"{a.idea}-fut" if a.custos == "fut" else f"{a.idea}"
    print(f"Ideia: {name} ({tf}) | periodo: {a.period}")
    for model in ("cfd", "fut"):
        print(f"\n[{model}]")
        print(pd.DataFrame(out[model]["per"]).T.to_string())
        print(f"Junto: n={out[model]['pooled']['n']} meanR={out[model]['pooled']['meanR']} t={out[model]['pooled']['t']}"
              f" -> {out[model]['verdict']}")
    print(f"\nVEREDICTO ({a.custos}): {vd}")
    for key, (pv, nm) in {"nq": (2.0, "MNQ"), "es": (5.0, "MES"), "dow": (0.5, "MYM")}.items():
        rk = MICRO_RISK.get(key)
        if rk:
            print(f"  {nm}: stop mediano {rk:.0f} pontos = {rk * pv:,.0f} USD por contrato -> conta minima para 1%: {rk * pv * 100:,.0f} USD")
    if a.no_log:
        return
    os.makedirs(R.RUNS_DIR, exist_ok=True)
    doc = {"variant": name, "params": {"play": "swing", "levels": a.idea, "tf": tf, "stop_atr": stop_atr,
                                         "tp_r": tp_r, "max_hold": max_hold, "custos": a.custos},
           "period": a.period, "date": datetime.now().astimezone().isoformat(timespec="minutes"), "verdict": vd,
           "pooled": cfd["pooled"], "markets": cfd["per"],
           "yearly": {k: {str(y): float(r) for y, r in s.items()} for k, s in cfd["yearly"].items()},
           "equity": cfd["curves"], "periods": cfd["periods"],
           "fut": {"markets": fut["per"], "pooled": fut["pooled"], "verdict": fut["verdict"]},
           "micro_risco_usd": {k: round(v * {"nq": 2.0, "es": 5.0, "dow": 0.5}[k]) for k, v in MICRO_RISK.items()}}
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
