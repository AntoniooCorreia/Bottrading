"""
Melhor teste cripto pela pontuacao do painel (pedido do Antonio, 2026-11-19) e diagnostico do que falha.
Pontuacao = media do percentil em win rate, % total acumulado e melhor ano, entre as carteiras cripto do periodo dev
(results/carteiras/K*.json). E a base que o agente usa para tentar melhorar.
  python best.py            -> ranking + diagnostico do 1.o
  python best.py --label K20 -> diagnostico de uma carteira concreta
"""
from __future__ import annotations

import argparse
import glob
import json

import pandas as pd


def load():
    out = []
    for f in glob.glob("results/carteiras/K*.json"):
        if "patch" in f:
            continue
        d = json.load(open(f))
        if d.get("mercado") != "crypto" or d.get("period") != "dev":
            continue
        T = d["trades"]
        d["_win"] = 100 * sum(t[4] > 0 for t in T) / max(len(T), 1)   # breakeven (0.000R) nao conta como ganha
        d["_tot"] = sum(t[4] for t in T)
        d["_best"] = max(d["por_ano"].values()) if d["por_ano"] else 0.0
        out.append(d)
    n = max(len(out) - 1, 1)
    for d in out:
        d["_sc"] = round(100 * sum(sum(o[k] < d[k] for o in out) / n for k in ("_win", "_tot", "_best")) / 3)
    return sorted(out, key=lambda d: -d["_sc"])


def diagnose(d):
    t = pd.DataFrame(d["trades"], columns=["t0", "t1", "mk", "idea", "R"])
    t["t0"], t["t1"] = pd.to_datetime(t["t0"]), pd.to_datetime(t["t1"])
    t["dias"] = (t["t1"] - t["t0"]).dt.days
    print(f"\n=== DIAGNOSTICO {d['label']} ({d.get('nota', '')}) ===")
    print(f"pontuacao {d['_sc']} | win rate {d['_win']:.0f}% | total {d['_tot']:+.0f}% | melhor ano {d['_best']:+.1f}% | "
          f"pior ano {d['pior_ano']:+.1f}% | pior mes {d['pior_mes']:+.1f}% | {d['trades_ano'] / 52:.1f} trades/semana (objetivo 2-3)")
    for o in d.get("oficial", []):
        print(f"criterio oficial {o['ideia']}: {'PASSA' if o['passa'] else 'REPROVADA'} {'; '.join(o['motivos'])}")
    g = lambda by: t.groupby(by)["R"].agg(trades="count", win=lambda r: round(100 * (r > 0).mean()), R_trade="mean", total="sum").round(2)
    print("\nPor moeda:"); print(g("mk").to_string())
    print("\nPor ano:"); print(g(t["t1"].dt.year).to_string())
    t["duracao"] = pd.cut(t["dias"], [-1, 1, 3, 7, 30, 10_000], labels=["<=1d", "2-3d", "4-7d", "8-30d", ">30d"])
    print("\nPor duracao (onde estao as perdas?):"); print(g("duracao").to_string())
    gap = t.sort_values("t0").groupby("mk")["t0"].diff().dt.days
    print(f"\nDias sem trade entre entradas (mediana por moeda): {gap.median():.0f} -> e aqui que se ganham trades")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    L = load()
    print("pont  carteira  win%  total%  melhor_ano  trades/sem  nota")
    for d in L[:10]:
        print(f"{d['_sc']:>4}  {d['label']:<8} {d['_win']:>5.0f} {d['_tot']:>7.0f} {d['_best']:>10.1f} {d['trades_ano'] / 52:>10.1f}  {d.get('nota', '')[:60]}")
    pick = next((d for d in L if d["label"] == a.label), L[0]) if L else None
    if pick:
        diagnose(pick)
