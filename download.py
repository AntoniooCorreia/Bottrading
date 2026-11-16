"""
Descarrega velas de 1m da Dukascopy (NQ, S&P 500, Dow) e cria data/m5/<instrumento>.csv.gz
  python download.py              # 2019 ate hoje
  python download.py 2019 2026
Precisa de Node.js (usa npx dukascopy-node) e de acesso a datafeed.dukascopy.com.
Anos ja descarregados sao reaproveitados.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from datetime import date

import pandas as pd

from sr.data import INSTR, M5_DIR, m5_path, resample_m1_to_m5

Y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2019
Y1 = int(sys.argv[2]) if len(sys.argv) > 2 else date.today().year


def get_year(inst: str, y: int) -> str | None:
    out = os.path.join("data", "m1", inst, f"{y}.csv")
    if os.path.exists(out) and os.path.getsize(out) > 10_000 and y < date.today().year:
        return out
    tmp = os.path.join("data", "tmp", inst)
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    end = f"{y + 1}-01-01" if y < date.today().year else date.today().isoformat()
    cmd = ["npx", "--yes", "dukascopy-node", "-i", inst, "-from", f"{y}-01-01", "-to", end,
           "-t", "m1", "-f", "csv", "-dir", tmp, "-r", "3"]
    print(f"  {inst} {y}: a descarregar...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    files = glob.glob(os.path.join(tmp, "*.csv"))
    if r.returncode != 0 or not files:
        print(f"  {inst} {y}: FALHOU\n{r.stdout[-500:]}\n{r.stderr[-500:]}")
        shutil.rmtree(tmp, ignore_errors=True)
        return None
    shutil.move(files[0], out)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def main():
    os.makedirs(M5_DIR, exist_ok=True)
    for key, inst in INSTR.items():
        parts = []
        for y in range(Y0, Y1 + 1):
            f = get_year(inst, y)
            if f:
                df = pd.read_csv(f)
                df.columns = [c.strip().lower() for c in df.columns]
                df.index = pd.to_datetime(df["timestamp"].astype("int64"), unit="ms", utc=True)
                parts.append(df[["open", "high", "low", "close"]])
        if not parts:
            print(f"{key}: sem dados")
            continue
        m1 = pd.concat(parts).sort_index()
        m1 = m1[~m1.index.duplicated(keep="last")]
        m5 = resample_m1_to_m5(m1)
        m5.index.name = "time"
        m5.reset_index().to_csv(m5_path(key), index=False, compression="gzip")
        print(f"{key}: {len(m5):,} velas de 5m ({m5.index[0].date()} -> {m5.index[-1].date()})")


if __name__ == "__main__":
    main()
