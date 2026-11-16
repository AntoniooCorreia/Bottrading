# Bottrading

Backtests de suporte e resistencia em NQ / S&P 500 / Dow (velas de 5m, Dukascopy, custos de CFD).
Regras e protocolo em [CLAUDE.md](CLAUDE.md); o que falta testar em [TODO.md](TODO.md);
resultados em [results/RESULTS.md](results/RESULTS.md).

```
pip install -r requirements.txt
python download.py
python -m pytest -q
python run.py --play bounce --levels pdhl
```
