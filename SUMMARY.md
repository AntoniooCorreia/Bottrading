# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| setup do Antonio (IFVG 1m, tp 1/2/3) - NQ cerca de -0.18R por trade | -17.5 / -13.0 / -10.7 | 3/3 REPROVADAS |
| ideias 1-6 do agente (gapfill, fake-onhl, break-nr4, break-lunchhl, gapgo-pdc, break-monhl) | -4.62 a **+2.34** | 6/6 REPROVADAS |
| ideias de prazo longo (diario): trend-sma100-d / rsi2-dip-d / donchian20-d | +0.70 / +0.89 / -0.19 | 3/3 REPROVADAS (< 60 trades) |
| mais trades: rsi2-dip-4h / ibs-dip-d / down3-d | ver TODO | 3/3 REPROVADAS no criterio oficial (Dow negativo ou ~0R) |

Leitura honesta: 27 testes, 27 reprovados no criterio oficial (12 do plano, 3 do Antonio, 12 ideias do agente). Total de ideias do agente testadas: 12.
NQ primeiro: nenhuma regra intraday sobrevive aos custos; nas diarias de comprar quedas o NQ e positivo mas pequeno (rsi2-dip-d ~1.2R/ano).
Carteira de referencia (rsi2-dip-d + ibs-dip-d + down3-d, 10 indices, max 3 abertas, 2012-2024): +8.7% ao ano, 5 anos >= 14%, pior queda -21.6%, ~175 trades/ano.
Faltam ~5.3% ao ano para o objetivo de 14%. Atencao: nenhuma das 3 cumpre a regra de entrada a risca (Dow negativo no dev em todas); e a melhor aproximacao, nao um edge provado.
Nota: a contagem por ano inclui um "2025" (-0.3%) de trades abertas em dez/2024 que fecham em 2025 (14 anos em vez de 13); efeito pequeno, a rever.
Sessao 4 de 2026-11-16: limite de ideias da noite ja atingido (12 entradas hoje em IDEAS.md), nada novo testado. Holdout intocado.
