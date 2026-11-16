# TODO de testes (so isto se testa; o Antonio aprova itens novos)

## Fase 1 - base (parametros por defeito: tp 2R, stop 0.5 ATR, sessao rth)
- [x] `python run.py --play bounce --levels pdhl` -> REPROVADA, t junto -11.29
- [x] `python run.py --play bounce --levels pwhl` -> REPROVADA, t junto -6.90
- [x] `python run.py --play bounce --levels swing1h` -> REPROVADA, t junto -15.79
- [x] `python run.py --play bounce --levels round` -> REPROVADA, t junto -10.02
- [x] `python run.py --play break --levels pdhl` -> REPROVADA, t junto -4.55
- [x] `python run.py --play break --levels pwhl` -> REPROVADA, t junto 1.34 (NQ/ES +0.13R, Dow -0.03R)
- [x] `python run.py --play break --levels swing1h` -> REPROVADA, t junto -5.49
- [x] `python run.py --play break --levels round` -> REPROVADA, t junto -3.65
- [x] `python run.py --play fake --levels pdhl` -> REPROVADA, t junto -6.86
- [x] `python run.py --play fake --levels pwhl` -> REPROVADA, t junto -1.12 (so Dow positivo)
- [x] `python run.py --play fake --levels swing1h` -> REPROVADA, t junto -7.62
- [x] `python run.py --play fake --levels round` -> REPROVADA, t junto -4.19

## Fase 2 - robustez (so para combinacoes da fase 1 com t junto >= 1.5 no dev)
Para cada uma: tp {1, 1.5, 3} x stop-atr {0.3, 1.0} e tambem --session all.
Acrescenta aqui as linhas concretas quando a fase 1 acabar.
(2026-11-16: fase 1 concluida; nenhuma combinacao com t junto >= 1.5 -> fase 2 vazia. A melhor foi break-pwhl com t 1.34.) Uma variante so conta se a vizinhanca de
parametros tambem for positiva (nao um pico isolado).

## Fase 3 - holdout
So variantes com PASSA no dev e vizinhanca positiva. Uma vez cada. Ver CLAUDE.md.

## Setup do Antonio (pre-registado por ele em 2026-11-16) - prioridade maxima
Regras em sr/antonio.py (niveis S/R de 15m/30m/1h + dia/semana/Asia/Londres, displacement + IFVG de 1m,
stop no extremo do sweep, Asia+Londres+NY, max 3 trades/dia). Precisa de data/m1gz (se faltar, regista erro
"faltam velas de 1m" e salta estes itens). Fasquia t >= 2.5 (pre-registado por humano). Foco do relatorio: NQ.
- [x] `python run.py --play antonio --levels all --tp 1` -> REPROVADA (NQ -0.18R/trade, t junto -17.5)
- [x] `python run.py --play antonio --levels all --tp 2` -> REPROVADA (NQ -0.17R/trade, t junto -13.0)
- [x] `python run.py --play antonio --levels all --tp 3` -> REPROVADA (NQ -0.18R/trade, t junto -10.7)

## Mais trades (pedido do Antonio, 2026-11-16) - correr com run_swing.py e depois em pre e na carteira
- [x] `python run_swing.py --idea rsi2-dip-4h` (e `--period pre`) -> REPROVADA: muitas trades mas ~0R (dev 0.00, pre -0.03)
- [x] `python run_swing.py --idea ibs-dip-d` (e `--period pre`) -> NQ e S&P positivos nos dois periodos, Dow ligeiramente negativo
- [x] `python run_swing.py --idea down3-d` (e `--period pre`) -> pre positiva nos 3 (t 3.7), dev Dow negativo
- [x] carteira rsi2+ibs+down3, max 3 abertas: +8.7%/ano, 5/13 anos >= 14%, pior queda -21.6%, ~3.4 trades/semana
