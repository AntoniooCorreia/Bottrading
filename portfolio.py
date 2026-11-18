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
REGIAO = {"nq": "eua", "es": "eua", "dow": "eua", "dax": "europa", "ftse": "europa", "estx": "europa",
          "cac": "europa", "nikkei": "asia", "asx": "asia", "hsi": "asia"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--markets", default=",".join(CARTEIRA))
    ap.add_argument("--period", default="tudo", choices=list(PERIODS))
    ap.add_argument("--unlock-holdout", action="store_true", help="holdout: UMA vez por carteira, fica em HOLDOUT_LOG.md")
    ap.add_argument("--only", default="", help="lista indice:ideia a usar (ex.: nq:rsi2-dip-d,es:ibs-dip-d)")
    ap.add_argument("--region-cap", type=int, default=0, help="maximo de trades abertas por regiao (EUA/Europa/Asia); 0 = sem limite")
    ap.add_argument("--month-stop", type=float, default=0.0, help="para de abrir trades no mes depois de perder X%% (0 = desligado)")
    ap.add_argument("--vol-filter", action="store_true", help="nao entra quando a volatilidade de 20 dias do indice esta acima do percentil 80 do ultimo ano")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--label", default="", help="numero do catalogo (ex.: C8): envia para o dashboard como carteira extra "
                    "(estado portfolio_<label>) e grava results/PORTFOLIO_<label>.md; nunca toca na carteira de referencia")
    ap.add_argument("--ref", action="store_true", help="com --label: esta carteira e a de referencia (envia para o estado "
                    "portfolio e grava results/PORTFOLIO.md); so usar se for MELHOR que a atual")
    ap.add_argument("--sem-domingos", action="store_true", help="tira as velas diarias de domingo (precos parados do fim de "
                    "semana nos dados Dukascopy); e assim que o MT5 da demo ve os dias (C10)")
    ap.add_argument("--custos", default="cfd", choices=["cfd", "fut"], help="fut = micro-futuros (sem financiamento)")
    ap.add_argument("--max-open", type=int, default=3,
                    help="maximo de trades abertas ao mesmo tempo (risco total maximo = max_open %%)")
    a = ap.parse_args()
    ideas = a.ideas.split(",")
    hold = a.period == "holdout"
    if hold:
        if not a.unlock_holdout:
            raise SystemExit("O holdout esta FECHADO. Ver CLAUDE.md.")
        if not a.label:
            raise SystemExit("Holdout de carteira precisa de --label (numero do catalogo).")
        log = open("HOLDOUT_LOG.md", encoding="utf-8").read() if os.path.exists("HOLDOUT_LOG.md") else ""
        if f"carteira {a.label} " in log:
            raise SystemExit(f"A carteira {a.label} ja foi ao holdout (HOLDOUT_LOG.md). So uma vez.")
    hold_start = pd.Timestamp(PERIODS["holdout"][0])
    rows, trades = [], []
    for key in a.markets.split(","):
        if not os.path.exists(m5_path(key)):
            print(f"  {key}: sem dados (python download.py 2012 2026 {key})")
            continue
        for name in ideas:
            if a.only and f"{key}:{name}" not in a.only.split(","):
                continue
            fn, tf, st, tp, mh = IDEAS[name]
            # holdout: carrega tudo para aquecer os indicadores (media de 200...) e so conta trades com entrada >= 2025
            b = load_tf(key, tf, None if hold else a.period)
            if a.sem_domingos and tf == "1d":
                b = b[(b.index.tz_localize(None) if b.index.tz is not None else b.index).dayofweek < 5]
            tr = run_positions(b, fn(b), st, SPEC[key]["cost_pts"], FUT_COST[key], tp, mh)
            if not len(tr):
                continue
            t = pd.DatetimeIndex(tr["exit"])
            t = t.tz_localize(None) if t.tz is not None else t
            t0 = pd.DatetimeIndex(tr["time"])
            t0 = t0.tz_localize(None) if t0.tz is not None else t0
            df = pd.DataFrame({"t0": t0, "t": t, "R": tr["R_fut" if a.custos == "fut" else "R"].to_numpy(), "mk": key, "idea": name})
            if hold:
                df = df[df["t0"] >= hold_start]
                if not len(df):
                    continue
            if a.vol_filter:
                d = load_tf(key, "1d", a.period)["close"]
                d.index = d.index.tz_localize(None) if d.index.tz is not None else d.index
                rv = d.pct_change().rolling(20).std() * np.sqrt(252)
                thr = rv.rolling(252, min_periods=120).quantile(0.8)
                hv = (rv > thr).shift(1).fillna(False)          # so informacao do dia anterior
                df["hivol"] = hv.reindex(df["t0"].dt.normalize(), method="ffill").fillna(False).to_numpy()
            trades.append(df)
            yrs = max((b.index[-1] - b.index[0]).days / 365.25, 0.1)
            rows.append({"indice": key, "ideia": name, "trades": len(tr), "R/trade": round(tr["R"].mean(), 3),
                         "%/ano": round(tr["R"].sum() / yrs, 2)})
    if not trades:
        raise SystemExit("Sem trades.")
    allt = pd.concat(trades).sort_values("t0").reset_index(drop=True)
    # limite de risco: no maximo max_open trades abertas ao mesmo tempo e 1 por indice (as outras sao ignoradas)
    keep, open_, closed = [], [], []
    for i, row in allt.iterrows():
        closed += [o for o in open_ if o[0] < row.t0]   # so liberta o lugar se fechou ANTES do dia de entrada
        open_ = [o for o in open_ if o[0] >= row.t0]
        if len(open_) >= a.max_open or any(o[1] == row.mk for o in open_):
            continue
        if a.region_cap and sum(REGIAO[o[1]] == REGIAO[row.mk] for o in open_) >= a.region_cap:
            continue
        if a.vol_filter and bool(row.get("hivol", False)):
            continue
        if a.month_stop:
            m = (row.t0.year, row.t0.month)
            pnl = sum(o[2] for o in closed if (o[0].year, o[0].month) == m)
            if pnl <= -a.month_stop:
                continue
        open_.append((row.t, row.mk, row.R))
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
    allm = allt.groupby([allt["t"].dt.year, allt["t"].dt.month])["R"].sum()
    rng = pd.period_range(allt["t"].min(), allt["t"].max(), freq="M")
    monthly = pd.Series([float(allm.get((p.year, p.month), 0.0)) for p in rng], index=[str(p) for p in rng])
    media = float(yearly.mean())
    print(per.to_string(index=False))
    print("\nPor ano (% da conta, 1% de risco por trade):")
    print(yearly.round(1).to_string())
    print(f"\nMedia: {media:+.1f}% ao ano | anos >= {OBJETIVO:g}%: {years_ok} de {len(yearly)} | "
          f"pior queda: {dd:.1f}% | trades/ano: {len(allt) / len(yearly):.0f} | "
          f"max {a.max_open} abertas, {dropped} sinais ignorados por limite de risco")
    print(f"Meses: pior {monthly.min():.1f}% | meses positivos {int((monthly > 0).sum())}/{len(monthly)} "
          f"| meses abaixo de -3%: {int((monthly < -3).sum())} | pior ano {yearly.min():.1f}% | anos negativos {int((yearly < 0).sum())}")
    os.makedirs("results", exist_ok=True)
    fname = f"PORTFOLIO_{a.label}.md" if a.label and not a.ref else "PORTFOLIO.md"
    with open(os.path.join("results", fname), "w") as f:
        f.write(f"# Carteira ({a.period})\n\nIdeias: {', '.join(ideas)}\n\n{per.to_markdown(index=False) if hasattr(per, 'to_markdown') else per.to_string(index=False)}\n\n"
                f"Media {media:+.1f}% ao ano, anos >= {OBJETIVO:g}%: {years_ok}/{len(yearly)}, pior queda {dd:.1f}%\n")
    doc = {"regras": {"max_open": a.max_open, "region_cap": a.region_cap, "month_stop": a.month_stop, "vol_filter": a.vol_filter},
           "pior_mes": round(float(monthly.min()), 2), "meses_pos": int((monthly > 0).sum()), "meses": int(len(monthly)),
           "pior_ano": round(float(yearly.min()), 2), "anos_neg": int((yearly < 0).sum()),
           "por_mes": {k: round(v, 2) for k, v in monthly.items()},
           "max_open": a.max_open, "ideas": ideas, "period": a.period, "media": round(media, 2), "anos_ok": years_ok, "anos": int(len(yearly)),
           "dd": round(dd, 2), "trades_ano": round(len(allt) / len(yearly), 1),
           "por_ano": {str(k): round(float(v), 2) for k, v in yearly.items()},
           "por_indice": per.to_dict(orient="records"),
           "label": a.label, "custos": a.custos, "markets": sorted(set(per["indice"])) if "indice" in per else [],
           # lista de trades (entrada, saida, indice, ideia, R = % da conta) para o calendario do dashboard
           "trades": [[r.t0.strftime("%Y-%m-%d"), r.t.strftime("%Y-%m-%d"), r.mk, r.idea, round(float(r.R), 3)]
                      for r in allt.sort_values("t0").itertuples()]}
    key = f"portfolio_{a.label}" if a.label and not a.ref else "portfolio"
    if not a.no_push and supa.set_state(key, doc):
        print("(enviado para o dashboard)")


if __name__ == "__main__":
    main()
