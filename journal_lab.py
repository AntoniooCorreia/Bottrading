"""
Diario do bot -> mudancas testadas e aplicadas SOZINHAS (pedido do Antonio, 2026-11-27).

A Edge Function paper-bot analisa cada trade fechada da demo e grava em paper_journal o porque e, quando a causa e corrigivel,
UMA mudanca de parametro (ex.: "so sair com RSI(2) > 70 em vez de 60"). Este script:
  1. le as mudancas com estado "proposta" (junta as iguais: a mesma variante proposta por varias perdas = 1 teste);
  2. corre no backtest 2019-2024 (perpetuos, as mesmas moedas da demo) a estrategia como esta e a variante, as duas geradas
     a partir da spec da demo (comparacao justa, so muda o parametro);
  3. REGRA FIXA (escrita antes de qualquer teste, nao se afina): APLICA se
       R por trade da variante >= R por trade atual + 0.02R   E   t >= t atual + 0.3   E   trades >= 50% das atuais;
     (o R por trade tem de subir: so mais trades com o mesmo R por trade nao e melhoria);
     senao REJEITA. Aplicar = gravar a variante em sr/journal_specs.json (substitui a original na demo via demo_pick.py);
  4. escreve no diario (paper_journal: estado + resultado antes -> depois) e no diario do agente (Telegram).
A conta 1 (K1) nunca e mudada aqui (essas propostas ficam "precisa do OK do Antonio").

  python journal_lab.py            -> testa ate 3 mudancas propostas e aplica as que passam a regra
  python journal_lab.py --dry      -> so mostra o que testaria
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

import crypto_lab
from sr import supa
from sr.demo_spec import SPECS
from sr.journal import idea_from_spec, load_specs, save_specs, vary
from sr.swing import MAIN_COINS

MIN_DT, MIN_DR, MAX_TESTS = 0.3, 0.02, 3


def proposals() -> list[dict]:
    url = f"{supa.URL}/rest/v1/paper_journal?select=*&estado=eq.proposta&order=id.asc"
    req = urllib.request.Request(url, headers={"apikey": supa.PUBLISHABLE, "Authorization": f"Bearer {supa.PUBLISHABLE}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def update(ids: list[int], estado: str, resultado: str) -> None:
    tok = os.environ.get("BT_WRITE_TOKEN", "")
    if not tok:
        print("[diario] sem BT_WRITE_TOKEN: nao atualizo o paper_journal")
        return
    body = json.dumps({"p_token": tok, "p_ids": ids, "p_estado": estado, "p_resultado": resultado}).encode()
    req = urllib.request.Request(f"{supa.URL}/rest/v1/rpc/journal_update", data=body, method="POST",
                                 headers={"apikey": supa.PUBLISHABLE, "Authorization": f"Bearer {supa.PUBLISHABLE}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()


def next_num() -> int:
    txt = open("IDEAS.md").read() + open("SUMMARY.md").read()
    return max(int(x) for x in re.findall(r"#(\d{3})\b", txt)) + 1


def run(name: str, spec: dict, num: str, push: bool, nota: str) -> dict:
    """Corre o crypto_lab com a ideia gerada a partir da spec; devolve o resumo do teste."""
    crypto_lab.IDEAS[name], crypto_lab.EXITS[name] = idea_from_spec(spec)
    if spec.get("orig_base") in crypto_lab.NO_MIN_RISK:
        crypto_lab.NO_MIN_RISK.add(name)
    coins = spec.get("coins") or list(MAIN_COINS)
    argv = ["crypto_lab.py", "--ideas", name, "--period", "dev", "--venue", "perp", "--confirm", "", "--num", num,
            "--coins", ",".join(coins)]
    if spec.get("max_open"):
        argv += ["--max-open", str(spec["max_open"])]
    if push:
        argv += ["--push", "--nota", nota]
    old = sys.argv
    sys.argv = argv
    try:
        crypto_lab.main()
    finally:
        sys.argv = old
    suf = f"-{len(coins)}m" if sorted(coins) != sorted(MAIN_COINS) else ""
    d = json.load(open(f"results/runs/{name}-perp{suf}__dev.json"))
    m = d["markets"]
    n = sum(v["n"] for v in m.values())
    mean = sum(v["meanR"] * v["n"] for v in m.values()) / max(n, 1)
    win = sum(v["win%"] * v["n"] for v in m.values()) / max(n, 1)
    return {"t": d["pooled"].get("t", 0.0), "meanR": mean, "n": n, "win": win, "pos_all": all(v["meanR"] > 0 for v in m.values()),
            "por_moeda": ", ".join(f"{k.upper()} {v['meanR']:+.2f}R" for k, v in m.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    P = proposals()
    groups: dict[str, list[dict]] = {}
    for p in P:
        if p.get("account", 1) >= 2 and p.get("mudanca"):
            groups.setdefault(p["mudanca"]["variante"], []).append(p)
    if not groups:
        print("Sem mudancas propostas pelo diario.")
        return
    applied = load_specs()
    log = []
    for var, ps in list(groups.items())[:MAX_TESTS]:
        mu, strat, ids = ps[0]["mudanca"], ps[0]["strategy"], [p["id"] for p in ps]
        print(f"\n=== {var}: {mu['texto']} (proposta por {len(ps)} perda(s)) ===")
        if strat not in SPECS:
            update(ids, "rejeitada", f"A estrategia {strat} ja nao esta nas specs da demo: nada a mudar.")
            continue
        if var in applied or var in SPECS:
            update(ids, "aplicada", f"Esta mudanca ja tinha sido aplicada antes ({var}).")
            continue
        if a.dry:
            continue
        orig = SPECS[strat]
        base_spec = {**orig, "orig_base": orig.get("base", strat)}
        var_spec = {**vary(orig, mu["param"], mu["para"]), "orig_base": orig.get("base", strat)}
        update(ids, "em teste", f"A testar no backtest 2019-2024: {mu['texto']}")
        num = f"#{next_num()}"
        with open("IDEAS.md", "a") as f:   # registo ANTES de correr (protocolo)
            f.write(f"\n- **{num} diario da demo** ({strat}): vai testar {mu['texto']} Proposta por {len(ps)} perda(s) ao vivo. "
                    f"Regra fixa do journal_lab.py: aplica se R/trade sobe >= {MIN_DR}R, t >= t atual + {MIN_DT} e trades >= 50%.\n")
        b = run(f"jbase~{strat}", base_spec, num, False, "")
        v = run(var, var_spec, num, True, f"{num} (diario da demo): {strat} com {mu['param']} {mu.get('de')} -> {mu['para']}")
        ok = v["t"] >= b["t"] + MIN_DT and v["meanR"] >= b["meanR"] + MIN_DR and v["n"] >= 0.5 * b["n"]
        res = (f"{num}: antes t {b['t']:+.2f}, {b['meanR']:+.3f}R/trade, win {b['win']:.0f}%, {b['n']} trades -> "
               f"depois t {v['t']:+.2f}, {v['meanR']:+.3f}R/trade, win {v['win']:.0f}%, {v['n']} trades ({v['por_moeda']}). ")
        if ok:
            res += "APLICADA: a demo passa a usar a variante." + ("" if v["pos_all"] else " Atencao: continua negativa em alguma moeda (so para ver ao vivo).")
            applied[var] = {**var_spec, "num": f"{orig.get('num', '')}+{num}", "base": var, "replaces": strat, "journal": True}
            save_specs(applied)
        else:
            why = [x for x, c in [(f"t nao subiu {MIN_DT}", v["t"] < b["t"] + MIN_DT), (f"R por trade nao subiu {MIN_DR}R", v["meanR"] < b["meanR"] + MIN_DR),
                                  ("perdeu mais de metade das trades", v["n"] < 0.5 * b["n"])] if c]
            res += "REJEITADA (" + "; ".join(why) + "): a estrategia fica como esta."
        print(res)
        update(ids, "aplicada" if ok else "rejeitada", res)
        log.append(f"{var}: {res}")
        with open("IDEAS.md", "a") as f:
            f.write(f"  Resultado {num}: {res}\n")
        for fn in os.listdir("results/runs"):   # a recontagem da estrategia atual e so a referencia do teste
            if fn.startswith("jbase~"):
                os.remove(os.path.join("results/runs", fn))
    if log and not a.dry:
        supa.log_event("teste", f"Diario do bot: {len(log)} mudanca(s) testada(s)", log)


if __name__ == "__main__":
    main()
