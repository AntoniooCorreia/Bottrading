# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| setup do Antonio (IFVG 1m, tp 1/2/3) - NQ cerca de -0.18R por trade | -17.5 / -13.0 / -10.7 | 3/3 REPROVADAS |
| ideias 1-6 do agente (gapfill, fake-onhl, break-nr4, break-lunchhl, gapgo-pdc, break-monhl) | -4.62 a **+2.34** | 6/6 REPROVADAS |
| ideias de prazo longo (diario): trend-sma100-d / rsi2-dip-d / donchian20-d | +0.70 / +0.89 / -0.19 | 3/3 REPROVADAS (< 60 trades) |
| mais trades: rsi2-dip-4h / ibs-dip-d / down3-d | ver TODO | 3/3 REPROVADAS no criterio oficial (Dow negativo ou ~0R) |
| ideias 13-15 (2026-11-17): tom-d / overnight-us-1h / **double7-d** | +1.30 / -1.60 / **+3.07** | 2 REPROVADAS; **double7-d PASSA** (dev e 2012-2018) |
| ideia 19 (2026-11-17, sessao 3): rsi2-pop-short-4h (vender subidas em tendencia de baixa) | -2.46 | REPROVADA (negativa nos 3, dev e 2012-2018) |
| ideias 16-18 (2026-11-17, sessao 2): opex-week-d / nr7-up-d / week-rev-d | -0.98 / -0.77 / +1.83 | 3/3 REPROVADAS (week-rev-d positiva nos 3 em dev e 2012-2018, mas piora a carteira) |

Leitura honesta (10 linhas):
1. 34 testes; so 1 passou no criterio oficial (double7-d). Ideias do agente testadas: 19 (quanto mais, mais desconfianca num resultado isolado).
2. double7-d: NQ +0.20R/trade (~+2.9%/ano), S&P +0.14R, Dow +0.04R; passa tambem em 2012-2018 (t 3.46). Holdout positivo nos 3 mas curto (78 trades, t 1.51).
3. Tudo o que e intraday (1m/5m/1h) com custos de CFD da ~0R ou negativo. O que funciona e comprar quedas curtas no diario em tendencia de alta.
4. Calendario (viragem do mes, vencimento de opcoes) e volatilidade (NR7): ~0R em 2019-2024.
5. Lado vendedor (rsi2-pop-short-4h, sessao 3): negativo nos 3 e nos dois periodos; vender indices dos EUA nao tem vantagem.
6. Carteira de referencia (rsi2-dip-d + ibs-dip-d + down3-d, 10 indices, max 3 abertas, 1 por regiao, paragem a -3%/mes, 2012-2024):
   +9.5%/ano, 5/14 anos >= 14%, pior mes -5.1%, pior ano -2.5%, pior queda -10.7%, ~144 trades/ano (~2.8/semana).
7. Juntar double7-d ou week-rev-d nao melhora: sobrepoem-se as compras de quedas que ja la estao. Mantem-se a referencia.
8. Faltam ~4.5% ao ano para o objetivo de 14%. Precisamos de sinais diferentes (nao mais variantes de comprar quedas), e esses tem falhado.
9. Nota: RESULTS.md tem uma linha duplicada de tom-d (pre), corrida duas vezes por engano; mesmo resultado.
