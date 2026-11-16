# Bottrading: pesquisa de suporte e resistencia (backtest)

Projeto do Antonio. Objetivo: descobrir se alguma regra MECANICA de suporte/resistencia tem edge real
nos indices americanos (NQ, S&P 500, Dow) em CFDs, DEPOIS de custos. So backtest: nada de MT5,
nada de broker, nada de chaves. O MT5 (conta demo STARTRADER) so entra no PC do Antonio e so
para uma variante que tenha passado o holdout.

O Antonio so opera o US100 (NQ). O S&P e o Dow ficam nos testes APENAS como confirmacao (detetor de sorte):
um edge real tem de aparecer nos tres. Em relatorios, diario e Telegram mostra sempre o NQ primeiro e com mais
detalhe (R por trade, win rate, R por mes); S&P e Dow numa linha curta como confirmacao.

O Antonio arrisca SEMPRE 1% da conta por trade (1R = 1%). No diario e no Telegram traduz resultados para
% da conta (ex.: +0.1R por trade = +0.1% por trade; 12R por ano = +12% ao ano).

OBJETIVO DO ANTONIO (2026-11-16): pelo menos +14% ao ano com 1% de risco por trade, ou seja >= 14R por ano no total
da carteira de estrategias, com queda maxima pequena. Nenhuma estrategia sozinha chega la (a melhor ate agora,
rsi2-dip-d, da ~1.2R/ano no NQ): o caminho e juntar VARIAS estrategias validadas e pouco correlacionadas
(mais trades por ano com a mesma vantagem: 4h/1h, outras formas de comprar quedas, outros sinais). O Antonio aceitou operar
outros indices (DAX, FTSE, Nikkei, Euro Stoxx, CAC, ASX, Hang Seng) desde que o objetivo seja atingido sempre ou
quase sempre. Uma ideia so entra na carteira se tiver passado no criterio oficial OU se for positiva nos 3 indices
dos EUA em 2012-2018 e em 2019-2024. Carteira de referencia atual (2026-11-16): rsi2-dip-d nos 10 indices, +3.2%/ano, 1/13 anos >= 14%, pior queda
-24.9%. So substituis o estado "portfolio" do dashboard por uma carteira MELHOR (mais % ao ano ou mais anos >= 14%);
nunca o apagues nem o troques por uma carteira vazia. No fim de cada sessao corre portfolio.py com as ideias aceites e diz no
SUMMARY.md e no --log fim quanto da (% ao ano, anos acima de 14%) e quanto falta. Nunca chegar la aumentando o risco por trade.

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
- `python run.py --play antonio --levels all --tp 1|2|3` - setup do Antonio em velas de 1m (sr/antonio.py; precisa de data/m1gz)
- `python run_swing.py --idea <nome>` - ideias de prazo mais longo (15m/1h/4h/diario), registadas em sr/swing_ideas.py;
  reporta custos de CFD (veredicto oficial) e de micro-futuros MNQ/MES/MYM
- `python portfolio.py --ideas a,b,c [--markets nq,dax,...] [--period tudo]` - carteira de ideias em varios indices,
  1% por trade: media % ao ano, anos acima de 14%, pior queda. Envia para o dashboard. E A METRICA DO OBJETIVO.
  Indices disponiveis: nq es dow (confirmacao) + dax ftse nikkei estx cac asx hsi (carteira; ver sr/data.py)
- `python run.py --play bounce|break|fake --levels pdhl|pwhl|swing1h|round [--tp 2 --stop-atr 0.5 --fake-atr 0.3 --session rth|all]`
  regista sozinho uma linha em `results/RESULTS.md`

## Protocolo (OBRIGATORIO - e o que impede enganar-nos a nos proprios)
1. So se testa o que esta em `TODO.md` com `[ ]`. Quando o TODO estiver vazio, entra o "modo ideias" (ver abaixo):
   so assim podes acrescentar testes novos, e sempre registados ANTES de correr.
2. Periodo `dev` (2019-2024) para tudo. O `holdout` (2025-2026) esta FECHADO.
3. Criterio de aprovacao no dev e fixo e esta em run.py (>=100 trades por indice, meanR>0 em CADA
   indice, t junto >= 2.5 para o plano original e >= 3.0 para ideias do agente - min_t_for em run.py). Nao mexas nos criterios, nos custos (SPEC em sr/data.py) nem nos periodos.
4. Holdout: so para variantes com veredicto PASSA no dev, UMA vez por variante, com
   `--period holdout --unlock-holdout`. Fica registado em HOLDOUT_LOG.md. Nunca afines depois de ver o holdout.
5. Se mudares o motor (sr/), explica no commit, mantem/acrescenta testes (passeio aleatorio sem edge
   e sem lookahead) e volta a correr as variantes ja testadas que o bug possa ter afetado.
6. Nunca apagues linhas de results/RESULTS.md.

## Modo ideias (o agente pensa sozinho) - so quando o TODO nao tem [ ]
O Antonio quer que o agente invente e teste ideias novas durante a noite. Regras para isso nao virar
"procurar ate encontrar sorte":
1. Limite: no maximo 3 ideias novas por sessao e 8 por noite (conta as entradas de hoje em IDEAS.md).
   Se o limite da noite ja foi atingido: `python sync.py --log fim "Limite de ideias da noite atingido"` e termina.
2. Cada ideia e registada em `IDEAS.md` ANTES de correr, com: data, nome curto, hipotese (porque podera ter edge,
   com base em comportamento de mercado conhecido, nao em olhar para os resultados), regras exatas de entrada,
   stop, alvo e sessao, e os parametros (fixos; nada de grelhas de otimizacao). Faz commit desse registo primeiro.
3. FOCO (decidido a 2026-11-16 depois de tudo em 1m/5m dar ~0R antes de custos): ideias de PRAZO MAIS LONGO,
   timeframes 15m, 1h, 4h e diario, trades de horas a dias, stops largos (custos passam de ~0.15-0.25R para ~0.03R).
   Usa sr/swing.py + sr/swing_ideas.py + run_swing.py (os testes em tests/test_swing.py apanham a ideia sozinhos).
   Intraday 1m/5m so com uma razao muito forte. Pode ser long-only. Proibido: martingale, sem stop,
   grid, mexer em custos, periodos ou criterios, usar dados do holdout, e repetir o que ja reprovou (ver historico
   e results/RESULTS.md).
4. Implementa a ideia como funcao em sr/swing_ideas.py e acrescenta-a ao dicionario IDEAS (timeframe, stop_atr,
   tp_r, max_hold fixos). pytest tem de passar antes de correr (passeio aleatorio sem edge + sem lookahead).
   Criterio em run_swing.py: >= 60 trades por indice, meanR > 0 em cada indice, t junto >= 3.0, com custos de CFD.
5. Acrescenta a ideia ao TODO numa seccao "Ideias do agente (AAAA-MM-DD)" e corre-a como qualquer item.
   Ideias novas tem fasquia t >= 3.0 (automatico no run.py).
6. Uma ideia que PASSE no dev vai uma vez ao holdout. Escreve no SUMMARY.md a leitura honesta, incluindo quantas
   ideias ja foram testadas no total (quanto mais, mais desconfianca num resultado isolado).

## Diario (o que o Antonio ve no dashboard e no Telegram)
O Antonio acompanha tudo pelo diario. Escreve para ele perceber sem ler codigo: frases curtas, portugues simples,
numeros concretos. Usa `python sync.py --log <tipo> "titulo" -b "ponto" -b "ponto"`:
- `estado` "o que estas a fazer agora" (sem pontos; nao vai para o Telegram)
- `ideia` "<nome>: <hipotese numa frase>" com pontos: Porque pode funcionar / Entrada / Stop e alvo / Sessao / Fasquia (t >= 3.0)
- `teste` "<variante>: PASSA|REPROVADA" com pontos: resultado por indice (R por trade e trades), win rate, R por mes,
  e "O que aprendemos: ..." numa frase
- `mudanca` "<o que mudou>" com pontos: o que mudou, porque, e o efeito (ex.: testes, resultados afetados)
- `erro` "<o que falhou>" com pontos: causa provavel e o que fizeste
- `fim` "<resumo numa linha>" com pontos: ideias testadas, o que passou, proximo passo

## Fluxo de cada sessao autonoma
1. `git pull`; trabalha no branch `research` (cria-o a partir do main se nao existir).
2. Se nao houver nenhum `[ ]` em TODO.md: modo ideias (seccao acima), dentro dos limites.
3. Garante dados em data/m5 (download.py so se faltarem) e testes a passar.
4. Pega nos itens `[ ]` por ordem. ANTES de cada um: `--log estado "A correr <variante>"`; depois corre-o, marca `[x]`
   com o veredicto e regista um `--log teste` com pontos (ver Diario). Ideias novas: `--log ideia` com pontos antes de as testar;
   mudancas ao motor ou ao projeto: `--log mudanca` com pontos.
5. Atualiza `SUMMARY.md`: tabela curta do que passou/reprovou e a tua leitura honesta, em 10 linhas.
6. Commit + push para `research`; se nao houver PR aberto de research -> main, abre um.
