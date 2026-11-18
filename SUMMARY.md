# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| setup do Antonio (IFVG 1m, tp 1/2/3) - NQ cerca de -0.18R por trade | -17.5 / -13.0 / -10.7 | 3/3 REPROVADAS |
| ideias 1-6 do agente (gapfill, fake-onhl, break-nr4, break-lunchhl, gapgo-pdc, break-monhl) | -4.62 a **+2.34** | 6/6 REPROVADAS |
| ideias de prazo longo (diario): trend-sma100-d / rsi2-dip-d / donchian20-d | +0.70 / +0.89 / -0.19 | 3/3 REPROVADAS (< 60 trades) |
| mais trades: rsi2-dip-4h / ibs-dip-d / down3-d | ver TODO | 3/3 REPROVADAS no criterio oficial (Dow negativo ou ~0R) |
| ideias 13-15 (2026-11-17): tom-d / overnight-us-1h / **double7-d** | +1.30 / -1.60 / **+3.07** | 2 REPROVADAS; **double7-d PASSA** (dev e 2012-2018) |
| ideias 16-18 (2026-11-17, sessao 2): opex-week-d / nr7-up-d / week-rev-d | -0.98 / -0.77 / +1.83 | 3/3 REPROVADAS (week-rev-d positiva nos 3, mas piora a carteira) |
| ideia 19 (2026-11-17, sessao 3): rsi2-pop-short-4h (vender subidas em tendencia de baixa) | -2.46 | REPROVADA (negativa nos 3, dev e 2012-2018) |
| ideia 20 (2026-11-17, sessao 4): **ibs-bear-d** (comprar quedas ABAIXO da media de 200) | +1.62 | REPROVADA no oficial (NQ 51 trades < 60), positiva nos 3 em dev e 2012-2018 -> **entra na carteira** |
| ideia 21 (2026-11-18): turnaround-tue-d (comprar a terca depois de uma segunda em queda) | +0.21 | REPROVADA (~0R: NQ -0.002R, Dow negativo) |
| ideia 22 (2026-11-18, sessao 2): keyrev-d (minimo novo de 10 dias que fecha acima do dia anterior) | +0.36 | REPROVADA (~0R em dev, poucas trades); piora a carteira (+11.6%/ano) |
| ideia 23 (2026-11-18, sessao 3): pullback20-d (recuo a media de 20 dias em tendencia forte) | +1.15 | REPROVADA (poucas trades; NQ +0.11R); piora a carteira (+9.6%/ano) |
| ideia 24 (2026-11-18, sessao 4): calmhigh-d (maximo novo de 10 dias numa subida calma) | +0.32 | REPROVADA (NQ +0.12R mas S&P e Dow negativos; 2012-2018 ~0R) |

Leitura honesta (10 linhas):
1. 39 testes; so 1 passou no criterio oficial (double7-d). Ideias do agente testadas: 24 (quanto mais, mais desconfianca num resultado isolado).
2. ibs-bear-d: pequeno (NQ +0.056R/trade, ~0.5R/ano por indice), t baixo (1.6 dev, 1.0 pre). Sozinha nao prova nada.
3. Mas foi pensada para a carteira (trades quando as outras estao paradas) e faz isso: positiva nos 10 indices na carteira, e ganha em 2020 e 2022.
4. Carteira nova (rsi2-dip-d + ibs-dip-d + down3-d + ibs-bear-d, 10 indices, max 3 abertas, 1 por regiao, paragem -3%/mes):
   +12.5%/ano (era +9.5%), 6/14 anos >= 14%, pior queda -9.1% (era -10.7%), 108/148 meses positivos, ~183 trades/ano (~3.5/semana).
5. Custo: pior ano -4.5% (2018; era -2.5%) e pior mes -5.5% (era -5.1%). Ligeiramente menos consistente nos piores casos.
6. Atencao: o periodo "tudo" da carteira inclui 2025; o ibs-bear-d nao foi ao holdout (nao passou no oficial). Tratar +12.5% com cautela.
7. Intraday (1m/5m/1h) com custos de CFD: ~0R ou negativo. Calendario, NR7, vender, dias de reversao, comprar maximos em subidas calmas (calmhigh-d): ~0R. Recuos de semanas (pullback20-d) pioram a carteira.
8. Carteira confirmada a 2026-11-18, sessao 4 (igual, +12.5%/ano, 6/14 anos >= 14%): faltam ~1.5% ao ano para o objetivo de 14%. Trades ~3.5/semana, um pouco acima das 2-3 pedidas.
9. Proximo passo: confirmar a carteira nova no holdout (decisao do Antonio) antes de qualquer conta demo.
10. Nota: RESULTS.md tem uma linha duplicada de tom-d (pre), corrida duas vezes por engano; mesmo resultado.
