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

## Ideias do agente (2026-11-17, sessao 3)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea rsi2-pop-short-4h` (e `--period pre`) -> REPROVADA, t junto -2.46 (dev negativa nos 3: NQ -0.01R, S&P -0.08R, Dow -0.08R; pre tambem negativa nos 3, t -2.09). Vender subidas em tendencia de baixa perde dinheiro: nao entra na carteira

## Ideias do agente (2026-11-17, sessao 4)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea ibs-bear-d` (e `--period pre`) -> REPROVADA no criterio oficial (poucas trades: NQ 51 < 60), t junto +1.62
  (dev NQ +0.056R, S&P +0.043R, Dow +0.048R; pre positiva nos 3, t +1.02) -> positiva nos 3 dos EUA nos dois periodos: pode ir a carteira
- [x] carteira + ibs-bear-d (2012-2025, mesmas regras de risco, 10 indices): MELHORA -> +12.5%/ano (era +9.5%), 6/14 anos >= 14% (era 5),
  pior queda -9.1% (era -10.7%), meses positivos 108/148 (era 102); piora pior mes -5.5% (era -5.1%) e pior ano -4.5% (era -2.5%, 2018).
  Positiva em todos os 10 indices. Ganho vem de 2020 (+7.9 -> +18.7%) e 2022 (-2.5 -> +10.4%). Nova carteira de referencia

## Ideias do agente (2026-11-18)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea turnaround-tue-d` (e `--period pre`) -> REPROVADA, t junto +0.21 (dev NQ -0.002R, S&P +0.023R, Dow -0.010R;
  pre positiva nos 3 mas minuscula, t +0.92). ~0R: o efeito de segunda/terca nao existe depois de custos. Nao entra na carteira

## Ideias do agente (2026-11-18, sessao 2)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea keyrev-d` (e `--period pre`) -> REPROVADA no criterio oficial (poucas trades: NQ 45 < 60), t junto +0.36
  (dev NQ +0.035R, S&P +0.022R, Dow +0.004R, ~0R; pre positiva nos 3, t +2.77) -> positiva nos 3 dos EUA nos dois periodos: testada na carteira
- [x] carteira + keyrev-d (mesmas regras de risco, 10 indices): PIORA -> +11.6%/ano (era +12.5%), 4/14 anos >= 14% (era 6), pior queda -12.2% (era -9.1%),
  17 meses abaixo de -3% (era 12); so melhora pior ano (-0.4%, era -4.5%) e pior mes (-4.9%, era -5.5%). Rouba lugares as outras ideias. Carteira de referencia mantem-se

## Ideias do agente (2026-11-18, sessao 3)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea pullback20-d` (e `--period pre`) -> REPROVADA no criterio oficial (poucas trades: NQ 49 < 60), t junto +1.15
  (dev NQ +0.106R, S&P +0.169R, Dow +0.007R; pre positiva nos 3, t +3.08) -> positiva nos 3 dos EUA nos dois periodos: testada na carteira
- [x] carteira + pullback20-d (mesmas regras de risco, 10 indices): PIORA -> +9.6%/ano (era +12.5%), 5/14 anos >= 14% (era 6), pior queda -11.4% (era -9.1%),
  pior mes -5.8% (era -5.5%), pior ano -5.0% (era -4.5%), 19 meses abaixo de -3% (era 12). Trades de semanas ocupam os lugares das compras de quedas
  (161 trades/ano, era 183) e e negativa fora dos EUA (FTSE, CAC, HSI, Euro Stoxx). Carteira de referencia mantem-se

## Ideias do agente (2026-11-18, sessao 4)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] `python run_swing.py --idea calmhigh-d` (e `--period pre`) -> REPROVADA, t junto +0.32 (dev NQ +0.124R/55 trades, S&P -0.059R, Dow -0.003R;
  pre t -0.01, NQ -0.040R). Nao e positiva nos 3 em nenhum dos periodos: nao vai a carteira. Comprar maximos em subidas calmas ~0R

## Holdout da carteira (decisao do Antonio, 2026-11-18) - UMA vez, sem afinar depois
Antes da conta demo. Mesmas ideias e regras de risco da C5, periodo 2025-01-01 a 2026-11-15 (fim dos dados).
Os indicadores (media de 200 etc.) aquecem com dados de antes de 2025; so contam trades com entrada >= 2025-01-01.
Leitura combinada antes de ver: positiva no total e sem pior mes abaixo de -6% -> segue para demo; caso contrario, decide o Antonio.
- [x] C9: `python portfolio.py --ideas rsi2-dip-d,ibs-dip-d,down3-d,ibs-bear-d --period holdout --unlock-holdout --max-open 3 --region-cap 1 --month-stop 3 --label C9`
  -> POSITIVA: 2025 +17.2%, 2026 (ate 15/11) +34.5%, pior mes -3.6%, pior queda -7.4%, 16/23 meses positivos, ~440 trades.
  Cumpre a leitura combinada (positiva e pior mes > -6%) -> segue para demo. 2025-26 foram anos de subida: resultado acima do esperado, tratar com cautela

## Erro na carteira (2026-11-18) - refazer com portfolio.py corrigido (pedido pelo protocolo, ponto 5)
- [x] C11: C5 corrigida (`--label C11 --ref`) -> +0.9%/ano, 1/14 anos >= 14%, pior ano -14.7%, pior queda -22.0%
- [x] C12: C11 `--sem-domingos` (como o MT5) -> +2.2%/ano, pior ano -9.2%, pior queda -13.6%
- [x] C13: C11 so NQ -> +2.1%/ano, pior ano -0.9%, pior queda -4.0%

## Futuros e carteiras corrigidas (decisao do Antonio, 2026-11-18) - correr por ordem, mesmas regras de risco
Base: C11 (C5 corrigida). Agora com custos de micro-futuros. Uma carteira so substitui a referencia se tiver mais % ao ano
(compara sempre pior mes e pior ano). Ideias que mudam a carteira: so as ja aprovadas pela regra 2012-2018 + 2019-2024.
- [x] C14: `python portfolio.py --ideas rsi2-dip-d,ibs-dip-d,down3-d,ibs-bear-d --period tudo --max-open 3 --region-cap 1 --month-stop 3 --custos fut --label C14` -> +1.8%/ano, 1/14 anos >= 14%, pior mes -5.4%, pior ano -13.8%, pior queda -20.0%, 126 trades/ano
- [x] C15: o mesmo que C14 com `--markets nq --label C15` (so MNQ) -> +2.4%/ano, pior mes -1.9%, pior ano -0.7%, pior queda -3.4%, 31 trades/ano
- [x] C16: C14 + double7-d (refaz C3 sem o erro) `--label C16` -> +2.2%/ano, pior mes -6.0%, pior ano -9.4%, pior queda -19.6% (melhora C14 pouco, piora pior mes)
- [x] C17: C14 + week-rev-d (refaz C4) `--label C17` -> +2.2%/ano, pior mes -5.7%, pior ano -10.6%, pior queda -18.6%
- [x] C18: C14 + keyrev-d (refaz C6) `--label C18` -> +1.9%/ano, pior mes -5.5%, pior ano -11.4%, pior queda -19.2%
- [x] C19: C14 + pullback20-d (refaz C7) `--label C19` -> +1.3%/ano, pior queda -20.0% (piora)
- [x] C20: so NQ com rsi2-dip-d + ibs-dip-d + down3-d + ibs-bear-d + double7-d, `--markets nq --custos fut --label C20` -> +2.6%/ano, pior mes -1.7%, pior ano -1.5%, pior queda -3.0%, 31 trades/ano -> NOVA REFERENCIA (melhor % e muito mais estavel)
Depois: modo ideias com o FOCO ATUAL (1h/4h, stops que caibam em MNQ).

## Ideias do agente (2026-11-18, sessao 5)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0. Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] #40: `python run_swing.py --idea fomc-holiday-1h` (e `--period pre`) -> PASSA no dev (fut t junto +3.81; NQ +0.197R/125 trades,
  S&P +0.165R/124, Dow +0.104R/121; CFD t +3.45). 2012-2018: t +0.85 (NQ +0.065R, S&P +0.036R, Dow +0.016R; positiva nos 3 mas ~0).
  Holdout (uma vez): t +0.29 (NQ +0.053R/38, S&P -0.041R/41, Dow +0.051R/42). Leitura: o forte de 2019-2024 nao se repete; edge fraco
- [x] C21: C20 + fomc-holiday-1h, so NQ: `python portfolio.py --ideas rsi2-dip-d,ibs-dip-d,down3-d,ibs-bear-d,double7-d,fomc-holiday-1h --markets nq --custos fut --period tudo --max-open 3 --region-cap 1 --month-stop 3 --label C21`
  (registado antes de correr; entra pela regra "positiva nos 3 dos EUA em 2012-2018 e 2019-2024". So substitui a referencia se for MELHOR)
  -> +5.6%/ano, 1/14 anos >= 14%, pior mes -3.9%, pior ano -0.4%, pior queda -6.4%, 44 trades/ano. 2012 +16% quase todo do #40 (sorte);
  2013-2025 ~+4.8%/ano. Mais %/ano que C20 mas o #40 falhou em 2012-18 e no holdout: NAO troquei a referencia, decide o Antonio

## Ideias do agente (2026-11-18, sessao 6)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0 (custos de futuros). Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] #41: `python run_swing.py --idea flush-1h` (e `--period pre`) -> REPROVADA (fut t junto +0.15; NQ +0.038R/346 trades,
  S&P -0.017R/348, Dow -0.012R/307; CFD t +0.12). 2012-2018: t -2.95 (NQ -0.043R, S&P -0.122R, Dow -0.004R). Vela de 1h violenta nao reverte

## Ideias do agente (2026-11-18, sessao 7)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0 (custos de futuros). Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [x] #42: `python run_swing.py --idea ibs-cash-1h` (e `--period pre`) -> REPROVADA no oficial (fut t junto +2.80 < 3.0; NQ +0.164R/263 trades,
  S&P +0.145R/261, Dow +0.081R/265; CFD t +2.24). 2012-2018 (fut): t +1.86 (NQ +0.221R/275, S&P +0.045R/310, Dow +0.010R/206).
  Positiva nos 3 dos EUA nos 2 periodos (futuros; em CFD o Dow 2012-18 da -0.009R) -> pode entrar na carteira pela regra
- [x] C22: C20 com ibs-cash-1h NO LUGAR do ibs-dip-d (como registado em IDEAS.md), so NQ, futuros:
  `python portfolio.py --ideas rsi2-dip-d,ibs-cash-1h,down3-d,ibs-bear-d,double7-d --markets nq --custos fut --period tudo --max-open 3 --region-cap 1 --month-stop 3 --label C22`
  (registado antes de correr. So substitui a referencia C20 se for MELHOR: mais %/ano sem piorar muito pior mes/pior queda)
  -> +5.8%/ano, 4/14 anos >= 14%, pior mes -4.5%, pior ano -5.7%, pior queda -12.8%, 41 trades/ano, 6 anos negativos.
  Mais %/ano mas pior queda 4x a da C20: NAO troquei a referencia, decide o Antonio

## Ideias do agente (2026-11-18, sessao 8)
Registada em IDEAS.md antes de correr. Fasquia t >= 3.0 (custos de futuros). Correr dev e depois `--period pre` (2012-2018) como confirmacao.
- [ ] #43: `python run_swing.py --idea rsi2-cash-1h` (e `--period pre`)
- [ ] C23 (so se #43 for positiva nos 3 dos EUA em 2019-2024 e em 2012-2018): C22 com rsi2-cash-1h NO LUGAR do rsi2-dip-d, so NQ, futuros:
  `python portfolio.py --ideas rsi2-cash-1h,ibs-cash-1h,down3-d,ibs-bear-d,double7-d --markets nq --custos fut --period tudo --max-open 3 --region-cap 1 --month-stop 3 --label C23`
  (So substitui a referencia C20 se for MELHOR: mais %/ano sem piorar muito pior mes/pior queda)
