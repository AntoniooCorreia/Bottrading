"""Dados: velas de 5m (hora de Nova Iorque) a partir dos ficheiros criados por download.py."""
from __future__ import annotations

import os

import pandas as pd

TZ = "America/New_York"
INSTR = {"nq": "usatechidxusd", "es": "usa500idxusd", "dow": "usa30idxusd"}
# custo ida-e-volta em pontos (spread CFD + slippage) e passo dos numeros redondos
SPEC = {
    "nq": {"cost_pts": 2.0, "round": 250.0},
    "es": {"cost_pts": 0.6, "round": 50.0},
    "dow": {"cost_pts": 3.0, "round": 500.0},
}
PERIODS = {
    "dev": ("2019-01-01", "2024-12-31"),       # para escolher / afinar
    "holdout": ("2025-01-01", "2030-12-31"),   # FECHADO: so com --unlock-holdout
    "pre": ("2012-01-01", "2018-12-31"),       # anos antigos: teste "as cegas" para ideias ja vistas no dev
}
M5_DIR = os.path.join("data", "m5")


def m5_path(key: str) -> str:
    return os.path.join(M5_DIR, f"{INSTR[key]}.csv.gz")


def load_m5(key: str, period: str | None = None) -> pd.DataFrame:
    path = m5_path(key)
    if not os.path.exists(path):
        raise SystemExit(f"Falta {path}. Corre primeiro: python download.py")
    df = pd.read_csv(path)
    idx = pd.DatetimeIndex(pd.to_datetime(df["time"], utc=True)).tz_convert(TZ)
    df = df[["open", "high", "low", "close"]].astype(float).set_index(idx).sort_index()
    if period:
        a, b = PERIODS[period]
        df = df[(df.index >= pd.Timestamp(a, tz=TZ)) & (df.index <= pd.Timestamp(b, tz=TZ) + pd.Timedelta(days=1))]
    return df


def resample_m1_to_m5(m1: pd.DataFrame) -> pd.DataFrame:
    """m1 com indice UTC -> m5 (indice UTC), rotulo = inicio da vela."""
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    return m1.resample("5min", label="left", closed="left").agg(agg).dropna()


M1_DIR = os.path.join("data", "m1gz")


def load_m1(key: str, period: str | None = None) -> pd.DataFrame:
    """Velas de 1m (indice UTC) a partir de data/m1gz/<instrumento>_<ano>.csv.gz (criados por pack_m1.py)."""
    import glob
    files = sorted(glob.glob(os.path.join(M1_DIR, f"{INSTR[key]}_*.csv.gz")))
    if not files:
        raise SystemExit(f"Faltam velas de 1m em {M1_DIR}. No PC: python pack_m1.py e push de data/m1gz")
    a, b = PERIODS[period] if period else ("1900-01-01", "2100-01-01")
    parts = []
    for f in files:
        y = int(os.path.basename(f).split("_")[-1][:4])
        if y < int(a[:4]) or y > int(b[:4]):
            continue
        df = pd.read_csv(f)
        df.index = pd.to_datetime(df["timestamp"].astype("int64"), unit="ms", utc=True)
        parts.append(df[["open", "high", "low", "close"]].astype(float))
    m1 = pd.concat(parts).sort_index()
    m1 = m1[~m1.index.duplicated(keep="last")]
    return m1[(m1.index >= pd.Timestamp(a, tz=TZ)) & (m1.index <= pd.Timestamp(b, tz=TZ) + pd.Timedelta(days=1))]
