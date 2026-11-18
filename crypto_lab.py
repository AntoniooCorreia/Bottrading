"""
Laboratorio de crypto: corre ideias (sr/swing_ideas.py) em BTC/ETH/SOL com custos da Kraken spot e junta-as numa
carteira com 1% de risco por trade, no maximo 1 posicao por moeda (o lugar so fica livre no dia a seguir ao fecho).
  python crypto_lab.py --ideas k-donchian20-d,k-sma100-d [--period dev|pre|tudo] [--label K1] [--push]
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd

from sr import supa
from sr.stats import summarize
from sr.swing import CRYPTO, KRAKEN_FEE, load_tf, run_positions
from sr.swing_ideas import IDEAS

COST_PCT = 2 * KRAKEN_FEE + 0.0005


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--coins", default=",".join(CRYPTO))
    ap.add_argument("--period", default="tudo", choices=["dev", "pre", "tudo", "holdout", "completo"])
    ap.add_argument("--label", default="")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    rows, allt = [], []
    for name in a.ideas.split(","):
        fn, tf, st, tp, mh = IDEAS[name]
        for k in a.coins.split(","):
            b = load_tf(k, tf, None if a.period == "completo" else a.period)
            tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, cost_pct=COST_PCT, financing=False)
            if not len(tr):
                continue
            yrs = (b.index[-1] - b.index[0]).days / 365.25
            s = summarize(tr, yrs)
            rows.append({"ideia": name, "moeda": k, "trades": s["n"], "R/trade": s["meanR"], "t": s["t"],
                         "win%": s["win%"], "%/ano": s["R/ano"], "pior_queda": s["maxDD_R"]})
            t0 = pd.DatetimeIndex(tr["time"]).tz_localize(None)
            t1 = pd.DatetimeIndex(tr["exit"]).tz_localize(None)
            allt.append(pd.DataFrame({"t0": t0, "t": t1, "R": tr["R"].to_numpy(), "mk": k, "idea": name}))
    per = pd.DataFrame(rows)
    print(per.to_string(index=False))
    if not allt:
        return
    allt = pd.concat(allt).sort_values("t0").reset_index(drop=True)
    keep, open_ = [], []
    for i, r in allt.iterrows():
        open_ = [o for o in open_ if o[0].normalize() >= r.t0.normalize()]   # ainda aberta (liberta so no dia seguinte ao fecho)
        if any(o[1] == r.mk for o in open_):
            continue
        open_.append((r.t, r.mk))
        keep.append(i)
    p = allt.loc[keep].sort_values("t")
    yearly = p.groupby(p["t"].dt.year)["R"].sum()
    rng = pd.period_range(p["t"].min(), p["t"].max(), freq="M")
    mg = p.groupby([p["t"].dt.year, p["t"].dt.month])["R"].sum()
    monthly = pd.Series([float(mg.get((q.year, q.month), 0.0)) for q in rng], index=[str(q) for q in rng])
    eq = p["R"].cumsum().to_numpy()
    dd = float((eq - np.maximum.accumulate(np.maximum(eq, 0))).min())
    comp = 10000.0
    for x in p["R"]:
        comp *= 1 + x / 100
    print(f"\nCom juros compostos: 10 000 EUR -> {comp:,.0f} EUR")
    print("\nPor moeda (depois da regra de 1 posicao por moeda):")
    print(p.groupby("mk")["R"].agg(["count", "sum", "mean"]).round(2).to_string())
    print("\nCarteira por ano (% da conta, 1% por trade):")
    print(yearly.round(1).to_string())
    print(f"Media {yearly.mean():+.1f}%/ano | anos >= 14%: {(yearly >= 14).sum()}/{len(yearly)} | pior mes {monthly.min():.1f}% "
          f"| pior ano {yearly.min():.1f}% | pior queda {dd:.1f}% | meses positivos {(monthly > 0).sum()}/{len(monthly)} "
          f"| {len(p) / max(len(yearly), 1):.0f} trades/ano")
    if a.push and a.label:
        doc = {"label": a.label, "ideas": a.ideas.split(","), "period": a.period, "mercado": "crypto",
               "media": round(float(yearly.mean()), 2), "anos_ok": int((yearly >= 14).sum()), "anos": int(len(yearly)),
               "dd": round(dd, 2), "trades_ano": round(len(p) / max(len(yearly), 1), 1),
               "pior_mes": round(float(monthly.min()), 2), "pior_ano": round(float(yearly.min()), 2),
               "meses_pos": int((monthly > 0).sum()), "meses": int(len(monthly)),
               "por_ano": {str(k): round(float(v), 2) for k, v in yearly.items()},
               "por_mes": {k: round(v, 2) for k, v in monthly.items()},
               "por_indice": per.rename(columns={"moeda": "indice"}).to_dict(orient="records"),
               "markets": sorted(p["mk"].unique().tolist()), "anos_neg": int((yearly < 0).sum()),
               "trades": [[r.t0.strftime("%Y-%m-%d"), r.t.strftime("%Y-%m-%d"), r.mk, r.idea, round(float(r.R), 3)]
                          for r in p.sort_values("t0").itertuples()]}
        print("dashboard:", supa.set_state("portfolio", doc))


if __name__ == "__main__":
    main()
