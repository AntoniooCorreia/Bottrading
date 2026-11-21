"""
Relatorio de scalping cripto: por ideia e moeda, com custos oficiais (Kraken taker 0.57% ida e volta) e, so como diagnostico,
com custos de maker (0.32%) e sem custos. Mostra o stop medio em % do preco e quanto os custos pesam em R.
  python scalp_report.py [--period dev] [--ideas s-bb-rev-5m-long,...]
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from crypto_lab import COST_PCT
from sr.swing import MAIN_COINS, load_tf, run_positions
from sr.swing_ideas import EXITS, IDEAS, NO_MIN_RISK

COSTS = {"oficial": COST_PCT, "maker": 2 * 0.0016, "futuros_taker": 0.0012, "futuros_maker": 0.0004, "zero": 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="dev")
    ap.add_argument("--ideas", default=",".join(sorted(NO_MIN_RISK)))
    a = ap.parse_args()
    rows = []
    for name in a.ideas.split(","):
        fn, tf, st, tp, mh = IDEAS[name]
        for k in MAIN_COINS:
            b = load_tf(k, tf, a.period)
            sig = fn(b)
            weeks = (b.index[-1] - b.index[0]).days / 7
            for lab, cp in COSTS.items():
                tr = run_positions(b, sig, st, 0.0, 0.0, tp, mh, cost_pct=cp, financing=False, min_risk_cost=0.0,
                                   **EXITS.get(name, {}))
                if not len(tr):
                    continue
                r = tr["R"].to_numpy()
                px = b["open"].reindex(tr["time"]).to_numpy()
                stop_pct = 100 * np.nanmedian(tr["risk_pts"].to_numpy() / px)
                hrs = (pd.DatetimeIndex(tr["exit"]) - pd.DatetimeIndex(tr["time"])).total_seconds().to_numpy() / 3600
                rows.append({"ideia": name, "moeda": k, "custos": lab, "trades": len(r), "trades/sem": round(len(r) / weeks, 1),
                             "win%": round(100 * (r > 0).mean()), "R/trade": round(r.mean(), 3),
                             "t": round(r.mean() / r.std(ddof=1) * np.sqrt(len(r)), 2) if len(r) > 1 else 0,
                             "%/ano": round(r.sum() / (weeks / 52), 1), "stop%": round(stop_pct, 2),
                             "custo_R": round(100 * cp / stop_pct, 2), "horas": round(float(np.median(hrs)), 1)})
    df = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    for lab in COSTS:
        print(f"\n=== custos {lab} ===")
        print(df[df["custos"] == lab].drop(columns="custos").to_string(index=False))
    df.to_csv("results/scalp_report.csv", index=False)


if __name__ == "__main__":
    main()
