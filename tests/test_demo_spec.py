"""A demo experimental tem de decidir igual ao backtest: cada SPEC == a ideia de sr/swing_ideas.py, e engine.ts == demo_spec.py."""
import json
import os
import shutil
import subprocess

import numpy as np
import pandas as pd
import pytest

from sr.demo_spec import SPECS, entry_signal, exit_signal
from sr.swing import load_tf
from sr.swing_ideas import IDEAS

HAVE_DATA = os.path.exists("data/crypto/BTCUSDT_1h.csv.gz")


def _ref_entries(name, b):
    """Entradas da ideia original: vela onde o sinal (estado ou pulso) esta ligado e a anterior nao (para estados)
    ou simplesmente ligado (comparamos a condicao de entrada, por isso usamos o valor do sinal)."""
    from sr.demo_spec import SPECS as _S
    fn = IDEAS[_S.get(name, {}).get("base", name)][0]
    return pd.Series(np.sign(fn(b)), index=b.index)


@pytest.mark.skipif(not HAVE_DATA, reason="sem dados cripto")
@pytest.mark.parametrize("name", sorted(SPECS))
def test_spec_igual_a_ideia(name):
    spec = SPECS[name]
    if spec["tf"] in ("5m", "15m") and not os.path.exists("data/crypto/BTCUSDT_5m.csv.gz"):
        pytest.skip("sem dados de 5m (TF=5m python crypto_download.py ...)")
    btc = load_tf("btc", "1d", None)
    for coin in ("btc", "eth"):
        b = load_tf(coin, spec["tf"], None).iloc[-6000:]
        mine = entry_signal(b, spec, btc)
        ref = _ref_entries(name, b)
        skip = 1000   # aquecimento das medias
        if spec["signal_exit"]:
            # ideias com estado (_enter_exit): a entrada acontece quando o estado passa de 0 para ligado
            st = ref != 0
            starts = st & ~st.shift(1, fill_value=False)
            assert (starts.iloc[skip:] <= mine.iloc[skip:]).all(), f"{name}/{coin}: entrada da ideia sem sinal na spec"
        else:
            want = ref != 0
            diff = (want.iloc[skip:] != mine.iloc[skip:]).sum()
            assert diff == 0, f"{name}/{coin}: {diff} velas diferentes"


@pytest.mark.skipif(not HAVE_DATA or not shutil.which("node"), reason="sem node")
def test_engine_ts_igual_ao_python(tmp_path):
    btc = load_tf("btc", "1d", None)
    cases = []
    extra = {"_t_short_sma": {"num": "t", "tf": "1d", "side": -1, "entry": {"kind": "above_sma", "n": 50}, "trend_ema": 0,
                              "btc": "bear", "stop_atr": 2.0, "tp_r": 1.0, "max_hold": 3, "signal_exit": False},
             "_t_short_brk": {"num": "t", "tf": "4h", "side": -1, "entry": {"kind": "breakout", "n": 60}, "trend_ema": 200,
                              "btc": "bear", "stop_atr": 3.0, "tp_r": 1.0, "max_hold": 12, "signal_exit": False}}
    for name, spec in {**SPECS, **extra}.items():
        if spec["tf"] in ("5m", "15m") and not os.path.exists("data/crypto/ETHUSDT_5m.csv.gz"):
            continue
        b = load_tf("eth", spec["tf"], None).iloc[-720:]
        bd = btc[btc.index < b.index[-1] + pd.Timedelta(days=1)].iloc[-720:]
        cases.append({"name": name, "spec": spec,
                      "bars": [[int(t.value // 10**6), r.open, r.high, r.low, r.close, getattr(r, "volume", None)] for t, r in zip(b.index, b.itertuples())],
                      "btc": [[int(t.value // 10**6), r.open, r.high, r.low, r.close] for t, r in zip(bd.index, bd.itertuples())],
                      "py_entry": [bool(x) for x in entry_signal(b, spec, btc).iloc[-200:]],
                      "py_exit": [bool(x) for x in exit_signal(b, spec).iloc[-200:]]})
    f = tmp_path / "cases.json"
    f.write_text(json.dumps(cases))
    out = subprocess.run(["node", "--experimental-strip-types", "--no-warnings", "tests/engine_check.ts", str(f)],
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout + out.stderr
