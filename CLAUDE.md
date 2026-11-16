# Bottrading: pesquisa de suporte e resistencia (backtest)

Projeto do Antonio. Objetivo: descobrir se alguma regra MECANICA de suporte/resistencia tem edge real
nos indices americanos (NQ, S&P 500, Dow) em CFDs, DEPOIS de custos. So backtest: nada de MT5,
nada de broker, nada de chaves. O MT5 (conta demo STARTRADER) so entra no PC do Antonio e so
para uma variante que tenha passado o holdout.

Escreve tudo (commits, relatorios, notas) em portugues de Portugal, sem acentos nos ficheiros .py.

## Historico (ja testado noutro chat, NAO repetir)
FVG HTF + IFVG 1m (negativo), sweep de sessao + FVG (sem sinais), opening range (zero),
intraday momentum (negativo recente), noise boundary (so NQ, negativo em ES/Dow),
trend following multi-ativo diario com CFDs (Sharpe ~0, financiamento mata). Conclusao ate agora:
regras intraday nos indices EUA com custos de CFD raramente sobrevivem. Espera-se o mesmo aqui;
o trabalho e confirmar ou desmentir com honestidade, nao "encontrar" algo.

## Comandos
- `pip install -r requirements.txt`
- `python download.py` - descarrega 1m da Dukascopy e cria `data/m5/*.csv.gz` (so se faltarem; os
  .csv.gz de 5m estao no repo, faz commit deles se os criares)
- `python -m pytest -q` - TEM de passar antes de qualquer commit
- `python run.py --play bounce|break|fake --levels pdhl|pwhl|swing1h|round [--tp 2 --stop-atr 0.5 --fake-atr 0.3 --session rth|all]`
  regista sozinho uma linha em `results/RESULTS.md`

## Protocolo (OBRIGATORIO - e o que impede enganar-nos a nos proprios)
1. So se testa o que esta em `TODO.md` com `[ ]`. Nao inventes variantes novas para testar.
   Ideias novas vao para `IDEAS.md` (com o porque); o Antonio decide se passam para o TODO.
2. Periodo `dev` (2019-2024) para tudo. O `holdout` (2025-2026) esta FECHADO.
3. Criterio de aprovacao no dev e fixo e esta em run.py (>=100 trades por indice, meanR>0 em CADA
   indice, t junto >= 2.5). Nao mexas nos criterios, nos custos (SPEC em sr/data.py) nem nos periodos.
4. Holdout: so para variantes com veredicto PASSA no dev, UMA vez por variante, com
   `--period holdout --unlock-holdout`. Fica registado em HOLDOUT_LOG.md. Nunca afines depois de ver o holdout.
5. Se mudares o motor (sr/), explica no commit, mantem/acrescenta testes (passeio aleatorio sem edge
   e sem lookahead) e volta a correr as variantes ja testadas que o bug possa ter afetado.
6. Nunca apagues linhas de results/RESULTS.md.

## Fluxo de cada sessao autonoma
1. `git pull`; trabalha no branch `research` (cria-o a partir do main se nao existir).
2. Se nao houver nenhum `[ ]` em TODO.md: escreve no maximo 3 linhas em NOTES.md e termina. Nao gastes mais.
3. Garante dados em data/m5 (download.py so se faltarem) e testes a passar.
4. Pega nos itens `[ ]` por ordem. ANTES de cada um: `python sync.py --log estado "A correr <variante>"` (o dashboard mostra
   isto em tempo real); depois corre-o, marca `[x]` com o veredicto e `python sync.py --log teste "<variante>: <veredicto>, t junto <t>"`.
5. Atualiza `SUMMARY.md`: tabela curta do que passou/reprovou e a tua leitura honesta, em 10 linhas.
6. Commit + push para `research`; se nao houver PR aberto de research -> main, abre um.
