"""
Laboratorio de crypto (criterio oficial cripto: por ideia, >= 60 trades em cada moeda, meanR > 0 em cada moeda
BTC/ETH/SOL e t junto >= 3.0, com custos Kraken; a SOL so tem dados desde 2020-08). Confirmacao (detetor de sorte):
positiva em >= 3 das 5 moedas extra XRP/ADA/DOGE/LINK/AVAX (linha CONFIRMACAO). Laboratorio de crypto: corre ideias (sr/swing_ideas.py) em BTC/ETH/SOL com custos da Kraken spot e junta-as numa
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
from sr.swing import CONFIRM_COINS, KRAKEN_FEE, MAIN_COINS, load_tf, run_positions
from sr.swing_ideas import EXITS, IDEAS

COST_PCT = 2 * KRAKEN_FEE + 0.0005


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--coins", default=",".join(MAIN_COINS))
    ap.add_argument("--confirm", default=",".join(CONFIRM_COINS), help="moedas de confirmacao ('' para nao correr)")
    ap.add_argument("--period", default="tudo", choices=["dev", "pre", "tudo", "holdout", "completo"])
    ap.add_argument("--label", default="", help="nome da carteira (K2, K3...). Com --push e sem --label usa o proximo K livre")
    ap.add_argument("--push", action="store_true", help="guarda SEMPRE a carteira no painel (aprovada ou reprovada)")
    ap.add_argument("--ref", action="store_true", help="tambem a torna a carteira de referencia (so com OK do Antonio)")
    ap.add_argument("--nota", default="", help="nota curta que aparece no painel (ex.: '#100 persistencia 1 dia')")
    ap.add_argument("--out", default="", help="escreve a carteira num ficheiro JSON (sem Supabase)")
    a = ap.parse_args()
    rows, allt, byidea = [], [], {}
    for name in a.ideas.split(","):
        fn, tf, st, tp, mh = IDEAS[name]
        for k in a.coins.split(","):
            b = load_tf(k, tf, None if a.period == "completo" else a.period)
            tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, cost_pct=COST_PCT, financing=False, **EXITS.get(name, {}))
            if not len(tr):
                continue
            yrs = (b.index[-1] - b.index[0]).days / 365.25
            s = summarize(tr, yrs)
            byidea.setdefault(name, {})[k] = tr["R"].to_numpy()
            rows.append({"ideia": name, "moeda": k, "trades": s["n"], "R/trade": s["meanR"], "t": s["t"],
                         "win%": s["win%"], "%/ano": s["R/ano"], "pior_queda": s["maxDD_R"]})
            t0 = pd.DatetimeIndex(tr["time"]).tz_localize(None)
            t1 = pd.DatetimeIndex(tr["exit"]).tz_localize(None)
            allt.append(pd.DataFrame({"t0": t0, "t": t1, "R": tr["R"].to_numpy(), "mk": k, "idea": name}))
    conf = {}
    for name in a.ideas.split(","):
        fn, tf, st, tp, mh = IDEAS[name]
        for k in [c for c in a.confirm.split(",") if c]:
            b = load_tf(k, tf, None if a.period == "completo" else a.period)
            if len(b) < 300:
                continue
            tr = run_positions(b, fn(b), st, 0.0, 0.0, tp, mh, cost_pct=COST_PCT, financing=False, **EXITS.get(name, {}))
            if len(tr):
                conf.setdefault(name, {})[k] = tr["R"].to_numpy()
    per = pd.DataFrame(rows)
    print(per.to_string(index=False))
    print()
    oficial = []
    for name, d in byidea.items():
        allr = np.concatenate(list(d.values()))
        t = allr.mean() / allr.std(ddof=1) * np.sqrt(len(allr)) if len(allr) > 1 else 0.0
        ok = len(d) == len(a.coins.split(",")) and all(len(v) >= 60 and v.mean() > 0 for v in d.values()) and t >= 3.0
        print(f"VEREDICTO {name}: {'PASSA' if ok else 'REPROVADA'} | t junto {t:+.2f} | win rate {100 * (allr > 0).mean():.0f}% | "
              f"R/trade {allr.mean():+.3f} | " + ", ".join(f"{k} {v.mean():+.3f}R/{len(v)}" for k, v in d.items()))
        motivos = []
        for k in a.coins.split(","):
            v = d.get(k)
            if v is None or len(v) < 60:
                motivos.append(f"{k.upper()} so {0 if v is None else len(v)} trades (< 60)")
            elif v.mean() <= 0:
                motivos.append(f"{k.upper()} negativa ({v.mean():+.2f}R)")
        if t < 3.0:
            motivos.append(f"t junto {t:+.2f} (< 3.0)")
        o = {"ideia": name, "passa": bool(ok), "t": round(float(t), 2), "win": round(float(100 * (allr > 0).mean()), 1),
             "r_trade": round(float(allr.mean()), 3), "motivos": motivos}
        if conf.get(name):
            c = conf[name]
            npos = sum(v.mean() > 0 for v in c.values())
            cr = np.concatenate(list(c.values()))
            print(f"CONFIRMACAO {name}: positiva em {npos}/{len(c)} moedas extra (precisa >= 3) | win rate {100 * (cr > 0).mean():.0f}% | "
                  + ", ".join(f"{k} {v.mean():+.3f}R/{len(v)}" for k, v in c.items()))
            o["confirmacao"] = f"{npos}/{len(c)}"
            if npos < 3:
                o["passa"] = False
                o["motivos"].append(f"confirmacao so {npos}/{len(c)} moedas extra (precisa >= 3)")
        oficial.append(o)
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
    yearly = yearly.reindex(range(int(yearly.index.min()), int(yearly.index.max()) + 1), fill_value=0.0)   # anos sem trades contam 0%
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
          f"| {len(p) / max(len(yearly), 1):.0f} trades/ano | win rate {100 * (p['R'] > 0).mean():.0f}%")
    if a.push or a.out:
        label = a.label or (next_label() if a.push else "K?")
        doc = {"label": label, "ideas": a.ideas.split(","), "period": a.period, "mercado": "crypto",
               "criado": pd.Timestamp.now(tz="Europe/Lisbon").strftime("%Y-%m-%d %H:%M"), "nota": a.nota,
               "oficial": oficial, "oficial_passa": bool(oficial) and all(o["passa"] for o in oficial),
               "win": round(float(100 * (p["R"].round(3) > 0).mean()), 1),   # breakeven nao e ganha
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
        if a.out:
            with open(a.out, "w") as f:
                json.dump(doc, f)
            print("ficheiro:", a.out)
        if a.push:
            os.makedirs("results/carteiras", exist_ok=True)
            with open(f"results/carteiras/{label}.json", "w") as f:   # copia no repo (best.py le daqui)
                json.dump(doc, f)
            # cada teste e uma carteira no painel (separador Backtesting), aprovada ou reprovada
            print(f"carteira {label} no painel:", supa.set_state("portfolio_" + label, doc))
            if a.ref:
                print("referencia:", supa.set_state("portfolio", doc))


def next_label() -> str:
    """Proximo K livre (K2, K3, ...) lido do painel."""
    import re
    import urllib.request
    try:
        req = urllib.request.Request(f"{supa.URL}/rest/v1/state?select=key&key=like.portfolio_K*",
                                     headers={"apikey": supa.PUBLISHABLE, "Authorization": f"Bearer {supa.PUBLISHABLE}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            keys = [x["key"] for x in json.load(r)]
        nums = [int(m.group(1)) for k in keys if (m := re.fullmatch(r"portfolio_K(\d+)", k))]
        return f"K{max(nums + [1]) + 1}"
    except Exception as e:
        print(f"[supabase] nao li as carteiras ({e}); usa --label")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
