from __future__ import annotations

import numpy as np
import pandas as pd


def summarize(tr: pd.DataFrame, years: float) -> dict:
    if tr is None or len(tr) == 0:
        return {"n": 0, "meanR": 0.0, "t": 0.0, "win%": 0.0, "R/ano": 0.0, "R/mes": 0.0, "maxDD_R": 0.0}
    r = tr["R"].to_numpy()
    sd = r.std(ddof=1) if len(r) > 1 else 0.0
    t = r.mean() / (sd / np.sqrt(len(r))) if sd > 0 else 0.0
    eq = np.cumsum(r)
    dd = (eq - np.maximum.accumulate(np.maximum(eq, 0))).min()
    return {"n": int(len(r)), "meanR": round(float(r.mean()), 3), "t": round(float(t), 2),
            "win%": round(float((r > 0).mean() * 100), 1), "R/ano": round(float(r.sum() / years), 1),
            "R/mes": round(float(r.sum() / years / 12), 2), "maxDD_R": round(float(dd), 1)}


def by_year(tr: pd.DataFrame) -> pd.Series:
    if tr is None or len(tr) == 0:
        return pd.Series(dtype=float)
    return tr.groupby(pd.DatetimeIndex(tr["time"]).year)["R"].sum().round(1)
