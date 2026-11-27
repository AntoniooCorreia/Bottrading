"""
Escolhe SOZINHO a estrategia da conta demo EXPERIMENTAL (conta 2 da Edge Function paper-bot, perpetuos simulados).
Pedido do Antonio (2026-11-22): os bots decidem sozinhos o que corre na demo experimental, com mais trades (minimo 1/semana, ideal 3).
Regras (fixas, nao afinar):
  - so ideias que a demo sabe correr ao vivo (sr/demo_spec.py SPECS, testadas contra o backtest);
  - backtest dev 2019-2024 com custos de PERPETUOS (crypto_lab --venue perp): R/trade > 0 em BTC, ETH e SOL;
  - pelo menos 1 trade por semana (BTC+ETH+SOL juntos);
  - entre as que passam, ordena por t junto e junta estrategias (no maximo 3) ate a soma chegar a 3 trades/semana.
    Cada estrategia tem as suas posicoes (1 por moeda) e 1% de risco por trade.
  - (2026-11-26) Uma conta demo por ESTILO: 2 = swing (dias), 3 = day trade (horas), 4 = scalping (minutos); ver pick_style.
  - REGIME ATUAL (2026-11-23): le o BTC na Kraken. Se nenhuma das escolhidas pode operar no regime de agora (ex.: todas precisam de
    BTC acima da media de 200 dias e ele esta abaixo), junta a melhor que passa as regras E opera no regime atual. Se nao houver,
    avisa (a demo fica parada) e regista-o no doc.
A demo experimental NAO e aprovacao: e um teste ao vivo com dinheiro a fingir. A conta 1 (K1) nao muda.
  python demo_pick.py [--push]      (--push grava state.demo_exp no Supabase; a demo usa-a na hora seguinte)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request

import pandas as pd

from sr import supa
from sr.demo_spec import REPLACED, SPECS, style

WEEKS_DEV = (pd.Timestamp("2024-12-31") - pd.Timestamp("2019-01-01")).days / 7


def evaluate(name: str) -> dict:
    sp = SPECS[name]
    base, coins = sp.get("base", name), sp.get("coins") or ["btc", "eth", "sol"]
    suf = f"-{len(coins)}m" if sorted(coins) != ["btc", "eth", "sol"] else ""
    if sp.get("max_open") and sp["max_open"] != 4:
        suf += f"-mo{sp['max_open']}"  # igual ao crypto_lab.save_run
    f = f"results/runs/{base}-perp{suf}__dev.json"
    if not os.path.exists(f):
        cmd = [sys.executable, "crypto_lab.py", "--ideas", base, "--period", "dev", "--venue", "perp",
               "--confirm", "", "--num", sp["num"], "--coins", ",".join(coins)]
        if sp.get("max_open"):
            cmd += ["--max-open", str(sp["max_open"])]
        subprocess.run(cmd, check=True, capture_output=True)
    d = json.load(open(f))
    m = d["markets"]
    n = sum(m[k]["n"] for k in coins if k in m)
    tpw = n / WEEKS_DEV
    pos_all = all(k in m and m[k]["meanR"] > 0 for k in coins)
    motivos = [f"{k.upper()} {m[k]['meanR']:+.3f}R" for k in coins if k in m and m[k]["meanR"] <= 0]
    if tpw < 1:
        motivos.append(f"so {tpw:.1f} trades/semana")
    return {"ideia": name, "num": SPECS[name]["num"], "t": d["pooled"]["t"], "r_trade": d["pooled"]["meanR"],
            "win": d["pooled"]["win%"], "trades_semana": round(tpw, 1), "ok": pos_all and tpw >= 1, "motivos": motivos,
            "por_moeda": {k: [m[k]["meanR"], m[k]["n"]] for k in m}}


def btc_regime_now() -> str | None:
    """'bull' se o BTC fechou ontem acima da media de 200 dias (Kraken), 'bear' se abaixo, None se nao der para ler."""
    try:
        with urllib.request.urlopen("https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440", timeout=20) as r:
            j = json.load(r)
        k = [x for x in j["result"] if x != "last"][0]
        c = [float(x[4]) for x in j["result"][k][:-1]]
        return "bull" if c[-1] > sum(c[-200:]) / 200 else "bear"
    except Exception as e:
        print(f"[kraken] nao li o regime do BTC ({e})")
        return None


def current() -> dict | None:
    try:
        req = urllib.request.Request(f"{supa.URL}/rest/v1/state?select=value&key=eq.demo_exp",
                                     headers={"apikey": supa.PUBLISHABLE, "Authorization": f"Bearer {supa.PUBLISHABLE}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            rows = json.load(r)
        return rows[0]["value"] if rows else None
    except Exception:
        return None


ACCOUNTS = [(2, "swing", "Swing (dias)"), (3, "day", "Day trade (horas)"), (4, "scalp", "Scalping (minutos)")]


def pick_style(res: list[dict], st: str, reg: str | None) -> tuple[list[dict], str]:
    """Escolhe as estrategias de UM estilo (pedido do Antonio, 2026-11-26: uma conta demo por estilo, sempre com algo a correr):
    1) as que ganham nas 3 moedas (ok), por t, sem repetir a mesma entrada, ate ~3 trades/semana;
    2) se nenhuma das escolhidas opera no regime atual do BTC, junta a melhor (por t) que opere agora, mesmo que nao passe:
       fica marcada 'nao passa no backtest - so para ver ao vivo'."""
    mine = [r for r in res if style(SPECS[r["ideia"]]) == st]
    fam = lambda r: json.dumps([SPECS[r["ideia"]].get(k) for k in ("tf", "side", "entry", "btc", "vol_mult")])
    active = lambda r: SPECS[r["ideia"]].get("btc") in (None, "", reg)
    pick: list[dict] = []
    for r in [x for x in mine if x["ok"]]:
        if sum(x["trades_semana"] for x in pick) >= 3 or len(pick) >= 3:
            break
        if fam(r) not in {fam(x) for x in pick}:
            pick.append(r)
    aviso = ""
    if reg and not any(active(r) for r in pick):
        extra = sorted([r for r in mine if active(r) and r not in pick], key=lambda r: (not r["ok"], -r["t"]))
        if extra:
            pick.append(extra[0])
            if not extra[0]["ok"]:
                aviso = (f"Nenhuma estrategia {st} que passa opera com o BTC em regime '{reg}'; para haver trades ao vivo corre "
                         f"{extra[0]['num']} {extra[0]['ideia']}, que NAO passa no backtest ({'; '.join(extra[0]['motivos'])}).")
        else:
            aviso = f"Nenhuma estrategia {st} opera com o BTC em regime '{reg}': esta conta fica parada."
    for r in pick:
        r["estado"] = "passa as regras da demo" if r["ok"] else "nao passa no backtest (so para ver ao vivo)"
    return pick, aviso


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    res = [evaluate(n) for n in SPECS if n not in REPLACED]   # o diario substituiu estas por variantes melhores
    res.sort(key=lambda r: (not r["ok"], -r["t"]))
    print("estilo ideia                              ok   t      R/trade  win%  trades/sem  motivos")
    for r in res:
        print(f"{style(SPECS[r['ideia']]):<6} {r['ideia']:<34} {'SIM' if r['ok'] else 'nao':<4} {r['t']:+.2f}  {r['r_trade']:+.3f}   "
              f"{r['win']:>4.0f}  {r['trades_semana']:>6.1f}     {'; '.join(r['motivos'])}")
    reg = btc_regime_now()
    contas = []
    for acc, st, nome in ACCOUNTS:
        pick, aviso = pick_style(res, st, reg)
        tpw = sum(x["trades_semana"] for x in pick)
        contas.append({"id": acc, "estilo": st, "nome": nome, "aviso": aviso,
                       "estrategias": [{"ideia": r["ideia"], **SPECS[r["ideia"]], "t": r["t"], "trades_semana": r["trades_semana"],
                                        "win": r["win"], "r_trade": r["r_trade"], "estado": r["estado"]} for r in pick],
                       "porque": f"~{tpw:.1f} trades/semana no backtest 2019-2024 (custos de perpetuos). " + "; ".join(
                           f"{r['num']} {r['ideia']}: t {r['t']:+.2f}, win {r['win']:.0f}%, {r['r_trade']:+.3f}R ({r['estado']})" for r in pick)})
        print(f"\n[{nome}] " + contas[-1]["porque"] + (f"\n  AVISO: {aviso}" if aviso else ""))
    doc = {"contas": contas, "estrategias": contas[0]["estrategias"], "porque": contas[0]["porque"], "aviso": contas[0]["aviso"],
           "venue": "perp", "fee": 0.0005, "slip": 0.0002, "funding_8h": 0.0001, "risco": 0.01,
           "escolhida": pd.Timestamp.now(tz="Europe/Lisbon").strftime("%Y-%m-%d %H:%M"),
           "aprovada": False, "candidatas": res, "regime_btc": reg}
    if a.push:
        print("gravado no painel:", supa.set_state("demo_exp", doc))
    with open("results/demo_exp.json", "w") as f:
        json.dump(doc, f)


if __name__ == "__main__":
    main()
