"""
Descarrega velas de 1h de crypto do arquivo publico da Binance (data.binance.vision) e grava
data/crypto/<SIMBOLO>_1h.csv.gz (UTC). Serve so para backtest: o preco do BTC e praticamente igual em
todas as exchanges; os custos usados nos testes sao os da Kraken.
  python crypto_download.py                 # BTC, ETH, SOL
  python crypto_download.py BTCUSDT
"""
from __future__ import annotations

import io
import os
import sys
import urllib.request
import zipfile
from datetime import date

import pandas as pd

SYMBOLS = sys.argv[1:] or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
BASE = "https://data.binance.vision/data/spot/monthly/klines/{s}/1h/{s}-1h-{y}-{m:02d}.zip"
OUT = os.path.join("data", "crypto")


def month_df(sym: str, y: int, m: int) -> pd.DataFrame | None:
    try:
        with urllib.request.urlopen(BASE.format(s=sym, y=y, m=m), timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
    except Exception:
        return None
    raw = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4, 5])
    raw.columns = ["ts", "open", "high", "low", "close", "volume"]
    ts = raw["ts"].astype("int64")
    ts = ts.where(ts < 10 ** 14, ts // 1000)          # desde 2025 a Binance usa microssegundos
    raw["ts"] = ts
    return raw


def main():
    os.makedirs(OUT, exist_ok=True)
    today = date.today()
    for sym in SYMBOLS:
        parts, y, m, started = [], 2017, 1, False
        while (y, m) < (today.year, today.month):
            df = month_df(sym, y, m)
            if df is not None:
                parts.append(df)
                started = True
            elif started:
                print(f"  {sym} {y}-{m:02d}: em falta")
            m += 1
            if m == 13:
                y, m = y + 1, 1
        if not parts:
            print(f"{sym}: sem dados")
            continue
        out = pd.concat(parts).drop_duplicates("ts").sort_values("ts")
        out.to_csv(os.path.join(OUT, f"{sym}_1h.csv.gz"), index=False, compression="gzip")
        t = pd.to_datetime(out["ts"], unit="ms", utc=True)
        print(f"{sym}: {len(out):,} velas de 1h ({t.iloc[0].date()} -> {t.iloc[-1].date()})")


if __name__ == "__main__":
    main()
