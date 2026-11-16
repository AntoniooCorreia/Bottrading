"""
Carteira: corre varias ideias (sr/swing_ideas.py) em varios indices ao mesmo tempo, cada trade com 1% de risco,
e mostra quanto daria por ano no total. E isto que mede o objetivo do Antonio (>= +14% ao ano).
  python portfolio.py --ideas rsi2-dip-d                 # todos os indices disponiveis, 2012-2024
  python portfolio.py --ideas rsi2-dip-d,outra --markets nq,dax,ftse --period tudo
Nunca usa o holdout. Envia o resumo para o dashboard (estado "portfolio") se BT_WRITE_TOKEN existir.
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from sr import supa
from sr.data import CARTEIRA, PERIODS, SPEC, m5_path
from sr.swing import FUT_COST, load_tf, run_positions
from sr.swing_ideas import IDEAS

OBJETIVO = 14.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--markets", default=",".join(CARTEIRA))
    ap.add_argument("--period", default="tudo", choices=[p for p in PERIODS if p != "holdout"])
    ap.add_argument("--only", default="", help="lista indice:ideia a usar (ex.: nq:rsi2-dip-d,es:ibs-dip-d)")
    ap.add_argument("--max-open", type=int, default=3,
                    help="maximo de trades abertas ao mesmo tempo (risco total maximo = max_open %%)")
    a = ap.parse_args()
    ideas = a.ideas.split(",")
    rows, trades = [], []
    for key in a.markets.split(","):
        if not os.path.exists(m5_path(key)):
            print(f"  {key}: sem dados (python download.py 2012 2026 {key})")
            continue
        for name in ideas:
            if a.only and f"{key}:{name}" not in a.only.split(","):
                continue
            fn, tf, st, tp, mh = IDEAS[name]
            b = load_tf(key, tf, a.period)
            tr = run_positions(b, fn(b), st, SPEC[key]["cost_pts"], FUT_COST[key], tp, mh)
            if not len(tr):
                continue
            t = pd.DatetimeIndex(tr["exit"])
            t = t.tz_localize(None) if t.tz is not None else t
            t0 = pd.DatetimeIndex(tr["time"])
            t0 = t0.tz_localize(None) if t0.tz is not None else t0
            trades.append(pd.DataFrame({"t0": t0, "t": t, "R": tr["R"].to_numpy(), "mk": key, "idea": name}))
            yrs = max((b.index[-1] - b.index[0]).days / 365.25, 0.1)
            rows.append({"indice": key, "ideia": name, "trades": len(tr), "R/trade": round(tr["R"].mean(), 3),
                         "%/ano": round(tr["R"].sum() / yrs, 2)})
    if not trades:
        raise SystemExit("Sem trades.")
    allt = pd.concat(trades).sort_values("t0").reset_index(drop=True)
    # limite de risco: no maximo max_open trades abertas ao mesmo tempo e 1 por indice (as outras sao ignoradas)
    keep, open_ = [], []
    for i, row in allt.iterrows():
        open_ = [o for o in open_ if o[0] > row.t0]
        if len(open_) >= a.max_open or any(o[1] == row.mk for o in open_):
            continue
        open_.append((row.t, row.mk))
        keep.append(i)
    dropped = len(allt) - len(keep)
    allt = allt.loc[keep].sort_values("t")
    per = pd.DataFrame(rows)
    # numeros por indice/ideia DEPOIS do limite de risco (so as trades que a carteira fez mesmo)
    nyears = max((allt["t"].max() - allt["t"].min()).days / 365.25, 0.1)
    g = allt.groupby(["mk", "idea"])["R"]
    per = pd.DataFrame({"indice": [k[0] for k in g.groups], "ideia": [k[1] for k in g.groups],
                        "trades": g.size().to_numpy(), "R/trade": g.mean().round(3).to_numpy(),
                        "%/ano": (g.sum() / nyears).round(2).to_numpy()})
    per = per.sort_values("%/ano", ascending=False)
    yearly = allt.groupby(allt["t"].dt.year)["R"].sum()          # 1% por trade -> R = % da conta
    eq = allt["R"].cumsum().to_numpy()
    dd = float((eq - np.maximum.accumulate(np.maximum(eq, 0))).min())
    years_ok = int((yearly >= OBJETIVO).sum())
    media = float(yearly.mean())
    print(per.to_string(index=False))
    print("\nPor ano (% da conta, 1% de risco por trade):")
    print(yearly.round(1).to_string())
    print(f"\nMedia: {media:+.1f}% ao ano | anos >= {OBJETIVO:g}%: {years_ok} de {len(yearly)} | "
          f"pior queda: {dd:.1f}% | trades/ano: {len(allt) / len(yearly):.0f} | "
          f"max {a.max_open} abertas, {dropped} sinais ignorados por limite de risco")
    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", "PORTFOLIO.md"), "w") as f:
        f.write(f"# Carteira ({a.period})\n\nIdeias: {', '.join(ideas)}\n\n{per.to_markdown(index=False) if hasattr(per, 'to_markdown') else per.to_string(index=False)}\n\n"
                f"Media {media:+.1f}% ao ano, anos >= {OBJETIVO:g}%: {years_ok}/{len(yearly)}, pior queda {dd:.1f}%\n")
    doc = {"max_open": a.max_open, "ideas": ideas, "period": a.period, "media": round(media, 2), "anos_ok": years_ok, "anos": int(len(yearly)),
           "dd": round(dd, 2), "trades_ano": round(len(allt) / len(yearly), 1),
           "por_ano": {str(k): round(float(v), 2) for k, v in yearly.items()},
           "por_indice": per.to_dict(orient="records")}
    if supa.set_state("portfolio", doc):
        print("(enviado para o dashboard)")


if __name__ == "__main__":
    main()
