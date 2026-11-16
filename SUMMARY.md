# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| setup do Antonio (IFVG 1m, tp 1/2/3) - NQ cerca de -0.18R por trade | -17.5 / -13.0 / -10.7 | 3/3 REPROVADAS |
| ideias 1-6 do agente (gapfill, fake-onhl, break-nr4, break-lunchhl, gapgo-pdc, break-monhl) | -4.62 a **+2.34** | 6/6 REPROVADAS |
| ideias de prazo longo (diario): trend-sma100-d / rsi2-dip-d / donchian20-d | +0.70 / +0.89 / -0.19 | 3/3 REPROVADAS (< 60 trades) |

Leitura honesta: 24 testes, 24 reprovados (12 do plano, 3 do Antonio, 9 ideias; hoje 9 entradas em IDEAS.md, limite de 8 atingido).
NQ primeiro: nenhuma regra intraday tem R por trade positivo com folga depois de custos; o setup do Antonio perde ~0.18R por trade.
O melhor isolado continua o `gapgo-pdc` (t 2.34, abaixo de 3.0); depois de 24 testes isso e o esperado por sorte.
As ideias diarias dao poucas trades em 6 anos; o proximo passo (proxima noite) e 1h/4h, como manda o novo foco. Holdout intocado.
