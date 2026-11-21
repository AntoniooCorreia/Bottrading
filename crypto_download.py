"""
Descarrega velas de {TF} de crypto do arquivo publico da Binance (data.binance.vision) e grava
data/crypto/<SIMBOLO>_1h.csv.gz (UTC). Serve so para backtest: o preco do BTC e praticamente igual em
todas as exchanges; os custos usados nos testes sao os da Kraken.
  python crypto_download.py                 # BTC, ETH, SOL
  python crypto_download.py BTCUSDT
  TF=5m python crypto_download.py     # velas de 5m (scalping) -> data/crypto/<SIMBOLO>_5m.csv.gz
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
TF = os.environ.get("TF", "1h")
BASE = "https://data.binance.vision/data/spot/monthly/klines/{s}/" + TF + "/{s}-" + TF + "-{y}-{m:02d}.zip"
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
        months = []
        while (y, m) < (today.year, today.month):
            months.append((y, m))
            m += 1
            if m == 13:
                y, m = y + 1, 1
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(8) as ex:
            res = list(ex.map(lambda ym: month_df(sym, *ym), months))
        for (y, m), df in zip(months, res):
            if df is not None:
                parts.append(df)
                started = True
            elif started:
                print(f"  {sym} {y}-{m:02d}: em falta")
        if not parts:
            print(f"{sym}: sem dados")
            continue
        out = pd.concat(parts).drop_duplicates("ts").sort_values("ts")
        out.to_csv(os.path.join(OUT, f"{sym}_{TF}.csv.gz"), index=False, compression="gzip")
        t = pd.to_datetime(out["ts"], unit="ms", utc=True)
        print(f"{sym}: {len(out):,} velas de {TF} ({t.iloc[0].date()} -> {t.iloc[-1].date()})")


if __name__ == "__main__":
    main()
