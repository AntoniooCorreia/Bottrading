# Resumo (custos CFD incluidos)

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

## Carteiras (C) - 1% por trade, % da conta por ano (2012-2025)

| # | data | carteira | % ao ano | anos >= 14% | pior mes / pior ano / pior queda | trades/semana | veredicto |
|---|---|---|---|---|---|---|---|
| C1 | 2026-11-16 | #23 + #26 + #27 (rsi2-dip-d, ibs-dip-d, down3-d), 10 indices, max 3 abertas | +8.7% | 5/13 | - / - / -21.6% | ~3.4 | substituida por C2 |
| C2 | 2026-11-17 | C1 + 1 trade por regiao + paragem mensal a -3% | +9.5% | 5/14 | -5.1% / -2.5% / -10.7% | - | substituida por C5 |
| C3 | 2026-11-17 | C2 + #30 double7-d | +7.3% | - | - / - / -16.5% | - | piora |
| C4 | 2026-11-17 | C2 + #33 week-rev-d | +5.8% | - | - / - / -13.8% | - | piora |
| C5 | 2026-11-17 | C2 + #35 ibs-bear-d | **+12.5%** | **6/14** | -5.5% / -4.5% / -9.1% | ~3.5 | **REFERENCIA ATUAL** |
| C6 | 2026-11-18 | C5 + #37 keyrev-d | +11.6% | 4/14 | -4.9% / -0.4% / -12.2% | - | piora |
| C7 | 2026-11-18 | C5 + #38 pullback20-d | +9.6% | 5/14 | -5.8% / -5.0% / -11.4% | ~3.1 | piora |
| C8 | 2026-11-18 | C5 so no NQ (pedido do Antonio) | +3.6% | 0/14 | -1.7% / -0.9% / -3.1% | ~0.7 | muito estavel mas longe dos 14% |
| C9 | 2026-11-18 | C5 no **holdout 2025-26** (uma vez, decisao do Antonio) | 2025 +17.2%, 2026 +34.5% | 2/2 | -3.6% / +17.2% / -7.4% | ~4.4 | **positiva -> segue para demo** (anos de subida: cautela) |

Leitura honesta (10 linhas):
1. 39 testes de estrategias (#1-#39); so 1 passou no criterio oficial (#30 double7-d). Ideias do agente: 24 (quanto mais, mais desconfianca num resultado isolado).
2. #1-#21 (suporte/resistencia, intraday 1m/5m, setup do Antonio): todos negativos ou ~0R depois de custos.
3. O que funciona sao compras de quedas no diario (#23, #26, #27, #35): pequenas (+0.05 a +0.2R por trade) mas positivas em quase todos os indices.
4. Carteira de referencia C5: +12.5%/ano, 6/14 anos >= 14%, pior mes -5.5%, pior ano -4.5%, pior queda -9.1%, ~3.5 trades/semana.
5. Faltam ~1.5% ao ano para o objetivo de 14%; trades um pouco acima das 2-3 por semana pedidas.
6. C8 (so NQ): +3.6%/ano, ~0.7 trades/semana. So com o NQ o objetivo nao e alcancavel com estas regras.
7. Atencao: C5 inclui 2025 e o #35 nao foi ao holdout. Tratar +12.5% com cautela.
8. Calendario, NR7, vender, dias de reversao, maximos em subidas calmas (#28, #31, #32, #34, #36, #37, #39): ~0R.
9. C9 (C5 no holdout 2025-26): positiva, pior mes -3.6%. Proximo passo: conta demo MT5 no PC do Antonio (live/c5_live.py).
10. Nota: RESULTS.md tem uma linha duplicada de tom-d (pre), corrida duas vezes por engano; mesmo resultado.
