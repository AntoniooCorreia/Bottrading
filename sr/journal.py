"""
Diario do bot (pedido do Antonio, 2026-11-27): mudancas que o diario da demo propos e que o journal_lab.py testou e APLICOU.
Cada mudanca aplicada fica em sr/journal_specs.json como uma spec completa (a da demo com UM parametro mudado) e vira:
- uma ideia de backtest gerada a partir da spec (journal_ideas), para o crypto_lab e o demo_pick a poderem correr;
- uma spec da demo (sr/demo_spec.py carrega o ficheiro), que substitui a original ("replaces") na escolha do demo_pick.
A ideia e construida com sr/demo_spec.entry_signal/exit_signal, os mesmos sinais que a Edge Function usa (testado).
"""
from __future__ import annotations

import json
import os

import pandas as pd

FILE = os.path.join(os.path.dirname(__file__), "journal_specs.json")


def load_specs() -> dict:
    if not os.path.exists(FILE):
        return {}
    return json.load(open(FILE))


def save_specs(d: dict) -> None:
    json.dump(d, open(FILE, "w"), indent=1, ensure_ascii=True, sort_keys=True)


def vary(spec: dict, param: str, para) -> dict:
    """Copia da spec com UM parametro mudado (lo/hi/n vivem dentro de entry)."""
    v = json.loads(json.dumps(spec))
    if param in ("lo", "hi", "n"):
        v["entry"][param] = para
    else:
        v[param] = para
    return v


def idea_from_spec(spec: dict):
    """(fn, tf, stop_atr, tp_r, max_hold) + exits, como em sr/swing_ideas.IDEAS. Sinal +1/-1 = entrar (ou estado ligado)."""
    from sr.demo_spec import entry_signal, exit_signal
    from sr.swing import load_tf
    from sr.swing_ideas import _enter_exit
    btc = load_tf("btc", "1d", None)
    side = spec["side"]

    def fn(b: pd.DataFrame) -> pd.Series:
        en = entry_signal(b, spec, btc)
        if spec.get("signal_exit"):
            return _enter_exit(en, exit_signal(b, spec)) * side
        return en.astype(int) * side

    exits = {} if spec.get("signal_exit") else {"signal_exit": False}
    return (fn, spec["tf"], spec["stop_atr"], spec["tp_r"], spec["max_hold"]), exits


def journal_ideas() -> tuple[dict, dict, set]:
    """Ideias das mudancas aplicadas: (IDEAS, EXITS, NO_MIN_RISK) para juntar aos do swing_ideas."""
    from sr.swing_ideas import NO_MIN_RISK
    ideas, exits, nmr = {}, {}, set()
    for name, spec in load_specs().items():
        ideas[name], exits[name] = idea_from_spec(spec)
        if spec.get("orig_base") in NO_MIN_RISK:
            nmr.add(name)
    return ideas, exits, nmr
