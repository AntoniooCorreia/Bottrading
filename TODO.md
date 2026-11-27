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
- [x] #43: `python run_swing.py --idea rsi2-cash-1h` (e `--period pre`) -> REPROVADA (fut t junto +0.92; NQ +0.325R/109 trades,
  S&P -0.024R/136, Dow +0.021R/144; CFD t +0.63). 2012-2018 (fut): t +2.98 (NQ +0.303R/127, S&P +0.198R/124, Dow +0.279R/99).
  S&P negativo em 2019-24 -> nao cumpre a regra dos 3 indices nos 2 periodos. NQ forte nos dois periodos (+0.3R/trade), mas so no NQ = detetor de sorte falha
- [x] C23 NAO CORRIDA: a condicao registada falhou (#43 negativa no S&P em 2019-24). Era: (so se #43 for positiva nos 3 dos EUA em 2019-2024 e em 2012-2018): C22 com rsi2-cash-1h NO LUGAR do rsi2-dip-d, so NQ, futuros:
  `python portfolio.py --ideas rsi2-cash-1h,ibs-cash-1h,down3-d,ibs-bear-d,double7-d --markets nq --custos fut --period tudo --max-open 3 --region-cap 1 --month-stop 3 --label C23`
  (So substitui a referencia C20 se for MELHOR: mais %/ano sem piorar muito pior mes/pior queda)

## Cripto (2026-11-18, missao noturna: aumentar o win rate sem matar o resultado)
Sem itens [ ]: o agente entra em modo ideias (ver CLAUDE.md, seccao MISSAO NOTURNA). Cada ideia nova entra aqui antes de correr.

## Ideias do agente (2026-11-19, cripto sessao 1)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev` (e `--period pre` se passar dev + confirmacao).
- [x] #100: k-sma200-4h-persist -> PASSA no dev (t +3.06; BTC +2.26R/77, ETH +1.67R/75, SOL +2.21R/60; confirmacao 5/5; win rate 28%, antes 16%).
  Pre 2017-18 positivo (+0.59R/trade). Holdout (uma vez): BTC/ETH/SOL +0.79R/trade, t 1.53, 2025 +15.7%, mas confirmacao 1/5 -> misto, nao robusta
- [x] #101: k-dc55-4h-btcbull -> REPROVADA (SOL 53 trades < 60); t +3.02, win rate 34%, confirmacao 5/5; carteira sem ano negativo no dev (pior 2019 +21.4%)
- [x] #102: k-dc55-4h-wide -> REPROVADA (SOL 59 trades < 60); t +3.44, win rate 42% (antes 35%), +0.44R/trade (antes +0.66R); carteira +17%/ano, pior ano -4.9%
- [x] #103: k-dip-hold-4h -> REPROVADA (t +0.77; +0.04R/trade; win rate 49%)

## Ideias do agente (2026-11-19, cripto sessao 2 :30)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev` (e `--period pre` se passar dev + confirmacao).
- [x] #104: k-dc55-4h-bw-tp1 -> PASSA no dev (t +3.05; BTC +0.154R/102, ETH +0.057R/109, SOL +0.223R/79; confirmacao 5/5; win rate 47%).
  Pre 2017-18 negativo (1 trade, -0.52R): REPROVADA no pre (o filtro BTC so deixou entrar 9 dias em 2018; pre quase vazio). Holdout NAO aberto
- [x] #105: k-persist-bw -> REPROVADA (t +2.74; BTC 39, ETH 42, SOL 31 trades < 60); +1.70R/trade, win rate 38%, carteira +31.7%/ano, pior ano -6.5%
- [x] #106: k-persist-bw-tp1 -> PASSA no dev (t +4.64; BTC +0.226R/100, ETH +0.161R/106, SOL +0.304R/71; confirmacao 5/5; win rate 54%).
  Pre 2017-18 negativo (2 trades, -0.75R): REPROVADA no pre (pre quase vazio pelo filtro BTC). Holdout NAO aberto
- [x] #107: k-dc20-d-bull-tp1 -> REPROVADA (SOL 57 trades < 60); t +4.43, win rate 60%, +0.277R/trade, confirmacao 5/5; carteira +8.6%/ano, pior ano 0.0%, pior mes -2.0%

## Ideias do agente (2026-11-19, cripto sessao 3 :00)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev` (e `--period pre` se passar dev + confirmacao).
- [x] #108: k-persist-bw-half -> REPROVADA (t +2.59; BTC +0.876R/45, ETH +0.507R/47, SOL +0.889R/32 < 60; confirmacao 5/5; win rate 42%).
  Carteira +13.6%/ano, pior ano -6.0% (2023), pior mes -2.8%. Parcial: R/trade +0.74 (vs +0.22 da #106) mas win rate 42% (vs 54%)
- [x] #109: k-dc20-4h-bw-tp1 -> REPROVADA (t +2.67; BTC +0.093R/157, ETH +0.048R/166, SOL +0.102R/123; confirmacao 4/5; win rate 41%).
  Carteira +3.2%/ano, pior ano 0.0%, pior mes -4.0%
- [x] #110: k-dc20-4h-bw-half -> REPROVADA (t +2.54; BTC +0.138R/104, ETH +0.107R/120, SOL +0.148R/89; confirmacao 4/5; win rate 36%).
  Carteira +6.8%/ano, pior ano 0.0%, pior mes -4.9%
- [x] #111: k-dc20-4h-bw-be -> REPROVADA por pouco (t +2.96 < 3.0; BTC +0.266R/104, ETH +0.203R/120, SOL +0.205R/89; confirmacao 5/5; win rate 35%).
  Carteira +11.9%/ano, pior ano 0.0% (sem ano negativo), pior mes -4.9%

## Ideias do agente (2026-11-19, cripto sessao 4 :30)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev` (e `--period pre` se passar dev + confirmacao).
- [x] #112: k-dc20-d-own-tp1 -> REPROVADA (BTC 55, SOL 44 trades < 60); t +4.13, win rate 60%, +0.28R; confirmacao 4/5; carteira +7.4%/ano, pior ano -2.1% (2019)
- [x] #113: k-sma100-d-bull-tp1 -> PASSA dev (t +4.78; BTC +0.266R/85, ETH +0.174R/93, SOL +0.308R/69; win rate 53%; confirmacao 4/5;
  carteira +10.0%/ano, pior ano 0.0%, pior mes -2.8%). Pre 2017-18: 1 trade (ETH -0.26R) -> REPROVADA no pre (regra: pre >= 0). Holdout NAO aberto
- [x] #114: k-pb-d-bull-tp1 -> REPROVADA (t +1.82; +0.12R/trade; win rate 66%; SOL 33 trades; pior ano -3.2%, pior mes -5.1%)
- [x] #115: k-dc20-d-own-be -> REPROVADA (20-25 trades por moeda; t +1.93; +1.74R/trade; win rate 50%; +19.7%/ano mas 2021 +95% e 2023 -7.3%)

## Ideias do agente (2026-11-19, cripto sessao 5 :00)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev` (e `--period pre` se passar dev + confirmacao).
- [x] #116: k-sma100-d-b100-tp1 -> PASSA dev (t +4.63; BTC +0.267R/89, ETH +0.180R/93, SOL +0.264R/73; win rate 53%; confirmacao 4/5;
  carteira +10.0%/ano, pior ano -4.9% (2022), pior mes -2.8%). Pre 2017-18: 20 trades, +0.006R/trade (BTC -0.05R/12, ETH +0.09R/8) -> >= 0, passa por um fio.
  Holdout 2025-26 (UMA vez): +0.044R/trade (BTC -0.02R/17, ETH +0.19R/17, SOL -0.02R/22), win rate 46%, confirmacao 3/5, 2025 +4.3%, 2026 -1.8%
  -> REPROVADA (< 60 trades; efeito quase nulo). Holdout gasto
- [x] #117: k-sma600-4h-bull-tp1 -> PASSA dev (t +3.78; BTC +0.190R/121, ETH +0.077R/133, SOL +0.170R/98; win rate 40%; confirmacao 5/5;
  carteira +4.4%/ano, pior ano 0.0%, pior mes -2.7%). Pre 2017-18: 1 trade (ETH -0.66R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #118: k-sma100-d-bull-bracket -> REPROVADA (SOL 54 trades < 60); t +4.87, BTC +0.393R/63, ETH +0.225R/72, SOL +0.390R/54; win rate 68%;
  confirmacao 5/5 (win rate 62%); carteira +10.3%/ano, pior ano -2.0% (2022), pior mes -4.1%. Pre/holdout NAO corridos (falhou o dev)
- [x] #119: k-sma100-d-slope-tp1 -> REPROVADA (SOL 58 trades < 60); t +4.10, BTC +0.238R/75, ETH +0.199R/77, SOL +0.263R/58; win rate 53%;
  confirmacao 4/5; carteira +8.1%/ano, pior ano 0.0%, pior mes -2.7% (pior que a #113: menos trades, mesmo win rate)

## Ideias do agente (2026-11-21, cripto sessao :00 19h UTC)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --push --num "#138"` (e `--period pre` se passar).
- [x] #138: k-sma600-4h-bull-bracket -> REPROVADA (t junto +2.47 < 3.0); BTC +0.097R/246, ETH +0.051R/273, SOL +0.150R/173; win rate 59%;
  confirmacao 5/5; carteira K41: +5.5%/ano, pior ano -2.1%, pior mes -9.3%, 1.2 trades/semana (base K20: 0.6). Pre/holdout NAO corridos

## Ideias do agente (2026-11-22, cripto sessao :00 00h; base K20 = #118)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --push --num "#13x" --nota "..."` (e `--period pre` se passar).
- [x] #139: k-sma100-d-bull-bracket-mh10 -> PASSA dev (t +4.12; BTC +0.135R/142, ETH +0.104R/135, SOL +0.235R/92; win rate 57%; confirmacao 5/5);
  carteira K42: +9.1%/ano, pior ano -1.5%, pior mes -3.9%, pior queda -11.1%, 1.2 trades/semana. Pre 2017-18: 1 trade (ETH -1.03R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #140: k-sma100-d-own-bracket -> REPROVADA (SOL 56 trades < 60); t +4.31, BTC +0.369R/71, ETH +0.207R/81, SOL +0.277R/56; win rate 65%;
  confirmacao 5/5; carteira K43: +9.7%/ano mas 2022 -13.5% (pior queda -17.7%), 0.7 trades/semana
- [x] #141: k-sma100-d-bull-bracket-s2 -> PASSA dev (t +3.47; BTC +0.158R/118, ETH +0.148R/127, SOL +0.276R/86; win rate 62%; confirmacao 4/5);
  carteira K44: +10.2%/ano, pior ano -2.1%, pior mes -5.3%, pior queda -18.1%, 1.1 trades/semana. Pre 2017-18: 1 trade (ETH -1.05R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #142: carteira #118 + #107 (K45) -> as duas REPROVADAS sozinhas (SOL < 60); a carteira junta so mais 14 trades em 6 anos (0.6/semana):
  win rate 64%, +9.8%/ano, pior ano -2.0%, pior mes -4.1%, pior queda -8.0%. Sobrepoem-se quase sempre

## Ideias do agente (2026-11-22, cripto sessao :30 00h30; base K44 = #141)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --push --num "#14x" --nota "..."` (e `--period pre` se passar).
- [x] #143: k-sma100-d-bull-bracket-s2-mh10 -> PASSA dev (t +3.20; BTC +0.106R/182, ETH +0.101R/173, SOL +0.175R/126; win rate 57%; conf. 4/5);
  carteira K46: +9.8%/ano, pior ano -2.9%, pior mes -6.4%, 1.5 trades/semana. Pre 2017-18: 1 trade (ETH -1.05R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #144: k-sma50-d-bull-bracket-s2 -> PASSA dev (t +3.69; BTC +0.191R/110, ETH +0.149R/125, SOL +0.289R/83; win rate 63%; conf. 5/5);
  carteira K47: +10.6%/ano, pior ano -0.7%, pior mes -5.3%, 1.0 trades/semana. Pre 2017-18: 1 trade (BTC -1.04R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #145: k-ema100-d-bull-bracket-s2 -> PASSA dev (t +3.37; BTC +0.155R/128, ETH +0.132R/132, SOL +0.245R/102; win rate 61%; conf. 4/5);
  carteira K48: +10.4%/ano, pior ano -4.3% (2022), pior mes -5.3%, 1.2 trades/semana. Pre 2017-18: 47 trades, -0.058R, win rate 49%, 2018 -7.5% -> REPROVADA no pre. Holdout NAO aberto
- [x] #146: k-sma100-d-bull50-bracket-s2 -> PASSA dev (t +3.88; BTC +0.127R/111, ETH +0.215R/117, SOL +0.333R/78; win rate 63%; conf. 5/5);
  carteira K49: +10.9%/ano, pior ano 0.0%, pior mes -5.3%, pior queda -17.0%, 1.0 trades/semana. Pre 2017-18: 1 trade (ETH -1.05R) -> REPROVADA no pre. Holdout NAO aberto

## Ideias do agente (2026-11-22, cripto sessao :00 01h; base K49 = #146)
Registadas em IDEAS.md antes de correr.
- [x] #147: k-sma50-d-bull50-bracket-s2 -> PASSA dev (t +4.10; BTC +0.171R/107, ETH +0.204R/118, SOL +0.331R/79; win rate 64%; conf. 5/5);
  carteira K54: +11.4%/ano, pior ano -0.7%, pior mes -5.3%, pior queda -18.1%, 1.0 trades/semana. Pre 2017-18: 1 trade (BTC -1.04R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #148: k-sma100-d-bull50-bracket-s2-tp075 -> PASSA dev (t +3.48; BTC +0.092R/145, ETH +0.132R/139, SOL +0.222R/109; win rate 68%; conf. 4/5);
  carteira K55: +9.3%/ano, pior ano -0.9%, pior mes -6.4%, pior queda -16.3%, 1.3 trades/semana. Pre 2017-18: 1 trade (ETH -1.05R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #149: k-sma100-d-bull50-mom7-bracket-s2 -> PASSA dev (t +3.96; BTC +0.176R/98, ETH +0.243R/103, SOL +0.278R/76; win rate 64%; conf. 5/5);
  carteira K56: +10.6%/ano, pior ano 0.0%, pior mes -4.2%, pior queda -15.8%, 0.9 trades/semana. Pre 2017-18: 0 trades -> REPROVADA no pre (nao da para julgar). Holdout NAO aberto
- [x] #150: k-sma100-d-bull50-red-bracket-s2 -> REPROVADA (SOL 56 < 60; t +3.27; win rate 63%; conf. 3/5);
  carteira K57: +8.1%/ano, pior ano 0.0%, pior mes -4.3%, pior queda -13.2%, 0.75 trades/semana

## Ideias do agente (2026-11-22, cripto sessao :30 01h30; base K54 = #147)
Registadas em IDEAS.md antes de correr.
- [x] #151: k-sma50-d-btc50-bracket-s2 -> PASSA dev (t +4.57; BTC +0.199R/137, ETH +0.194R/149, SOL +0.303R/97; win rate 64%; conf. 5/5);
  carteira K58: +14.3%/ano, pior ano -13.5% (2022), pior mes -5.3%, pior queda -16.8%, 1.2 trades/semana. Pre 2017-18: 50 trades -0.003R, 2018 -9.0% -> REPROVADA no pre. Holdout NAO aberto
- [x] #152: k-sma50-d-bull50-bracket-s2-lose7 -> PASSA dev (t +4.30; BTC +0.106R/150, ETH +0.158R/152, SOL +0.291R/112; win rate 51%; conf. 5/5);
  carteira K59: +12.1%/ano, pior ano -0.7%, pior mes -5.3%, pior queda -17.0%, 1.3 trades/semana. Pre: 1 trade (BTC -1.04R) -> REPROVADA no pre. Holdout NAO aberto
- [x] #153: k-sma50up-d-bull50-bracket-s2 -> PASSA dev (t +3.94; BTC +0.193R/102, ETH +0.178R/114, SOL +0.333R/73; win rate 64%; conf. 5/5);
  carteira K61: +10.7%/ano, pior ano -1.2%, pior mes -4.2%, pior queda -17.7%, 0.9 trades/semana. Pre: 0 trades -> REPROVADA no pre (nao da para julgar). Holdout NAO aberto
- [x] #154: k-sma50-d-bull50-bracket-s2-rx -> PASSA dev (t +4.53; BTC +0.173R/121, ETH +0.206R/128, SOL +0.276R/95; win rate 60%; conf. 5/5);
  carteira K60: +12.3%/ano, pior ano 0.0%, pior mes -4.9%, pior queda -15.0%, 1.1 trades/semana. Pre: 1 trade (BTC -1.04R) -> REPROVADA no pre. Holdout NAO aberto

## Ideias do agente (2026-11-22, cripto sessao :00 02h, base K58 = #151)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --push --num "#1xx" --nota ...` (e `--period pre` se passar).
- [x] #155: k-sma50-d-btc50-bracket-s2-rx -> PASSA dev (t +5.05; BTC +0.193R/154, ETH +0.201R/157, SOL +0.269R/112; win rate 60%; conf. 5/5;
  K64 +15.2%/ano, pior ano -9.4%, pior mes -5.0%). Pre +0.048R/54 trades (>= 0). HOLDOUT (uma vez): -0.007R/114, t -0.09, conf. 1/5: REPROVADA
- [x] #156: k-sma50-d-btc50up-bracket-s2 -> PASSA dev (t +4.60; BTC +0.210R/119, ETH +0.192R/127, SOL +0.350R/88; win rate 65%; conf. 5/5;
  K65 +13.4%/ano, pior ano -5.3%, pior mes -4.3%). Pre -0.114R/41 trades: REPROVADA no pre
- [x] #157: k-sma50-d-btc50-bracket-s15 -> PASSA dev (t +3.77; BTC +0.116R/218, ETH +0.148R/211, SOL +0.209R/154; win rate 61%; conf. 4/5;
  K66 +14.8%/ano, pior ano -11.6%, pior mes -6.5%, 1.9 trades/semana). Pre +0.034R/77 (>= 0). HOLDOUT (uma vez): -0.072R/141, t -0.86, conf. 0/5: REPROVADA
- [x] #158: k-sma20-d-btc50-bracket-s2 -> PASSA dev (t +4.65; BTC +0.209R/137, ETH +0.219R/139, SOL +0.270R/101; win rate 64%; conf. 5/5;
  K67 +14.4%/ano, pior ano -13.6%). Pre -0.100R/53 trades, 2018 -12.2%: REPROVADA no pre

## Ideias do agente (2026-11-23, cripto sessao :00 00h; PRIORIDADE: mercado em baixa, short, perpetuos)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --venue perp --push --num "#1xx" --nota ...`.
- [x] #165: s-sma50-d-bear-bracket-s2-mh3 -> REPROVADA (t -0.88; BTC -0.060R/166, ETH -0.021R/169, SOL +0.018R/133; win rate 47%; conf. 0/5; K79 -1.9%/ano, pior ano -9.3%, so 2022 +10.9%)
- [x] #166: s-sma100-d-bear-bracket-mh10 -> REPROVADA (t -2.08; BTC -0.090R/81, ETH -0.110R/73, SOL -0.077R/61; win rate 44%; conf. 0/5; K80 -3.3%/ano, pior ano -10.1%)
- [x] #167: s-sma600-4h-bear-bracket -> REPROVADA (t -1.15; BTC -0.085R/133, ETH -0.080R/102, SOL -0.015R/93; win rate 49%; conf. 0/5; K81 -1.8%/ano, 2022 +14.5%, 2021 -10.6%)
- [x] #168: s-dc20-d-bear-bracket-s2-mh5 -> REPROVADA (t +0.47; BTC -0.066R/29, ETH -0.035R/32, SOL +0.247R/25 < 60; win rate 44%; conf. 3/5; K82 +0.5%/ano)

## Ideias do agente (2026-11-23, cripto sessao :30 00h30; PRIORIDADE: mercado em baixa, ressaltos em long, perpetuos)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --venue perp --push --num "#1xx" --nota ...`.
- [x] #169: l-rsi2-d-bear-s2-tp05-mh2 -> REPROVADA (t -0.47; BTC +0.048R/76, ETH -0.041R/69, SOL -0.081R/54; win rate 59%; conf. 1/5; K83 -0.6%/ano, pior ano -8.3% (2022), pior mes -6.8%)
- [x] #170: l-low10-d-bear-s2-tp1-mh3 -> REPROVADA (t -1.26; BTC +0.050R/73, ETH -0.073R/74, SOL -0.147R/65; win rate 55%; conf. 2/5; K84 -1.9%/ano, pior ano -14.6% (2022))
- [x] #171: l-rsi2-4h-bear-s2-tp1-mh6 -> REPROVADA (t -3.43; BTC -0.092R/338, ETH -0.097R/350, SOL -0.064R/247; win rate 49%; conf. 1/5; K85 -10.4%/ano, 2022 -41.7%)
- [x] #172: l-low30-4h-bear-s3-tp05-mh12 -> REPROVADA (t -3.35; BTC -0.052R/161, ETH -0.134R/170, SOL -0.111R/130; win rate 55%; conf. 0/5; K86 -5.7%/ano, 2022 -25.5%)

## Ideias do agente (2026-11-23, cripto sessao :00 01h; PRIORIDADE: baixa separada pela inclinacao da media 200 do BTC, perpetuos)
Registadas em IDEAS.md antes de correr. `python crypto_lab.py --ideas <nome> --period dev --venue perp --push --num "#1xx" --nota ...`.
- [x] #173: s-sma50-d-bear200dn-bracket-s2-mh3 -> REPROVADA (t -0.64; BTC -0.063R/88, ETH -0.043R/86, SOL +0.046R/71; win rate 47%; conf. 1/5; K87 -1.0%/ano, pior ano -6.3% (2020))
- [x] #174: s-sma600-4h-bear200dn-bracket -> REPROVADA (t -1.21; BTC -0.095R/80, ETH -0.176R/56, SOL +0.007R/60; win rate 47%; conf. 1/5; K88 -1.4%/ano, pior ano -7.5% (2020))
- [x] #175: l-rsi2-4h-bear200up-s2-tp1-mh6 -> REPROVADA (t -2.20; BTC -0.078R/128, ETH -0.137R/138, SOL -0.043R/107; win rate 48%; conf. 1/5; K89 -6.3%/ano, pior ano -15.2% (2023))
- [x] #176: l-low30-4h-bear200up-s3-tp05-mh12 -> REPROVADA (t -1.99; BTC -0.015R/67, ETH -0.175R/74, SOL -0.058R/53; win rate 55%; conf. 0/5; K90 -2.6%/ano, pior ano -8.3% (2022))

## Ideias do agente (2026-11-23, sessao 01h30): vender ressaltos em baixa (perp)
- [x] #177 s-rsi2hi-d-bear-s2-tp1-mh3 -> REPROVADA (t -3.08, win 43%, K91)
- [x] #178 s-rsi2hi-4h-bear-s2-tp1-mh6 -> REPROVADA (t -2.64, win 49%, K92)
- [x] #179 s-rsi2hi-4h-bear-s3-tp05-mh12 -> REPROVADA (t -3.85, win 55%, K93)
- [x] #180 s-rsi2hi-4h-bear-ema200-s2-tp1-mh6 -> REPROVADA (t +0.33, win 54%, K94; positiva nas 3 moedas mas ~0R)

## Ideias do agente (2026-11-23, sessao 02h): regime da propria moeda (EMA 200 de 4h) em baixa (perp)
- [x] #181 s-rsi2hi-4h-ema200-s2-tp1-mh6 -> REPROVADA (t -0.28; BTC -0.018R/261, ETH -0.030R/281, SOL +0.036R/199; win 52%; conf. 2/5; K95 +1.9%/ano, pior ano -1.6%, pior mes -7.2%)
- [x] #182 s-rsi2hi-4h-bear-ema600-s2-tp1-mh6 -> REPROVADA (t -0.75; BTC -0.033R/251, ETH -0.001R/242, SOL -0.039R/161; win 52%; conf. 0/5; K96 +0.5%/ano, pior ano -4.8%)
- [x] #183 l-rsi2-4h-bear-ema200-s2-tp1-mh6 -> REPROVADA (t -1.85; BTC -0.160R/63, ETH +0.002R/62, SOL -0.207R/35; win 49%; conf. 2/5; K97 -1.6%/ano, pior ano -8.0%)
- [x] #184 s-dc20-4h-bear-ema200-s2-tp1-mh6 -> REPROVADA (t -0.02; BTC +0.021R/137, ETH -0.016R/147, SOL -0.007R/119; win 47%; conf. 3/5; K98 +0.5%/ano, pior ano -5.6%)

## Ideias do agente (2026-11-23, sessao 19h): vender o ressalto FALHADO / rejeicao na media descendente em baixa (perp)
- [x] #185 s-failrally-d-bear-s2-tp1-mh3 -> REPROVADA (t +0.61; BTC +0.090R/26, ETH -0.007R/18, SOL +0.039R/18; win 53%; conf. 2/5; K99 +0.5%/ano, pior ano -1.3%; poucas trades)
- [x] #186 s-failrally-4h-bear-s2-tp1-mh6 -> REPROVADA (t -1.35; BTC -0.117R/228, ETH +0.028R/243, SOL -0.027R/167; win 46%; conf. 0/5; K100 -4.3%/ano, pior ano -14.0%)
- [x] #187 s-ema20rej-d-bear-s2-tp1-mh3 -> REPROVADA (t -1.64; BTC -0.071R/59, ETH -0.046R/49, SOL -0.137R/40; win 45%; conf. 0/5; K101 -2.0%/ano, pior ano -5.2%)
- [x] #188 s-ema20rej-4h-bear-s2-tp1-mh6 -> REPROVADA (t -1.39; BTC -0.030R/226, ETH -0.050R/224, SOL -0.044R/161; win 48%; conf. 0/5; K102 -0.3%/ano, pior ano -9.9%, pior mes -11.3%)

## Ideias do agente (2026-11-23, sessao 19h30): comprar os ressaltos DEPOIS de comecarem (rutura em long com BTC em baixa, perp)
- [x] #189 l-dc20-4h-bear-s2-tp1-mh6 -> REPROVADA (t +0.85; BTC +0.028R/172, ETH +0.032R/166, SOL +0.036R/98; win 50%; conf. 3/5; K103 -0.4%/ano, pior ano -13.4% (2022))
- [x] #190 l-dc20-d-bear-s2-tp1-mh5 -> REPROVADA (t +1.78; BTC +0.069R/32, ETH +0.271R/29, SOL +0.141R/15 < 60; win 58%; conf. 5/5; K104 +2.0%/ano, pior ano -4.2%)
- [x] #191 l-dc20-4h-bear-s2-tp2-mh12 -> REPROVADA (t +2.45 < 3; BTC +0.109R/136, ETH +0.179R/129, SOL +0.182R/75; win 50%; conf. 5/5; K105 +8.1%/ano, pior ano -1.4%, pior mes -6.9%) -> a melhor ideia de baixa ate agora
- [x] #192 l-dc24-1h-bear-s3-tp2-mh24 -> REPROVADA (t +1.33; BTC +0.077R/258, ETH +0.082R/254, SOL -0.014R/169; win 46%; conf. 5/5; K106 +3.2%/ano, pior ano -11.4%)

## Ideias do agente (2026-11-23, sessao 20h): variantes da #191 (rutura 4h em long com BTC em baixa, alvo 2R, perp)
- [x] #193 l-dc20-4h-bear-s2-tp2-mh30 -> REPROVADA (t +2.84; BTC +0.174R/122, ETH +0.318R/110, SOL +0.145R/70; win 46%; conf. 4/5; K107 +8.2%/ano, pior ano -14.0% (2022))
- [x] #194 l-dc10-4h-bear-s2-tp2-mh12 -> REPROVADA (t +1.47; BTC +0.097R/195, ETH +0.057R/185, SOL +0.057R/116; win 48%; conf. 5/5; K108 +4.5%/ano, pior ano -21.4% (2022))
- [x] #195 l-dc20-4h-bear-s15-tp2-mh12 -> REPROVADA (t +2.74; BTC +0.174R/145, ETH +0.178R/140, SOL +0.199R/82; win 49%; conf. 4/5; K109 +9.3%/ano, pior ano -3.2%, pior mes -6.8%)
- [x] #196 l-dc20-4h-bear-s3-tp2-mh12 -> REPROVADA (t +1.67; BTC +0.120R/123, ETH +0.072R/117, SOL +0.037R/73; win 50%; conf. 5/5; K110 +3.5%/ano, pior ano -10.0%)

## Ideias do agente (2026-11-23, sessao 20h30): filtrar ruturas falsas da #191 (volume, BTC) e 2.a estrategia na carteira (perp)
- [x] #197 l-dc20-4h-bear-vol15-s2-tp2-mh12 -> REPROVADA so por SOL 54 < 60 trades (t +3.34; BTC +0.206R/109, ETH +0.255R/96, SOL +0.297R/54; win 53%; conf. 5/5; K111 +8.2%/ano, pior ano +0.5%, pior mes -5.6%)
- [x] #198 l-dc20-4h-bear-btcbo-s2-tp2-mh12 -> REPROVADA (t +2.16; BTC +0.109R/136, ETH +0.217R/96, SOL +0.126R/53; win 48%; conf. 4/5; K114 +6.9%/ano, pior ano -2.9%)
- [x] #199 s-dc20-4h-bear-s2-tp2-mh12 -> REPROVADA (t -0.16; BTC -0.085R/114, ETH -0.064R/126, SOL +0.157R/93; win 44%; conf. 4/5; K112 -0.2%/ano, pior ano -18% (2021)); carteira #191+#199 K115 +6.0%/ano, pior ano -17.9%
- [x] #200 l-dc20-4h-bear-retest-s2-tp2-mh12 -> REPROVADA (t +1.71; BTC +0.148R/82, ETH +0.222R/93, SOL -0.092R/58; win 50%; conf. 3/5; K113 +3.6%/ano, pior ano -10.3%); carteira #191+#200 K116 +7.2%/ano, pior ano -1.1%, 53 trades/ano

## Ideias do agente (2026-11-27, sessao 02h): o filtro de volume da #197 noutros horizontes (perp; scalping, day trade, swing)
- [x] #201 l-dc96-15m-bear-vol15-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -1.62; BTC -0.067R/541, ETH +0.003R/529, SOL -0.091R/381; win 41%; conf. 1/5; K120 -16%/ano, pior ano -89.6%)
- [x] #202 l-dc24-1h-bear-vol15-s3-tp2-mh24 (day trade 1h) -> REPROVADA (t +1.99; BTC +0.113R/231, ETH +0.087R/232, SOL +0.061R/142; win 47%; conf. 4/5; K117 +6.0%/ano, pior ano -9.4%); quase passa -> SPECS
- [x] #203 s-dc20-4h-bear-vol15-s2-tp2-mh12 (swing 4h short) -> REPROVADA (t +0.43; BTC -0.013R/85, ETH +0.015R/100, SOL +0.104R/71; win 45%; conf. 4/5; K118 +1.4%/ano, pior ano -9.5%); #197+#203 K121 +8.4%/ano, pior ano -4.2%
- [x] #204 l-dc20-4h-bear-vol15-s2-tp1-mh6 (day trade 4h) -> REPROVADA (t +1.86; BTC +0.077R/130, ETH +0.094R/116, SOL +0.069R/73; win 54%; conf. 5/5; K119 +2.3%/ano, pior ano -1.2%); quase passa -> SPECS

## Ideias do agente (2026-11-27, sessao 02h30): capitulacao com volume (selling climax) em baixa, 3 estilos + upthrust em short (perp)
- [x] #205 l-climax96-15m-bear-vol15-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -5.06; BTC -0.106R/555, ETH -0.124R/546, SOL -0.157R/390; win 45%; conf. 0/5; K122 -22.1%/ano, pior ano -83.1%)
- [x] #206 l-climax24-1h-bear-vol15-s3-tp2-mh24 (day trade 1h) -> REPROVADA (t -2.93; BTC -0.032R/289, ETH -0.137R/275, SOL -0.167R/200; win 42%; conf. 0/5; K123 -7.7%/ano, pior ano -31.0%)
- [x] #207 l-climax20-4h-bear-vol15-s2-tp2-mh12 (swing 4h) -> REPROVADA (t +0.09; BTC +0.174R/76, ETH -0.064R/78, SOL -0.114R/60; win 48%; conf. 0/5; K124 +0.4%/ano, pior ano -6.3%)
- [x] #208 s-upthrust20-4h-bear-vol15-s2-tp2-mh12 (swing 4h short) -> REPROVADA (t -0.91; BTC -0.025R/66, ETH -0.121R/71, SOL -0.041R/34; win 40%; conf. 1/5; K125 -1.7%/ano, pior ano -8.2%)

## Ideias do agente (2026-11-27, sessao 03h): recuo RSI(2) < 10 dentro do contexto da #197 (4h) / #202 (1h), 3 estilos (perp)
- [x] #209 l-pb15m-ctx197-rsi2-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -1.84; BTC -0.147R/329, ETH -0.028R/293, SOL +0.031R/184; win 47%; conf. 3/5; K128 +2.5%/ano, pior ano -10.8%)
- [x] #210 l-pb1h-ctx197-rsi2-s3-tp2-mh24 (day trade 1h) -> REPROVADA (t -1.36; BTC -0.078R/94, ETH -0.112R/79, SOL -0.017R/51; win 43%; conf. 4/5; K127 -1.9%/ano, pior ano -12.7%)
- [x] #211 l-pb4h-ctx197-rsi2-s2-tp2-mh12 (swing 4h) -> REPROVADA (t +0.40; BTC -0.048R/21, ETH +0.118R/23, SOL +0.088R/14; win 48%; conf. 4/5; K126 +0.3%/ano, pior ano -3.8%)
- [x] #212 l-pb15m-ctx202-rsi2-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -1.43; BTC -0.038R/358, ETH -0.097R/405, SOL +0.030R/263; win 46%; conf. 2/5; K129 +0.6%/ano, pior ano -10.3%)

## Ideias do agente (2026-11-27, sessao 03h30, noite intensiva): rutura de volatilidade de Williams em baixa (perp)
- [x] #213 l-vbo05-1h-bear-s3-tp2-mh24 (day trade 1h) -> REPROVADA (t +1.60; BTC +0.093R/238, ETH +0.078R/246, SOL +0.024R/182; win 45%; conf. 3/5; K130 +7.1%/ano, pior ano -3.2%, pior mes -14.6%)
- [x] #214 s-vbo05-1h-bear-s3-tp2-mh24 (day trade short 1h) -> REPROVADA (t +0.47; BTC +0.041R/239, ETH +0.043R/248, SOL -0.036R/195; win 44%; conf. 3/5; K131 +2.7%/ano, pior ano -7.9%)
- [x] #215 l-vbo05-15m-bear-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -0.29; BTC -0.011R/285, ETH +0.026R/299, SOL -0.061R/228; win 43%; conf. 1/5; K133 -3.0%/ano, pior ano -52.1%)
- [x] #216 l-wvbo05-4h-bear-s2-tp2-mh12 (swing semanal 4h) -> REPROVADA (t +1.85; BTC +0.207R/50, ETH +0.203R/42, SOL +0.130R/33; win 54%; conf. 3/5; K132 +4.0%/ano, pior ano -5.1%, pior mes -3.5%)

## Ideias do agente (2026-11-27, sessao 04h, noite intensiva): vizinhas e contexto da #197 em baixa (perp)
- [x] #217 l-dc20-4h-bear-vol15-s2-tp2-mh24 (swing 4h, 4 dias) -> REPROVADA (t +3.27; BTC +0.246R/101, ETH +0.340R/91, SOL +0.232R/54 < 60; win 50%; conf. 4/5; K134 +8.5%/ano, pior ano -3.1%, pior mes -4.6%)
- [x] #218 l-dc10-4h-bear-vol15-s2-tp2-mh12 (swing 4h, canal 10) -> REPROVADA (t +2.43; BTC +0.186R/143, ETH +0.114R/139, SOL +0.132R/81; win 50%; conf. 5/5; K135 +6.0%/ano, pior ano -3.4%, pior mes -8.0%)
- [x] #219 l-dc96-15m-ctx197-vol15-s3-tp2-mh32 (scalping 15m) -> REPROVADA (t -0.50; BTC +0.046R/103, ETH -0.034R/107, SOL -0.156R/67; win 40%; conf. 1/5; K137 -1.3%/ano, pior ano -12.9%)
- [x] #220 l-dc24-1h-ctx197-vol15-s3-tp2-mh24 (day trade 1h) -> REPROVADA (t +0.52; BTC +0.204R/58, ETH -0.010R/62, SOL -0.111R/35; win 41%; conf. 2/5; K136 +0.2%/ano, pior ano -9.7%)

## Ideias do agente (2026-11-27, sessao 19h): carteira de 8 moedas das vizinhas da #197 (perp)
- [x] #225 diario da demo s-rsi2-15m-long~lo3 (scalping) -> REJEITADA pelo journal_lab (-0.119 -> -0.113R/trade, nao sobe 0.02R)
- [x] #226 carteira-8 #204 l-dc20-4h-bear-vol15-s2-tp1-mh6 (day trade 4h, 8 moedas, max 4 abertas) -> REPROVADA no criterio (t 8 moedas +2.79; positiva nas 8; win 54%; K144 +10.8%/ano, TODOS os anos positivos (pior +6.7%), pior mes -8.5%, ~1.8/semana) -> SPECS
- [x] #227 carteira-8 #218 l-dc10-4h-bear-vol15-s2-tp2-mh12 (swing 4h, 8 moedas, max 4 abertas) -> REPROVADA (t 8 moedas +2.99; positiva nas 8; win 46%; K143 +9.8%/ano, pior ano -5.7%, pior mes -9.9%, ~2/semana) -> SPECS

## Ideias do agente (2026-11-27, sessao 20h): pior mes das carteiras de 8 moedas (max 2 abertas) + #224 em 8 moedas (perp)
- [x] #228 carteira-8 #226 l-dc20-4h-bear-vol15-s2-tp1-mh6 (day trade 4h, 8 moedas, max 2 abertas) -> REPROVADA (positiva nas 8; win 53%; K145 +4.8%/ano (antes +10.8%), pior ano +3.3%, pior mes -5.2% (antes -8.5%), 64 trades/ano)
- [x] #229 carteira-8 #224 l-dc24-1h-bear-vol20-s3-tp2-mh24 (day trade 1h, 8 moedas, max 4 abertas) -> REPROVADA no criterio (t 3 moedas 2.46; t 8 moedas +3.76, positiva nas 8; win 46%; K146 +9.8%/ano, pior ano -11.9%, pior mes -14.2%, 144 trades/ano) -> SPECS; demo_pick pos na #D3
- [x] #230 carteira-8 #221 l-dc20-4h-bear-vol15-s2-tp2-mh12 (swing 4h, 8 moedas, max 2 abertas) -> REPROVADA no criterio (SOL 54 < 60; positiva nas 8; win 50%; K147 +10.4%/ano (antes +14.3%), pior ano -0.1%, pior mes -3.4% (antes -6.5%), 51 trades/ano) -> SPECS

## Ideias do agente (2026-11-27, sessao 21h): pior mes/ano da #229 + carteira swing+day trade (8 moedas, perp)
- [x] #231 carteira-8 #229 l-dc24-1h-bear-vol20-s3-tp2-mh24 (day trade 1h, 8 moedas, max 2 abertas) -> REPROVADA no criterio (t 3 moedas 2.46; t 8 moedas +3.76, positiva nas 8; win 46%; K148 +8.7%/ano, pior ano +1.5% (antes -11.9%), pior mes -5.6% (antes -14.2%), 91 trades/ano) -> SPECS
- [x] #232 carteira-8 #230 + #229 (swing 4h + day trade 1h, 8 moedas, max 3 abertas) -> REPROVADA (win 45%; K149 +8.7%/ano, pior ano -9.3%, pior mes -9.5%, 124 trades/ano; pior que a #230 sozinha)
- [x] #233 carteira-8 l-dc24-1h-bear-vol20-s3-tp1-mh24 (#229 com alvo 1R, day trade 1h, 8 moedas, max 4) -> REPROVADA (t 8 moedas +2.82; win 54%; +0.062R/trade; K150 +8.0%/ano, pior ano -12.0%, pior mes -12.2%, 195 trades/ano)
