# CRIPTO (foco atual desde 2026-11-18; Kraken spot, so long, custos 0.57% ida e volta, 1% de risco por trade)

| # | data | variante | t dev | win rate | R/trade | carteira dev (%/ano, pior ano) | veredicto |
|---|---|---|---|---|---|---|---|
| K1 | 2026-11-18 | k-donchian20-d + k-sma100-d + k-donchian55-4h + k-sma200-4h | - | 21% | - | +52%, -21.0% | holdout 2025 -10.9%: nao robusta |
| #100 | 2026-11-19 | k-sma200-4h-persist (6 fechos de 4h seguidos acima/abaixo da media 200) | +3.06 | 28% | +2.04 | +70%, -20.8% | **PASSA dev + pre**; holdout BTC/ETH/SOL +0.79R mas confirmacao 1/5: misto |
| #101 | 2026-11-19 | k-dc55-4h-btcbull (rutura 55 velas so com BTC > media 200 dias) | +3.02 | 34% | +0.77 | +26.6% (corrigido: 2022 = 0%), sem ano negativo | REPROVADA (SOL 53 trades < 60) |
| #102 | 2026-11-19 | k-dc55-4h-wide (rutura 55 velas, stop 6 ATR) | +3.44 | 42% | +0.44 | +17%, -4.9% | REPROVADA (SOL 59 trades < 60) |
| #103 | 2026-11-19 | k-dip-hold-4h (minimo de 5 dias em tendencia, segura 7 dias) | +0.77 | 49% | +0.04 | +1.6%, -4.0% | REPROVADA |
| #104 | 2026-11-19 | k-dc55-4h-bw-tp1 (#101 + stop 6 ATR + alvo 1R) | +3.05 | 47% | +0.14 | +2.2%, -0.5% | PASSA dev; pre negativo (1 trade): REPROVADA no pre |
| #105 | 2026-11-19 | k-persist-bw (#100 + regime BTC + stop 6 ATR) | +2.74 | 38% | +1.70 | +31.7%, -6.5% | REPROVADA (31-42 trades por moeda) |
| #106 | 2026-11-19 | k-persist-bw-tp1 (#105 + alvo 1R) | +4.64 | 54% | +0.22 | +3.5%, -2.3% | PASSA dev; pre negativo (2 trades): REPROVADA no pre |
| #107 | 2026-11-19 | k-dc20-d-bull-tp1 (rutura 20 dias + regime BTC + alvo 1R) | +4.43 | 60% | +0.28 | +8.6%, 0.0% | REPROVADA (SOL 57 trades < 60) |
| #108 | 2026-11-19 | k-persist-bw-half (#105 + metade em 1R, resto em breakeven) | +2.59 | 42% | +0.74 | +13.6%, -6.0% | REPROVADA (SOL 32 trades < 60) |
| #109 | 2026-11-19 | k-dc20-4h-bw-tp1 (#107 em 4h, stop 6 ATR, alvo 1R) | +2.67 | 41% | +0.08 | +3.2%, 0.0% | REPROVADA |
| #110 | 2026-11-19 | k-dc20-4h-bw-half (#109 com saida parcial) | +2.54 | 36% | +0.13 | +6.8%, 0.0% | REPROVADA |
| #111 | 2026-11-19 | k-dc20-4h-bw-be (#109 sem alvo, stop para breakeven em +1R) | +2.96 | 35% | +0.23 | +11.9%, 0.0% | REPROVADA por pouco (t < 3.0) |
| #112 | 2026-11-19 | k-dc20-d-own-tp1 (#107 com regime da propria moeda) | +4.13 | 60% | +0.28 | +7.4%, -2.1% | REPROVADA (BTC 55, SOL 44 trades) |
| #113 | 2026-11-19 | k-sma100-d-bull-tp1 (acima da media 100 dias + regime BTC, alvo 1R repetido) | +4.78 | 53% | +0.24 | +10.0%, 0.0% | **PASSA dev** (conf. 4/5); pre 1 trade -0.26R: REPROVADA no pre |
| #114 | 2026-11-19 | k-pb-d-bull-tp1 (recuo de 5 dias na tendencia, alvo 1R) | +1.82 | 66% | +0.12 | +3.0%, -3.2% | REPROVADA |
| #115 | 2026-11-19 | k-dc20-d-own-be (#112 sem alvo, breakeven em +1R) | +1.93 | 50% | +1.74 | +19.7%, -7.3% | REPROVADA (20-25 trades por moeda) |
| #116 | 2026-11-19 | k-sma100-d-b100-tp1 (#113 com regime BTC > media 100 dias) | +4.63 | 53% | +0.23 | +10.0%, -4.9% | PASSA dev + pre (~0); holdout +0.04R, win rate 46%: REPROVADA |
| #117 | 2026-11-19 | k-sma600-4h-bull-tp1 (#113 em 4h) | +3.78 | 40% | +0.14 | +4.4%, 0.0% | PASSA dev; pre 1 trade -0.66R: REPROVADA no pre |
| #118 | 2026-11-19 | k-sma100-d-bull-bracket (#113 sem saida pelo sinal: so alvo 1R ou stop) | +4.87 | **68%** | +0.33 | +10.3%, -2.0% | REPROVADA (SOL 54 trades < 60); confirmacao 5/5 |
| #119 | 2026-11-19 | k-sma100-d-slope-tp1 (#113 so com media 100 a subir) | +4.10 | 53% | +0.23 | +8.1%, 0.0% | REPROVADA (SOL 58 trades < 60) |
| #120-#127 | 2026-11-21 | SCALPING 5m/15m long e short (Bollinger 5m, 1.a hora de NY, RSI(2) 15m, explosao 15m); K22-K29 | -50 a -8 | 15-35% | -0.4 a -1.8 | -300% a -770%/ano | REPROVADAS: os custos (0.57%) valem 0.3-1.4R por trade |
| K1 short | 2026-11-21 | as 4 da K1 ao espelho (so shorts); K30 | -1.9 a -0.7 | 22% | -0.07 a -0.15 | -4.6%, -17.9% (so 2022 positivo) | REPROVADA |
| #128 | 2026-11-21 | shorts da K1 so com BTC < media 200 dias; K31 | -0.9 a 0.0 | 27% | -0.06 | -0.8%, -15.5% | REPROVADA |
| #129-#132 | 2026-11-21 | INTRADAY 1h, max 24h, so long, regime BTC (RSI(2) 1h, minimo 12h + alvo 1R, rutura maximo 24h, squeeze); K32-K35 | -16.6 a -2.8 | 35-47% | -0.09 a -0.32 | -6% a -42%/ano | REPROVADAS; #131 rutura 24h tem +0.13R antes de custos (t ~2.7 nas 3 moedas) e ficaria +0.08 a +0.11R com custos de futuros |
| #133-#137 | 2026-11-21 | PERPETUOS Kraken (0.14% ida e volta + funding): rutura 24h long, quebra 24h short (baixa), RSI(2) 1h long/short, ORB NY; K36-K40 | -5.5 a +2.2 | 38-67% | -0.13 a +0.06 | -69% a +3.6%/ano | REPROVADAS; #133 rutura 24h long e a melhor: positiva nas 3 moedas e 4/5 confirmacao, mas t 2.16 < 3 e pior ano -14% |
| #139 | 2026-11-22 | k-sma100-d-bull-bracket-mh10 (#118 com tempo maximo 10 dias); K42 | +4.12 | 57% | +0.15 | +9.1%, -1.5% (pior queda -11%) | PASSA dev; pre 1 trade -1R: REPROVADA no pre |
| #140 | 2026-11-22 | k-sma100-d-own-bracket (#118 sem filtro do BTC); K43 | +4.31 | 65% | +0.28 | +9.7%, -13.5% (2022) | REPROVADA (SOL 56 < 60) |
| #141 | 2026-11-22 | k-sma100-d-bull-bracket-s2 (#118 com stop 2 ATR); K44 | +3.47 | 62% | +0.19 | +10.2%, -2.1% (pior mes -5.3%, queda -18%) | PASSA dev; pre 1 trade -1R: REPROVADA no pre |
| #142 | 2026-11-22 | carteira #118 + #107 (rutura 20 dias); K45 | - | 64% | - | +9.8%, -2.0% | as duas falham SOL < 60; quase nao acrescenta trades |
| #138 | 2026-11-21 | k-sma600-4h-bull-bracket (#118 em 4h, stop 3 ATR de 4h, so alvo 1R ou stop); K41 | +2.47 | 59% | +0.09 | +5.5%, -2.1% (pior mes -9.3%) | REPROVADA (t < 3); 2x mais trades que a #118 mas o custo come metade do ganho |
| #143 | 2026-11-22 | k-sma100-d-bull-bracket-s2-mh10 (#141 + tempo maximo 10 dias); K46 | +3.20 | 57% | +0.12 | +9.8%, -2.9% (pior mes -6.4%, queda -21%) | PASSA dev (conf. 4/5); pre 1 trade -1R: REPROVADA no pre |
| #144 | 2026-11-22 | k-sma50-d-bull-bracket-s2 (#141 com a moeda acima da media 50); K47 | +3.69 | 63% | +0.20 | +10.6%, -0.7% (pior mes -5.3%, queda -19%) | PASSA dev (conf. 5/5); pre 1 trade -1R: REPROVADA no pre |
| #145 | 2026-11-22 | k-ema100-d-bull-bracket-s2 (#141 com EMA 100 / EMA 200 BTC); K48 | +3.37 | 61% | +0.17 | +10.4%, -4.3% (2022) | PASSA dev (conf. 4/5); pre 47 trades -0.06R, 2018 -7.5%: REPROVADA no pre |
| #146 | 2026-11-22 | k-sma100-d-bull50-bracket-s2 (#141 + BTC tambem acima da media 50); K49 | +3.88 | 63% | +0.21 | +10.9%, 0.0% (pior mes -5.3%, queda -17%) | PASSA dev (conf. 5/5); pre 1 trade -1R: REPROVADA no pre |
| #147 | 2026-11-22 | k-sma50-d-bull50-bracket-s2 (#146 com a moeda acima da media 50); K54 | +4.10 | 64% | +0.23 | +11.4%, -0.7% (pior mes -5.3%, queda -18%) | PASSA dev (conf. 5/5); pre 1 trade -1R: REPROVADA no pre. Nova base (pontuacao 86) |
| #151 | 2026-11-22 | k-sma50-d-btc50-bracket-s2 (#147 com BTC so acima da media 50); K58 | +4.57 | 64% | +0.22 | +14.3%, -13.5% (2022) | PASSA dev (conf. 5/5); pre 50 trades -0.00R, 2018 -9%: REPROVADA no pre. Pontuacao 90 (nova base), mas falha o pior ano |
| #152 | 2026-11-22 | k-sma50-d-bull50-bracket-s2-lose7 (#147, sai ao 7.o dia se a perder); K59 | +4.30 | 51% | +0.18 | +12.1%, -0.7% | PASSA dev (conf. 5/5); pre 1 trade -1R: REPROVADA no pre |
| #153 | 2026-11-22 | k-sma50up-d-bull50-bracket-s2 (#147 com a media 50 a subir); K61 | +3.94 | 64% | +0.22 | +10.7%, -1.2% | PASSA dev (conf. 5/5); pre 0 trades: REPROVADA no pre |
| #154 | 2026-11-22 | k-sma50-d-bull50-bracket-s2-rx (#147, sai quando o regime do BTC desliga); K60 | +4.53 | 60% | +0.21 | +12.3%, 0.0% (pior mes -4.9%, queda -15%) | PASSA dev (conf. 5/5); pre 1 trade -1R: REPROVADA no pre. Melhor carteira no objetivo (sem ano negativo, pior mes > -5%) |
| #148 | 2026-11-22 | k-sma100-d-bull50-bracket-s2-tp075 (#146 com alvo 0.75R); K55 | +3.48 | 68% | +0.14 | +9.3%, -0.9% (pior mes -6.4%, queda -16%) | PASSA dev (conf. 4/5); pre 1 trade -1R: REPROVADA no pre |
| #149 | 2026-11-22 | k-sma100-d-bull50-mom7-bracket-s2 (#146 + moeda acima do fecho de 7 dias antes); K56 | +3.96 | 64% | +0.23 | +10.6%, 0.0% (pior mes -4.2%, queda -16%) | PASSA dev (conf. 5/5); pre 0 trades: REPROVADA no pre |
| #150 | 2026-11-22 | k-sma100-d-bull50-red-bracket-s2 (#146 so depois de um dia vermelho); K57 | +3.27 | 63% | +0.21 | +8.1%, 0.0% (pior mes -4.3%) | REPROVADA (SOL 56 < 60) |

Scalping (2026-11-21): ANTES de custos ha uma vantagem pequena (RSI(2) 15m long: win rate 69%, +0.05R; Bollinger 5m BTC +0.08R),
mas o stop de um scalp e 0.4-1.7% do preco e os custos da Kraken (0.57% ida e volta) valem 0.3-1.4R por trade. Nem com custos de maker
(0.32%) passa. So com custos de futuros com ordens limit (~0.04% ida e volta) ficam perto de zero (+0.035R no ORB long). Conclusao:
scalping em spot e impossivel com estes custos; shorts da K1 perdem (so ganham em 2022). Ideias cripto testadas no total: 42.
Intraday 1h (#129-#132, 2026-11-21): 3-5 trades por semana como o Antonio quer, mas os custos de spot (0.2-0.3R por trade) apagam
a vantagem. A unica com vantagem clara antes de custos e a rutura do maximo de 24h (#131). Total de ideias cripto: 46.
Perpetuos (#133-#137): mesmo com custos 4x mais baixos nada passa. Os shorts intraday tambem perdem. Total de ideias cripto: 51.

#138 (2026-11-21, 19h): a #118 em 4h abre 2x mais trades (1.2/semana, SOL 173) com win rate 59%, mas so +0.09R/trade: t 2.47, REPROVADA.

Leitura honesta cripto (2026-11-22, sessao das :30 01h30):
1. Ideias cripto testadas no total: 68 (#100-#154, K1, scalping, intraday, perpetuos). Mais testes = mais desconfianca num resultado isolado.
2. Melhor win rate com resultado positivo: 68% (#118 +0.33R, reprovada SOL < 60; #148 +0.14R, passa o dev). Na familia atual: 64% (#147/#151/#153).
3. #154 (sair de tudo quando o BTC perde o regime) e a 1.a que cumpre pior ano (0.0%) E pior mes (-4.9%) com +12.3%/ano e queda -15%; win rate 60%.
4. #151 (BTC so acima da media 50) tem a maior pontuacao (90, nova base pelo best.py): +14.3%/ano e 1.2 trades/semana, mas 2022 -13.5%
   e pre 2018 -9%: sem a media 200 do BTC os anos de baixa voltam. Pontuacao alta NAO e aprovacao.
5. #152 (sair ao 7.o dia a perder) abre +30% de trades mas o win rate cai para 51%. #153 (media 50 a subir) nao resolve 2024.
6. Pre: as variantes com a media 200 do BTC continuam com 0-1 trades em 2017-18; a #151 mostra que, quando ha trades no pre, o resultado e ~0R.
7. Painel: K58-K61 (dev) e K62-K63 (pre) gravadas; as corridas em paralelo voltaram a sobrepor K59/K63 (corrigido com --label no dev).
8. Proximo passo: base K58 (#151) com a saida da #154 (sair quando o BTC perde a media 50) e com o filtro BTC > media 200 so para entrar em
   2022 -> juntar o %/ano da #151 ao pior ano da #154. Ninguem passou o pre: holdout fechado.

# Resumo indices (ARQUIVO, custos CFD incluidos)

Catalogo: cada teste tem um numero fixo. Estrategias #1, #2, ...; carteiras C1, C2, ... Os numeros nunca mudam; testes novos recebem o numero seguinte.

## Estrategias (#)

| # | data | variante | t dev 2019-24 | t 2012-18 | veredicto |
|---|---|---|---|---|---|
| #1 | 2026-11-16 | `bounce-pdhl-tp2-sl0.5-rth` | -11.29 | - | REPROVADA |
| #2 | 2026-11-16 | `bounce-pwhl-tp2-sl0.5-rth` | -6.90 | - | REPROVADA |
| #3 | 2026-11-16 | `bounce-swing1h-tp2-sl0.5-rth` | -15.79 | - | REPROVADA |
| #4 | 2026-11-16 | `bounce-round-tp2-sl0.5-rth` | -10.02 | - | REPROVADA |
| #5 | 2026-11-16 | `break-pdhl-tp2-sl0.5-rth` | -4.55 | - | REPROVADA |
| #6 | 2026-11-16 | `break-pwhl-tp2-sl0.5-rth` | +1.34 | - | REPROVADA |
| #7 | 2026-11-16 | `break-swing1h-tp2-sl0.5-rth` | -5.49 | - | REPROVADA |
| #8 | 2026-11-16 | `break-round-tp2-sl0.5-rth` | -3.65 | - | REPROVADA |
| #9 | 2026-11-16 | `fake-pdhl-tp2-sl0.5-fk0.3-rth` | -6.86 | - | REPROVADA |
| #10 | 2026-11-16 | `fake-pwhl-tp2-sl0.5-fk0.3-rth` | -1.12 | - | REPROVADA |
| #11 | 2026-11-16 | `fake-swing1h-tp2-sl0.5-fk0.3-rth` | -7.62 | - | REPROVADA |
| #12 | 2026-11-16 | `fake-round-tp2-sl0.5-fk0.3-rth` | -4.19 | - | REPROVADA |
| #13 | 2026-11-16 | `gapfill-pdc-tp2-sl0.5-rth` | -1.34 | - | REPROVADA |
| #14 | 2026-11-16 | `fake-onhl-tp2-sl0.5-fk0.3-rth` | -4.62 | - | REPROVADA |
| #15 | 2026-11-16 | `break-nr4-tp2-sl0.5-rth` | -1.12 | - | REPROVADA |
| #16 | 2026-11-16 | `break-lunchhl-tp2-sl0.5-rth` | -3.41 | - | REPROVADA |
| #17 | 2026-11-16 | `gapgo-pdc-tp2-sl0.5-rth` | +2.34 | - | REPROVADA |
| #18 | 2026-11-16 | `break-monhl-tp2-sl0.5-rth` | +0.15 | - | REPROVADA |
| #19 | 2026-11-16 | `antonio-ifvg1m-tp1` | -17.52 | - | REPROVADA |
| #20 | 2026-11-16 | `antonio-ifvg1m-tp2-be1R` | -12.97 | - | REPROVADA |
| #21 | 2026-11-16 | `antonio-ifvg1m-tp3-be1R` | -10.70 | - | REPROVADA |
| #22 | 2026-11-16 | `trend-sma100-d` | +0.70 | +0.44 | REPROVADA |
| #23 | 2026-11-16 | `rsi2-dip-d` | +0.89 | +2.78 | REPROVADA no oficial (poucas trades) -> **na carteira** |
| #24 | 2026-11-16 | `donchian20-d` | -0.19 | -1.47 | REPROVADA |
| #25 | 2026-11-16 | `rsi2-dip-4h` | +0.01 | -1.50 | REPROVADA |
| #26 | 2026-11-16 | `ibs-dip-d` | +2.20 | +1.30 | REPROVADA no oficial (Dow ~0R) -> **na carteira** |
| #27 | 2026-11-16 | `down3-d` | +0.05 | +3.72 | REPROVADA no oficial (poucas trades) -> **na carteira** |
| #28 | 2026-11-17 | `tom-d` | +1.30 | -0.47 | REPROVADA |
| #29 | 2026-11-17 | `overnight-us-1h` | -1.60 | -5.44 | REPROVADA |
| #30 | 2026-11-17 | `double7-d` | +3.07 | +3.46 | **PASSA** (dev e 2012-18); holdout t +1.51, poucas trades |
| #31 | 2026-11-17 | `opex-week-d` | -0.98 | +3.38 | REPROVADA |
| #32 | 2026-11-17 | `nr7-up-d` | -0.77 | +1.86 | REPROVADA |
| #33 | 2026-11-17 | `week-rev-d` | +1.83 | +2.71 | REPROVADA; positiva nos 3, mas piora a carteira (C4) |
| #34 | 2026-11-17 | `rsi2-pop-short-4h` | -2.46 | -2.09 | REPROVADA |
| #35 | 2026-11-17 | `ibs-bear-d` | +1.62 | +1.02 | REPROVADA no oficial, positiva nos 3 nos 2 periodos -> **na carteira** |
| #36 | 2026-11-18 | `turnaround-tue-d` | +0.21 | +0.92 | REPROVADA |
| #37 | 2026-11-18 | `keyrev-d` | +0.36 | +2.77 | REPROVADA; piora a carteira (C6) |
| #38 | 2026-11-18 | `pullback20-d` | +1.15 | +3.08 | REPROVADA; piora a carteira (C7) |
| #39 | 2026-11-18 | `calmhigh-d` | +0.32 | -0.01 | REPROVADA |
| #40 | 2026-11-18 | `fomc-holiday-1h` (1h: antes do FOMC + vespera de feriado) | +3.81 (fut) / +3.45 (CFD) | +0.85 | **PASSA no dev**; 2012-18 ~0 e holdout t +0.29: provavel sorte do periodo |
| #41 | 2026-11-18 | `flush-1h` (1h: comprar vela de queda violenta a meio da sessao) | +0.15 (fut) | -2.95 | REPROVADA |
| #42 | 2026-11-18 | `ibs-cash-1h` (IBS da sessao cash, compra ao fecho das 16:00, stop de 1h) | +2.80 (fut) / +2.24 (CFD) | +1.86 | REPROVADA no oficial (t < 3); positiva nos 3 nos 2 periodos (fut); NQ +0.16R por trade |
| #43 | 2026-11-18 | `rsi2-cash-1h` (RSI(2) de Connors nos fechos das 16:00, stop de 1h) | +0.92 (fut) / +0.63 (CFD) | +2.98 | REPROVADA (S&P negativo no dev); NQ +0.3R por trade nos 2 periodos |

## Carteiras (C) - 1% por trade, % da conta por ano (2012-2025)

ATENCAO (2026-11-18): C1 a C10 foram calculadas com um ERRO em portfolio.py: uma trade que fechava num dia libertava o lugar
para outra que entrava na abertura desse mesmo dia, e as trades de 1 dia (as que mais ganham) nunca ocupavam lugar. Resultado:
varias trades ao mesmo tempo no mesmo indice e numeros muito inflacionados. C11-C13 sao as versoes corrigidas.

| # | data | carteira | % ao ano | anos >= 14% | pior mes / pior ano / pior queda | trades/semana | veredicto |
|---|---|---|---|---|---|---|---|
| C1 | 2026-11-16 | #23 + #26 + #27 (rsi2-dip-d, ibs-dip-d, down3-d), 10 indices, max 3 abertas | +8.7% | 5/13 | - / - / -21.6% | ~3.4 | substituida por C2 |
| C2 | 2026-11-17 | C1 + 1 trade por regiao + paragem mensal a -3% | +9.5% | 5/14 | -5.1% / -2.5% / -10.7% | - | substituida por C5 |
| C3 | 2026-11-17 | C2 + #30 double7-d | +7.3% | - | - / - / -16.5% | - | piora |
| C4 | 2026-11-17 | C2 + #33 week-rev-d | +5.8% | - | - / - / -13.8% | - | piora |
| C5 | 2026-11-17 | C2 + #35 ibs-bear-d | +12.5% | 6/14 | -5.5% / -4.5% / -9.1% | ~3.5 | inflacionada (erro, ver C11) |
| C6 | 2026-11-18 | C5 + #37 keyrev-d | +11.6% | 4/14 | -4.9% / -0.4% / -12.2% | - | piora |
| C7 | 2026-11-18 | C5 + #38 pullback20-d | +9.6% | 5/14 | -5.8% / -5.0% / -11.4% | ~3.1 | piora |
| C8 | 2026-11-18 | C5 so no NQ (pedido do Antonio) | +3.6% | 0/14 | -1.7% / -0.9% / -3.1% | ~0.7 | muito estavel mas longe dos 14% |
| C9 | 2026-11-18 | C5 no **holdout 2025-26** (uma vez, decisao do Antonio) | 2025 +17.2%, 2026 +34.5% | 2/2 | -3.6% / +17.2% / -7.4% | ~4.4 | **positiva -> segue para demo** (anos de subida: cautela) |
| C10 | 2026-11-18 | C5 sem velas de domingo (como no MT5) - ainda com o erro | +12.6% | 6/14 | -5.3% / -0.4% / -8.6% | ~3.5 | inflacionada (erro) |
| C11 | 2026-11-18 | C5 corrigida (o lugar so fica livre no dia a seguir ao fecho) | +0.9% | 1/14 | -5.5% / -14.7% / -22.0% | ~2.4 | verdade da C5 (CFD) |
| C12 | 2026-11-18 | C11 sem velas de domingo (= o que o bot da demo faria) | +2.2% | 1/14 | -5.5% / -9.2% / -13.6% | ~2.4 | longe dos 14% |
| C13 | 2026-11-18 | C11 so no NQ | +2.1% | 0/14 | -1.9% / -0.9% / -4.0% | ~0.6 | estavel, pequena |
| C14 | 2026-11-18 | C11 com custos de micro-futuros | +1.8% | 1/14 | -5.4% / -13.8% / -20.0% | ~2.4 | base futuros (10 indices) |
| C15 | 2026-11-18 | C14 so NQ (MNQ) | +2.4% | 0/14 | -1.9% / -0.7% / -3.4% | ~0.6 | estavel, pequena |
| C16 | 2026-11-18 | C14 + #30 double7-d (refaz C3) | +2.2% | 1/14 | -6.0% / -9.4% / -19.6% | ~2.3 | pouco melhor, mais instavel |
| C17 | 2026-11-18 | C14 + #33 week-rev-d (refaz C4) | +2.2% | 1/14 | -5.7% / -10.6% / -18.6% | ~2.3 | pouco melhor |
| C18 | 2026-11-18 | C14 + #37 keyrev-d (refaz C6) | +1.9% | 1/14 | -5.5% / -11.4% / -19.2% | ~2.5 | igual |
| C19 | 2026-11-18 | C14 + #38 pullback20-d (refaz C7) | +1.3% | 0/14 | -5.7% / -11.1% / -20.0% | ~2.2 | piora |
| **C20** | 2026-11-18 | **so NQ (MNQ): rsi2-dip-d + ibs-dip-d + down3-d + ibs-bear-d + double7-d, futuros** | **+2.6%** | 0/14 | -1.7% / -1.5% / -3.0% | ~0.6 | **REFERENCIA ATUAL** (stops diarios: 1 MNQ precisa de ~120 mil USD para 1%) |
| C21 | 2026-11-18 | C20 + #40 fomc-holiday-1h (so NQ, futuros) | +5.6% | 1/14 | -3.9% / -0.4% / -6.4% | ~0.8 | mais %/ano mas 2012 (+16%) e quase so o #40 com sorte; 2013-25 ~+4.8%. Nao virou referencia: decide o Antonio |
| C22 | 2026-11-18 | C20 com #42 ibs-cash-1h no lugar do ibs-dip-d (so NQ, futuros) | +5.8% | 4/14 | -4.5% / -5.7% / -12.8% | ~0.8 | mais %/ano e 4 anos >= 14%, mas muito menos estavel (6 anos negativos). Nao virou referencia: decide o Antonio |

Leitura honesta (10 linhas):
1. 43 testes de estrategias (#1-#43); passaram no criterio oficial 2 (#30 double7-d, #40 fomc-holiday-1h). Ideias do agente: 28 (quanto mais, mais desconfianca num resultado isolado).
2. #1-#21 (suporte/resistencia, intraday 1m/5m, setup do Antonio): todos negativos ou ~0R depois de custos.
3. As compras de quedas no diario (#23, #26, #27, #35) tem uma vantagem pequena por trade (+0.05 a +0.2R), positiva em quase todos os indices.
4. ERRO corrigido a 2026-11-18: C1-C10 contavam trades sobrepostas (C5 +12.5%/ano era na verdade +0.9%, C11). O holdout C9 nao serve de prova.
5. Referencia continua C20 (so NQ, futuros; reconfirmada no fim da sessao 8): +2.6%/ano, 0/14 anos >= 14%, pior mes -1.7%, pior ano -1.5%, pior queda -3.0%. Faltam ~11.4%/ano.
6. #40 fomc-holiday-1h: forte em 2019-24, ~0 em 2012-18 e no holdout -> provavel sorte do periodo (C21 +5.6%/ano, fragil).
7. #42 ibs-cash-1h: IBS medido na sessao cash e comprado as 16:00 com stop de 1h: NQ +0.16R/trade nos dois periodos, t 2.8 (abaixo de 3.0). C22 +5.8%/ano mas pior queda -12.8%.
8. #43 rsi2-cash-1h: o mesmo para o RSI(2): NQ +0.3R/trade nos dois periodos (stop cabe em 1 MNQ com ~36 mil USD), mas S&P e Dow ~0 em 2019-24 -> reprovada; o NQ sozinho nao prova nada.
9. Padrao: comprar quedas mede-se melhor nos fechos das 16:00 no NQ; nos outros indices a vantagem e fraca ou instavel. Pode ser sorte do NQ (subida forte desde 2012).
10. Proximo: decisao do Antonio entre C20 (estavel), C21 e C22 (mais %/ano, menos estaveis). Limite da noite atingido (8 de 8 ideias).
