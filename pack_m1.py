"""
Comprime as velas de 1m (data/m1, criadas pelo download.py) para data/m1gz/<instrumento>_<ano>.csv.gz,
para poderem ir para o repo e o agente usar entradas em 1m.
  python pack_m1.py
"""
from __future__ import annotations

import glob
import os

import pandas as pd


def main():
    os.makedirs(os.path.join("data", "m1gz"), exist_ok=True)
    files = sorted(glob.glob(os.path.join("data", "m1", "*", "*.csv")))
    if not files:
        raise SystemExit("Nao ha ficheiros em data/m1. Corre primeiro: python download.py")
    total = 0
    for f in files:
        inst = os.path.basename(os.path.dirname(f))
        year = os.path.splitext(os.path.basename(f))[0]
        out = os.path.join("data", "m1gz", f"{inst}_{year}.csv.gz")
        df = pd.read_csv(f)
        df.columns = [c.strip().lower() for c in df.columns]
        df = df[["timestamp", "open", "high", "low", "close"]]
        df["timestamp"] = df["timestamp"].astype("int64")
        for c in ("open", "high", "low", "close"):
            df[c] = df[c].round(2)
        df.to_csv(out, index=False, compression="gzip")
        size = os.path.getsize(out) / 1e6
        total += size
        print(f"  {inst} {year}: {len(df):,} velas -> {size:.1f} MB")
    print(f"Total: {total:.0f} MB em data/m1gz")


if __name__ == "__main__":
    main()
