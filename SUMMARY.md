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

Leitura honesta cripto (2026-11-19, sessao das :00 n.o 3):
1. Ideias cripto testadas no total: 24 (K1 = 4, 6 compras de quedas, 2 diagnosticos de alvo, #100-#111). Mais testes = mais desconfianca.
2. Melhor win rate com resultado positivo: 60% (#107, +0.28R, falha trades na SOL); entre as que passaram o dev: 54% (#106, +0.22R).
3. Saida parcial (#108, #110) e breakeven (#111) medidos: sobem o ganho por trade (2-3x o do alvo inteiro) mas NAO sobem o win rate.
4. Causa provavel: a #106 tem ~100 trades por moeda e a #105 (mesmas entradas) ~40; o win rate de 54% vem sobretudo das RE-ENTRADAS depois do alvo (tendencia forte -> novo alvo rapido). Com metade a correr nao ha re-entrada.
5. Em 4h a rutura de 20 velas (#109) e pior que no diario (#107): a saida de 10 velas de 4h e curta e corta as trades antes do alvo (win rate 41% vs 60%).
6. O regime BTC continua a apagar 2022: #109-#111 nao tem nenhum ano negativo no dev. #111 (+11.9%/ano, pior ano 0%) falhou so por t 2.96.
7. Escolha clara: win rate >= 50% (alvo inteiro, ~+3-9%/ano) OU mais % ao ano (parcial/breakeven/sem alvo, win rate 35-42%). Ainda nada da as duas coisas.
8. Pre 2017-18 continua quase vazio com o filtro BTC (BTC acima da media de 200 dias so 9 dias em 2018): decisao do Antonio pendente.
9. Nenhuma carteira K2 criada. Conta demo continua na K1. Holdouts abertos: so K1 e #100.
10. Proximo: rutura no DIARIO com mais sinais (ex.: rutura de 20 dias com alvo 1R e saida de 10 dias, mas com o regime da propria moeda em vez do BTC) para a SOL passar 60 trades.

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
