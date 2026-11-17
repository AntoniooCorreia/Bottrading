# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| setup do Antonio (IFVG 1m, tp 1/2/3) - NQ cerca de -0.18R por trade | -17.5 / -13.0 / -10.7 | 3/3 REPROVADAS |
| ideias 1-6 do agente (gapfill, fake-onhl, break-nr4, break-lunchhl, gapgo-pdc, break-monhl) | -4.62 a **+2.34** | 6/6 REPROVADAS |
| ideias de prazo longo (diario): trend-sma100-d / rsi2-dip-d / donchian20-d | +0.70 / +0.89 / -0.19 | 3/3 REPROVADAS (< 60 trades) |
| mais trades: rsi2-dip-4h / ibs-dip-d / down3-d | ver TODO | 3/3 REPROVADAS no criterio oficial (Dow negativo ou ~0R) |
| ideias 13-15 (2026-11-17): tom-d / overnight-us-1h / **double7-d** | +1.30 / -1.60 / **+3.07** | 2 REPROVADAS; **double7-d PASSA** (dev e 2012-2018) |
| ideias 16-18 (2026-11-17, sessao 2): opex-week-d / nr7-up-d / week-rev-d | -0.98 / -0.77 / +1.83 | 3/3 REPROVADAS (week-rev-d positiva nos 3 em dev e 2012-2018, mas piora a carteira) |

Leitura honesta: 33 testes; 1 passou no criterio oficial (double7-d). Total de ideias do agente testadas: 18 (quanto mais, mais desconfianca num resultado isolado).
double7-d (comprar fecho minimo de 7 dias acima da media de 200): NQ +0.20R/trade (~+2.9%/ano), S&P +0.14R, Dow +0.04R; tambem passa em 2012-2018 (t 3.46).
Holdout 2025-2026 (uma vez): positiva nos 3 (NQ +0.04R, S&P +0.07R, Dow +0.16R) mas so 78 trades, t 1.51: confirma a direcao, nao prova. Dow fraco em todos os periodos.
tom-d (viragem do mes) e overnight-us-1h (comprar ao fecho, vender a abertura): ~0R; os custos/financiamento do CFD comem o pouco que ha.
Carteira de referencia (rsi2-dip-d + ibs-dip-d + down3-d, 10 indices, max 3 abertas, 1 por regiao, paragem a -3%/mes, 2012-2024): +9.5%/ano, 5/14 anos >= 14%, pior mes -5.1%, pior ano -2.5%, pior queda -10.7%, ~144 trades/ano.
Juntar double7-d nao melhora: nos 10 indices piora (+7.3%/ano; negativa fora dos EUA) e so nos EUA fica igual (+9.4%/ano, pior queda -9.7%). Mantem-se a referencia.
Faltam ~4.5% ao ano para o objetivo de 14%. As ideias de comprar quedas sobrepoem-se: precisamos de sinais diferentes, nao de mais variantes da mesma coisa.
Sessao 2 de 2026-11-17: opex-week-d (semana de vencimento de opcoes) funcionava em 2012-2018 e desapareceu em 2019-2024; nr7-up-d ~0R. week-rev-d (comprar depois de uma semana em queda) da NQ +0.15R/trade mas e mais uma compra de quedas: na carteira piora (+8.9%/ano so nos EUA).
Nota: RESULTS.md tem uma linha duplicada de tom-d (pre), corrida duas vezes por engano; mesmo resultado.
