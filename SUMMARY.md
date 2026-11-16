# Resumo (periodo dev 2019-2024, custos CFD incluidos)

| variante | t junto | veredicto |
|---|---|---|
| plano original: 12 combinacoes bounce/break/fake x pdhl/pwhl/swing1h/round | -15.79 a +1.34 | 12/12 REPROVADAS |
| ideia `gapfill-pdc` (fade do gap 0.1-0.6% ate ao fecho anterior) | -1.34 | REPROVADA |
| ideia `fake-onhl` (falso rompimento max/min overnight) | -4.62 | REPROVADA |
| ideia `break-nr4` (rompimento do dia anterior apos dia NR4) | -1.12 | REPROVADA |

Leitura honesta: 15/15 testes reprovados (12 do plano + 3 ideias do agente; total de ideias do agente: 3). O gap fill
fecha ~50% das vezes com alvo 1:1, ou seja moeda ao ar antes de custos e ligeiramente negativo depois. O sweep da
max/min overnight e claramente perdedor (os rompimentos "falsos" continuam mais vezes do que voltam). O NR4 so ajuda
no NQ (+0.07R) e piora ES/Dow. Nada chega perto de t 3.0; o unico t positivo continua a ser break-pwhl (+1.34).
Confirma o historico: regras mecanicas intraday nos indices EUA com custos de CFD nao mostram edge. Holdout intocado.
