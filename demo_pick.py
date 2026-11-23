"""
Escolhe SOZINHO a estrategia da conta demo EXPERIMENTAL (conta 2 da Edge Function paper-bot, perpetuos simulados).
Pedido do Antonio (2026-11-22): os bots decidem sozinhos o que corre na demo experimental, com mais trades (minimo 1/semana, ideal 3).
Regras (fixas, nao afinar):
  - so ideias que a demo sabe correr ao vivo (sr/demo_spec.py SPECS, testadas contra o backtest);
  - backtest dev 2019-2024 com custos de PERPETUOS (crypto_lab --venue perp): R/trade > 0 em BTC, ETH e SOL;
  - pelo menos 1 trade por semana (BTC+ETH+SOL juntos);
  - entre as que passam, ordena por t junto e junta estrategias (no maximo 3) ate a soma chegar a 3 trades/semana.
    Cada estrategia tem as suas posicoes (1 por moeda) e 1% de risco por trade.
  - So troca a lista se a nova 1.a estrategia tiver t pelo menos 0.3 acima da atual 1.a (evita andar a saltar).
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
from sr.demo_spec import SPECS

WEEKS_DEV = (pd.Timestamp("2024-12-31") - pd.Timestamp("2019-01-01")).days / 7


def evaluate(name: str) -> dict:
    f = f"results/runs/{name}-perp__dev.json"
    if not os.path.exists(f):
        subprocess.run([sys.executable, "crypto_lab.py", "--ideas", name, "--period", "dev", "--venue", "perp",
                        "--confirm", "", "--num", SPECS[name]["num"]], check=True, capture_output=True)
    d = json.load(open(f))
    m = d["markets"]
    n = sum(m[k]["n"] for k in ("btc", "eth", "sol") if k in m)
    tpw = n / WEEKS_DEV
    pos_all = all(k in m and m[k]["meanR"] > 0 for k in ("btc", "eth", "sol"))
    motivos = [f"{k.upper()} {m[k]['meanR']:+.3f}R" for k in ("btc", "eth", "sol") if k in m and m[k]["meanR"] <= 0]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    res = [evaluate(n) for n in SPECS]
    res.sort(key=lambda r: (not r["ok"], -r["t"]))
    print("ideia                          ok   t      R/trade  win%  trades/sem  motivos")
    for r in res:
        print(f"{r['ideia']:<30} {'SIM' if r['ok'] else 'nao':<4} {r['t']:+.2f}  {r['r_trade']:+.3f}   {r['win']:>4.0f}  {r['trades_semana']:>6.1f}     {'; '.join(r['motivos'])}")
    ok = [r for r in res if r["ok"]]
    if not ok:
        print("\nNenhuma ideia cumpre as regras da demo experimental: fica a atual.")
        return
    pick = [ok[0]]
    fam = lambda r: json.dumps([SPECS[r["ideia"]][k] for k in ("tf", "side", "entry", "btc")])
    for r in ok[1:]:
        if sum(x["trades_semana"] for x in pick) >= 3 or len(pick) >= 3:
            break
        if fam(r) in {fam(x) for x in pick}:   # mesma entrada (so muda stop/tempo) = mesmas trades em dobro: salta
            continue
        pick.append(r)
    reg = btc_regime_now()
    aviso = ""
    active = lambda r: SPECS[r["ideia"]].get("btc") in (None, "", reg)
    if reg and not any(active(r) for r in pick):
        extra = next((r for r in ok if active(r) and r not in pick), None)
        if extra:
            pick.append(extra)
        else:
            aviso = (f"Nenhuma estrategia que passa as regras opera com o BTC em regime '{reg}': "
                     "a demo experimental fica parada ate o regime mudar.")
            print("\nAVISO:", aviso)
    cur = current()
    if cur and cur.get("estrategias"):
        cur_first = cur["estrategias"][0]["ideia"]
        cur_r = next((r for r in res if r["ideia"] == cur_first), None)
        same = [x["ideia"] for x in cur["estrategias"]] == [x["ideia"] for x in pick]
        if not same and cur_r and cur_r["ok"] and pick[0]["ideia"] != cur_first and pick[0]["t"] < cur_r["t"] + 0.3:
            print(f"\nMantem a lista atual (1.a {cur_first}, t {cur_r['t']:+.2f}).")
            return
    tpw = sum(x["trades_semana"] for x in pick)
    doc = {"estrategias": [{"ideia": r["ideia"], **SPECS[r["ideia"]], "t": r["t"], "trades_semana": r["trades_semana"],
                            "win": r["win"], "r_trade": r["r_trade"]} for r in pick],
           "venue": "perp", "fee": 0.0005, "slip": 0.0002, "funding_8h": 0.0001, "risco": 0.01,
           "escolhida": pd.Timestamp.now(tz="Europe/Lisbon").strftime("%Y-%m-%d %H:%M"),
           "porque": "Escolha automatica: estrategias que ganham nas 3 moedas com custos de perpetuos (2019-2024), por ordem de t, "
                     f"ate ~3 trades/semana, sem repetir a mesma regra de entrada. Juntas: ~{tpw:.1f} trades/semana. " + "; ".join(
                         f"{r['num']} {r['ideia']}: t {r['t']:+.2f}, {r['trades_semana']}/sem, win {r['win']:.0f}%, {r['r_trade']:+.3f}R"
                         for r in pick),
           "aprovada": False, "candidatas": res, "regime_btc": reg, "aviso": aviso}
    print(f"\nESCOLHIDAS: {doc['porque']}")
    if a.push:
        print("gravado no painel:", supa.set_state("demo_exp", doc))
    with open("results/demo_exp.json", "w") as f:
        json.dump(doc, f)

if __name__ == "__main__":
    main()
