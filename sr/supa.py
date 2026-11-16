"""Envia resultados para o Supabase (dashboard). Nao faz nada se BT_WRITE_TOKEN nao estiver definido."""
from __future__ import annotations

import json
import os
import urllib.request

URL = os.environ.get("BT_SUPABASE_URL", "https://ctyndeyumrvcwlxzdgnz.supabase.co")
PUBLISHABLE = "sb_publishable_hMd_xtAGBa1zcJY30QRNIA_LupFPdfp"   # chave publica (so leitura + RPCs com token)


def _rpc(fn: str, payload: dict) -> bool:
    token = os.environ.get("BT_WRITE_TOKEN")
    if not token:
        return False
    body = json.dumps({"p_token": token, **payload}).encode()
    req = urllib.request.Request(f"{URL}/rest/v1/rpc/{fn}", data=body, method="POST", headers={
        "apikey": PUBLISHABLE, "Authorization": f"Bearer {PUBLISHABLE}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200 <= r.status < 300
    except Exception as e:  # o dashboard nunca pode partir um backtest
        print(f"[supabase] {fn} falhou: {e}")
        return False


def report_run(run: dict) -> bool:
    return _rpc("report_run", {"p_run": run})


def set_state(key: str, value) -> bool:
    return _rpc("set_state", {"p_key": key, "p_value": value})


def log_event(kind: str, message: str) -> bool:
    return _rpc("log_event", {"p_kind": kind, "p_message": message})
