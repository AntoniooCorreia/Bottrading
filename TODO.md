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

## Ideias do agente (2026-11-16)
Registadas em IDEAS.md antes de correr. Fasquia t >= 3.0.
- [x] `python run.py --play gapfill --levels pdc` -> REPROVADA, t junto -1.34 (NQ -0.08R, ES +0.01R, Dow -0.01R)
- [x] `python run.py --play fake --levels onhl` -> REPROVADA, t junto -4.62 (negativa nos 3)
- [x] `python run.py --play break --levels nr4` -> REPROVADA, t junto -1.12 (so NQ positivo, +0.07R)
- [x] `python run.py --play break --levels lunchhl` -> REPROVADA, t junto -3.41 (negativa nos 3)
- [x] `python run.py --play gapgo --levels pdc` -> REPROVADA (t < 3), t junto +2.34 (positiva nos 3: NQ +0.05R, ES +0.13R, Dow +0.10R)
- [x] `python run.py --play break --levels monhl` -> REPROVADA, t junto +0.15 (Dow negativo)

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

## Ideias do agente (2026-11-17)
Registadas em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea tom-d` (e `--period pre`) -> REPROVADA, t junto +1.30 (dev positiva nos 3 mas pequena: NQ +0.06R; pre negativa nos 3, t -0.47)
- [x] `python run_swing.py --idea overnight-us-1h` (e `--period pre`) -> REPROVADA, t junto -1.60 (dev NQ -0.005R, S&P -0.02R, Dow -0.05R; pre negativa nos 3, t -5.44). Nota: os dados tem velas paradas ao fim de semana, por isso a trade de sexta sai no sabado e volta a entrar (custo a dobrar ~1 vez/semana); com futuros o NQ dava +0.04R mas S&P/Dow ~0 ou negativos, nao muda a conclusao
- [x] `python run_swing.py --idea double7-d` (e `--period pre`) -> PASSA no dev, t junto +3.07 (NQ +0.20R, S&P +0.14R, Dow +0.04R); pre tambem PASSA (t +3.46). Holdout (uma vez): positiva nos 3 mas so 78 trades, t +1.51 (ver HOLDOUT_LOG.md)
- [x] carteira + double7-d (2012-2024, mesmas regras de risco): nos 10 indices piora (+7.3%/ano, pior queda -16.5%: double7 e negativa em FTSE/Nikkei/ASX/HSI);
  so nos EUA (onde foi validada) fica igual (+9.4%/ano, pior queda -9.7%, pior ano -1.8%). Carteira de referencia mantem-se.

## Ideias do agente (2026-11-17, sessao 2)
Registadas em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea opex-week-d` (e `--period pre`) -> REPROVADA, t junto -0.98 (dev negativa nos 3: NQ -0.01R, S&P -0.06R, Dow -0.04R). Em 2012-2018 passava (t +3.38): o efeito parece ter desaparecido
- [x] `python run_swing.py --idea nr7-up-d` (e `--period pre`) -> REPROVADA, t junto -0.77 (dev negativa nos 3; pre t +1.86, so NQ claramente positivo)
- [x] `python run_swing.py --idea week-rev-d` (e `--period pre`) -> REPROVADA (t < 3), t junto +1.83 (dev NQ +0.15R, S&P +0.11R, Dow +0.04R; ~11 trades/ano por indice).
  Positiva nos 3 dos EUA tambem em 2012-2018 (t +2.71, Dow com 57 trades) -> pode ir a carteira pela regra do CLAUDE.md
- [x] carteira + week-rev-d (2012-2024, mesmas regras de risco): nos 10 indices piora (+5.8%/ano, pior queda -13.8%); so nos EUA
  tambem piora (+8.9%/ano, pior queda -14.5%, 19 meses abaixo de -3%). Carteira de referencia mantem-se (+9.5%/ano)
