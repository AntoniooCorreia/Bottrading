# FOCO ATUAL (2026-11-18): SO CRIPTO (Kraken spot, long-only). ESTA SECCAO MANDA SOBRE O RESTO DO FICHEIRO.
Decisao do Antonio: o laboratorio de indices foi arquivado (Supabase schema `arquivo`); agora so se testa cripto
(BTC, ETH, SOL; dados 1h da Binance em data/crypto, `python crypto_download.py` se faltarem). Custos Kraken: 0.26% por lado + 0.05% slippage
(COST_PCT em crypto_lab.py: NAO mexer). Spot = so long, sem alavancagem.
- Backtest: `python crypto_lab.py --ideas a,b --period dev|pre|holdout [--label K2 --push]`. Imprime por ideia/moeda, a linha
  `VEREDICTO <ideia>: PASSA|REPROVADA` e a carteira (1 posicao por moeda, 1% de risco por trade, win rate, pior mes/ano/queda).
- CARTEIRAS DE BACKTESTING (pedido do Antonio, 2026-11-19): CADA teste e uma carteira no painel, PASSE OU NAO.
  Corre sempre `python crypto_lab.py --ideas ... --period dev --push --nota "#1xx nome: o que muda"` (sem --label usa o proximo K livre:
  K6, K7, ...). Isto grava `portfolio_Kn` no Supabase e aparece no separador Backtesting > Carteiras, ordenada contra os objetivos
  (validada, holdout, >= 14%/ano, pior ano > -10%, pior mes > -5%, win rate >= 50%, 2-3 trades/semana) com o porque.
  NUNCA uses --ref (troca a carteira da conta demo) sem o OK do Antonio. Uma ideia testada sem carteira no painel conta como nao feita.
- CRITERIO OFICIAL CRIPTO (fixo): por ideia, no dev 2019-2024, >= 60 trades em CADA moeda, meanR > 0 em CADA moeda, t junto >= 3.0.
  E CONFIRMACAO (pedido do Antonio, mais backtesting): a linha `CONFIRMACAO` tem de ser positiva em >= 3 das 5 moedas extra
  (XRP, ADA, DOGE, LINK, AVAX; dados em data/crypto desde 2018-2020). Depois `--period pre` (2017-2018, confirmacao, tem de ser >= 0) e, se passar, UMA vez `--period holdout` (2025-2026), registado em HOLDOUT_LOG.md.
- Catalogo cripto: K1 = k-donchian20-d + k-sma100-d + k-donchian55-4h + k-sma200-4h. Dev +52%/ano mas win rate 25%, pior ano -21%,
  holdout 2025-26 JA ABERTO: -10.9% (2025), queda -40%. Reprovado como robusto; o holdout da K1 nao pode voltar a ser usado.
  Numeracao cripto: estrategias #100, #101, ... e carteiras K2, K3, ..., sempre com data.
- JA TESTADO EM CRIPTO (2017-2024, nao repetir igual): rsi2-dip-d, ibs-dip-d, down3-d, double7-d, pullback20-d -> win rate 56-71% mas ~0R
  depois de custos; rsi2-dip-4h negativo (-0.1R/trade). K1 com alvo fixo: 1R -> win rate 49% e +0.10R/trade; 2R -> 35%, +0.21R; sem alvo 25%, +0.91R.
- Conta demo: Edge Function Supabase `paper-bot` (supabase/functions/paper-bot; sinais de hora a hora, stops a cada minuto com ?mode=stops)
  simula a K1 com precos reais da Kraken em 100 000 USD (pedido do Antonio: tudo em dolares, conta de 100k; pares XBTUSD/ETHUSD/SOLUSD); pagina "Conta demo" no dashboard; avisos no Telegram. Nenhuma ordem real.
  So troca de estrategia na demo uma variante que tenha PASSADO dev + pre + holdout, e com o OK do Antonio.

FREQUENCIA E DURACAO (pedido do Antonio, 2026-11-21): quer 3 a 4 trades por semana na carteira e NAO quer ficar dias em trade.
Scalping 5m/15m (#120-#127) e intraday 1h (#129-#132) ja testados: vantagem antes de custos existe, mas os custos de spot Kraken a matam.
Nao repetir scalping em spot. Perpetuos (`--venue perp`: 0.14% ida e volta + funding 0.01%/8h) testados em #133-#137: nada passou
(#133 rutura 24h long: t 2.16). ATENCAO: a tabela da Kraken de jul-2026 subiu o spot tier 1 para 0.40% maker / 0.80% taker; o COST_PCT
de spot (0.57% ida e volta) esta OTIMISTA. Nao mexer sem o Antonio, mas diz-lo quando falares de spot.
TESTES (pedido do Antonio, 2026-11-21): QUALQUER teste tem de aparecer no separador Testes. crypto_lab.py faz isso sozinho para
--period dev|pre|holdout (results/runs/<variante>__<periodo>.json + tabela runs com --push). Usa sempre --num "#1xx".

DEMO EXPERIMENTAL (pedido do Antonio, 2026-11-22: "quero que sejam os bots automaticamente a pensar nisso"): conta 2 da Edge Function
paper-bot, 100 000 USD, perpetuos simulados (long/short). As estrategias sao escolhidas SO pelo agente:
- No FIM de cada noite (ou depois de testar algo que caiba na demo): `python demo_pick.py --push`. Regras fixas no ficheiro
  (ganha nas 3 moedas com custos de perpetuos 2019-2024, >= 1 trade/semana, por ordem de t, sem repetir a mesma entrada, ate ~3/semana;
  so troca se a nova 1.a tiver t >= +0.3 acima da atual). Se a lista mudar: `--log mudanca "Demo experimental: agora corre X"` com o porque.
- So entra na demo o que estiver em sr/demo_spec.py SPECS (familias breakout, rsi2, lowclose, above_sma + filtros EMA e regime BTC).
  Ideia nova que caiba nestas familias: acrescenta a SPECS e corre pytest (tests/test_demo_spec.py compara a spec com a ideia E o
  engine.ts com o Python). Familia nova = mexer em engine.ts + demo_spec.py + testes; NAO faças deploy da Edge Function (o Antonio/Claude do chat faz).
- A conta 1 (K1) nao muda sem o OK do Antonio. A demo experimental nao e aprovacao; ao fim de 2-3 meses compara-se com o backtest.

## DEMO POR ESTILO + ROTACAO DE ESTILOS (pedido do Antonio, 2026-11-27)
A demo experimental tem agora 3 contas de 100 000 USD (perpetuos simulados): conta 2 = Swing (dias), conta 3 = Day trade (horas,
max ~24h), conta 4 = Scalping (velas 5m/15m). O estilo de cada spec sai de sr/demo_spec.py style(). `python demo_pick.py --push`
enche as 3 contas sozinho: primeiro as que passam as regras da demo; se nenhuma opera no regime atual do BTC, junta a melhor que
opere, marcada "nao passa no backtest (so para ver ao vivo)". O Antonio quer VER trades ao vivo e comparar os estilos no painel.
- Tudo o que PASSA ou QUASE passa (positivo nas 3 moedas com custos de perpetuos) e cabe nas familias de SPECS entra em SPECS + pytest
  + `demo_pick.py --push` no fim da sessao.
- Em CADA noite, as ideias tem de rodar pelos 3 estilos: pelo menos 1 de scalping (5m/15m), 1 de day trade (1h/4h, max 24h) e 1 de
  swing (diario/4h, dias). Sempre --venue perp, --num, carteira no painel. Scalping em spot continua proibido (custos matam).
- Cron paper-bot-5min (?mode=fast) trata das estrategias de 5m/15m; nao e preciso deploy para specs novas nas familias existentes.

## NOMES #BK / #D E SO 30 TESTES NO PAINEL (pedido do Antonio, 2026-11-27)
- Testes de backtesting = #BK<n> (a carteira K138 aparece como #BK138); contas demo = #D1 (K1), #D2 Swing, #D3 Day trade, #D4 Scalping.
  No diario, Telegram, SUMMARY e commits escreve SEMPRE #BK<n> para carteiras de backtesting e #D<n> para a demo (internamente o
  ficheiro continua results/carteiras/K<n>.json e a chave portfolio_K<n>; o --label continua K<n>). As estrategias mantem #2xx.
- O painel mostra so as 30 melhores #BK (pontuacao do best.py); as reprovadas fora do top 30 sao retiradas sozinhas (funcao
  private.prune_backtests no Supabase; ficam em arquivo.backtests_podados e no git). NAO voltes a enviar carteiras podadas.
- Calendario: as demos aparecem no seletor de carteiras do painel como #D, #D1..#D4 (trades fechadas).

## DEPOIS DA NOITE INTENSIVA (2026-11-27, chat com o Antonio: "faz os proximos passos")
- #221 = #197 em carteira de 8 moedas (spec "l-dc20-4h-bear-vol15-s2-tp2-mh12-8m" com coins + max_open 4) corre na demo Swing; a Edge Function
  ja trata 8 moedas (spec.coins) e max_open. Testes de carteira em 8 moedas: `crypto_lab.py --coins btc,eth,sol,xrp,ada,doge,link,avax
  --confirm "" --max-open 4` (o teste fica com sufixo -8m e nao pisa o original). O criterio oficial (BTC/ETH/SOL >= 60) NAO muda.
- Scalping (5m/15m) em mercado de baixa: 0 de 6 -> PARADO. A regra "1 ideia de scalping por noite" fica suspensa enquanto o BTC
  estiver abaixo da media de 200 dias; as ideias vao para day trade e swing (de preferencia em carteira de 8 moedas).
- Rutura de volatilidade (#213/#216) e familia nova: so entra na demo se alguem mexer no engine.ts (nao prioritario: t < 2).

## PRIORIDADE DA NOITE (pedido do Antonio, 2026-11-23): ESTRATEGIAS PARA MERCADO EM BAIXA -> DEMO EXPERIMENTAL A OPERAR JA
O BTC esta ~17-19% abaixo da media de 200 dias e TODAS as estrategias aprovadas para a demo precisam de BTC acima dela: a demo esta
parada. O Antonio quer ver trades. Enquanto o BTC estiver abaixo da media de 200 dias, TODAS as ideias da noite sao para esse regime
(antes da missao de baixo). Sempre com --venue perp (a demo simula perpetuos; shorts permitidos), --num, carteira no painel.
Caminhos com fundamento (escolhe, justifica e regista no IDEAS.md ANTES de correr; parametros fixos):
- espelhos em short das que passaram em alta: #163 ao contrario (moeda ABAIXO da media de 50 dias + BTC abaixo da media de 200 dias,
  stop 2 ATR, alvo 1R, maximo 3 dias), #139 ao contrario (media 100, maximo 10 dias), #138 ao contrario (media 600 velas de 4h);
- quebra do minimo de 10/20 dias em short com BTC em baixa e alvo curto; ressaltos de curto prazo em long dentro da baixa (sobrevenda
  extrema) com alvo 0.5-1R e maximo 1-3 dias.
Se passar o criterio oficial: acrescenta a sr/demo_spec.py SPECS (familias ja suportam short: breakout e above_sma com side -1 =
fecho abaixo da media; btc "bear"), corre pytest e `python demo_pick.py --push` (o demo_pick ja junta sozinho uma estrategia que
opere no regime atual). Nao faças deploy da Edge Function (nao e preciso para estas familias).

## NOITE INTENSIVA 26->27-11 (pedido do Antonio, 2026-11-27 01:45; SUBSTITUI o LIMITE REDUZIDO so nesta noite)
Sessoes as 02:00, 02:30, 03:00, 03:30 e 04:00 (Lisboa). Ate 4 ideias por sessao e 20 na noite (conta desde as 19:00 de 26-11,
so seccoes do agente). Roda pelos 3 estilos (scalping 5m/15m, day trade 1h/4h, swing), sempre --venue perp, --num, carteira no painel,
prioridade ao regime de BTC em baixa. Nenhuma sessao comeca ideias novas depois das 04:40; tudo acabado ate as 05:00.
A sessao das 04:00 (a ultima) faz no fim `python demo_pick.py --push` e `python sync.py --log fim "Resumo da noite 26-27/11: N testes, X passaram"`
com UM ponto (-b) por teste da noite inteira (todas as sessoes): "#1xx nome (estilo): PASSA|REPROVADA, win rate, R por trade, trades/semana"
e no fim -b "Demo: o que cada conta (Swing/Day trade/Scalping) corre agora" e -b "Proximo passo". O --log fim vai para o Telegram.

LIMITE REDUZIDO (pedido do Antonio, 2026-11-23, uso semanal a 50%): ate ao fim da semana o limite e 10 ideias por noite (nao 20) e
3 por sessao; so correm as sessoes das :00 (as das :30 estao desligadas). Gasta pouco: nada de reler ficheiros grandes sem necessidade.
CONTAGEM DO LIMITE DA NOITE (corrigido 2026-11-23; SUBSTITUI o "conta as entradas de hoje" do prompt): a noite vai das 19:00 as 07:00.
Conta SO as seccoes do agente ("cripto - sessao ...") registadas desde as 19:00 da noite atual (se agora e antes das 07h, desde as 19:00
de ontem). As seccoes "(Claude, ...)" feitas no chat com o Antonio NAO contam. Na noite de 22-11 o agente parou todas as sessoes por
contar mal (contou as ideias da madrugada e as do chat): nao repetir.

## MISSAO NOTURNA ATUAL (pedido do Antonio, 2026-11-19): PEGAR NO MELHOR TESTE, PERCEBER O QUE FALHA, MELHORAR E ABRIR MAIS TRADES
1. No inicio de CADA sessao: `python best.py`. O 1.o da lista (pontuacao = win rate + % total acumulado + melhor ano, a mesma
   do painel Backtesting > Carteiras) e a BASE. `python best.py --label Kn` mostra o diagnostico de qualquer carteira.
2. Le o diagnostico e escreve no IDEAS.md, ANTES de correr, o que falha na base (por moeda, por ano, por duracao das trades,
   dias sem trade) e 4 variantes NOVAS da base, cada uma com UMA mudanca e a hipotese de porque melhora.
3. Obrigatorio em cada sessao: pelo menos 2 das 4 variantes tem de ABRIR MAIS TRADES (o Antonio quer 2-3 por semana; a base
   faz ~0.3-0.6/semana e reprova por < 60 trades por moeda). Caminhos com fundamento: reentrada quando a tendencia continua
   depois de uma saida, timeframe mais curto (4h/1h) com o mesmo filtro de regime, 2.a estrategia pouco correlacionada na
   mesma carteira (ideias separadas com virgula no --ideas), entradas em recuo dentro da tendencia alem da rutura,
   menos filtros que cortam trades. As outras 2 atacam o que o diagnostico mostra (ex.: perdas em trades de 1-7 dias, ano negativo).
4. Corre cada variante com `--push --nota "#1xx (base Kn): o que muda"` -> carteira nova no painel. No `--log teste` compara
   SEMPRE com a base: win rate, % total, melhor ano, pior ano, trades/semana (antes -> depois) e "O que aprendemos".
5. Se uma variante tiver pontuacao maior que a base, passa a ser a base da sessao seguinte (o best.py faz isso sozinho).
   Melhor pontuacao NAO e aprovacao: so vai ao pre e ao holdout quem passar o criterio oficial (>= 60 trades por moeda, etc.).
6. No `--log fim`: base usada, o que falhava, o que melhorou (numeros antes -> depois), nova base e proximo passo.
Os limites e proibicoes de baixo continuam (4 ideias por sessao, 20 por noite, parametros fixos, registar antes de correr,
nada de grelhas, nada de afinar depois do pre/holdout).

## MISSAO ANTERIOR (2026-11-18): AUMENTAR O WIN RATE SEM MATAR O RESULTADO
O Antonio quer win rate alto E bom resultado, e NAO quer anos muito negativos (prioridade: pior ano o mais perto possivel de 0, nunca abaixo de -10%). Objetivo de uma carteira cripto: win rate >= 50%, positiva em 2019-2024 e em 2017-2018,
pior ano > -10%, pior mes > -5%, e o mais % ao ano possivel com 1% de risco por trade. Estuda, testa, analisa o porque, e volta a testar
com variantes NOVAS registadas antes de correr. Caminhos com fundamento (escolhe e justifica no IDEAS.md):
- saidas: alvo parcial/tempo maximo/stop movido para breakeven (mede o efeito no win rate E no R por trade; reportar os dois sempre);
- entradas em tendencia mas com recuo (compra em pullback dentro da tendencia da K1 em vez de na rutura), filtros de regime
  (BTC acima da media de 200 dias, volatilidade), confirmacao entre moedas;
- menos custos por trade: menos trades com alvos maiores (custo ~0.57% ida e volta; uma ideia com ganho medio < 1% nunca sobrevive).
Regras para isto nao virar procurar sorte: no maximo 4 ideias por sessao e 20 por noite (pedido do Antonio: mais testes; ha sessoes as :00 e as :30) (variantes contam como ideias), parametros
fixos (nada de grelhas), cada ideia escrita em IDEAS.md com hipotese ANTES de correr e commit desse registo primeiro; nunca afinar
depois de ver o pre ou o holdout; no SUMMARY.md diz quantas ideias cripto ja foram testadas no total (mais testes = mais desconfianca).
Proibido: martingale, sem stop, grid, alavancagem, mexer em custos/periodos/criterio, usar dados de 2025-2026 fora do holdout unico.
Diario: `python sync.py --log teste "#100 nome: PASSA|REPROVADA" -b "BTC +0.10R/80 trades, ETH ..., SOL ..." -b "Win rate 58% (antes 25%)"
-b "% ao ano da carteira e pior ano" -b "O que aprendemos: ..."`. Fala sempre em % da conta (1R = 1%) e da sempre o WIN RATE.
No fim: `--log fim` com o que passou, o melhor win rate com resultado positivo e o proximo passo.
Ignora tudo o que, no texto abaixo, fala de NQ/MNQ/futuros/indices/portfolio.py: e historico. As regras de protocolo, diario e commits continuam.

# Bottrading: pesquisa de suporte e resistencia (backtest)

Projeto do Antonio. Objetivo: descobrir se alguma regra MECANICA de suporte/resistencia tem edge real
nos indices americanos (NQ, S&P 500, Dow) em CFDs, DEPOIS de custos. So backtest: nada de MT5,
nada de broker, nada de chaves. O MT5 (conta demo STARTRADER) so entra no PC do Antonio e so
para uma variante que tenha passado o holdout.

DECISAO DO ANTONIO (2026-11-18): vai operar FUTUROS (micro: MNQ primeiro; MES/MYM so como confirmacao), NAO CFDs nem MT5.
O veredicto oficial passa a usar custos de micro-futuros (run_swing.py --custos fut, por defeito; portfolio.py --custos fut).
Tamanho de conta assumido ate o Antonio dizer outro: 50 000 USD -> 1% = 500 USD -> 1 MNQ (2 USD/ponto) so cabe se o stop
mediano no NQ for <= 250 pontos. run_swing.py mostra o stop mediano e a conta minima: uma ideia que passe mas precise de
conta maior fica "PASSA mas nao cabe em MNQ" (regista isso; nunca aumentar o risco para a fazer caber).
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
dos EUA em 2012-2018 e em 2019-2024. Carteira de referencia atual (C20, 2026-11-18, futuros): so NQ (MNQ) com rsi2-dip-d + ibs-dip-d + down3-d + ibs-bear-d + double7-d,
regras de risco OBRIGATORIAS (portfolio.py --max-open 3 --region-cap 1 --month-stop 3 --custos fut): no maximo 3 trades abertas,
1 por indice, 1 por regiao, paragem mensal a -3%. Resultado 2012-2025: +2.6%/ano, 0/14 anos >= 14%, pior mes -1.7%,
pior ano -1.5%, pior queda -3.0%, ~31 trades/ano. Com 10 indices e futuros (C14) da +1.8%/ano com pior queda -20%.
ERRO CORRIGIDO a 2026-11-18: C1-C10 (incluindo os +12.5%/ano da C5 e o holdout C9) contavam trades sobrepostas no mesmo
indice no mesmo dia; os numeros antigos estao inflacionados e as comparacoes "carteira + ideia" tem de ser refeitas.
Bot da conta demo: live/c5_live.py (corre no PC do Antonio); tests/test_live.py obriga-o a decidir igual ao backtest.
O Antonio quer CONSISTENCIA (meses sem quedas grandes) tanto como os 14%/ano: compara sempre pior mes e pior ano.
So substituis o estado "portfolio" do dashboard por uma carteira MELHOR (mais % ao ano ou mais anos >= 14%);
nunca o apagues nem o troques por uma carteira vazia. No fim de cada sessao corre portfolio.py com as ideias aceites e diz no
SUMMARY.md e no --log fim quanto da (% ao ano, anos acima de 14%) e quanto falta. Nunca chegar la aumentando o risco por trade.
FREQUENCIA (pedido do Antonio): a carteira deve fazer em media 2 a 3 trades por semana (~100-150 por ano). Da prioridade
a ideias com mais trades (4h, 1h, sinais mais frequentes), sempre com as mesmas regras de validacao.

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
  Testes de carteira levam numero do catalogo: `--label C9` envia para o dashboard como carteira extra (nao toca na referencia);
  `--label C9 --ref` substitui a carteira de referencia (so se for MELHOR). O doc inclui a lista de trades (calendario do dashboard).
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
3. FOCO ATUAL (2026-11-18): ideias em 1h e 4h (e 15m com razao forte) com STOPS PEQUENOS que caibam em 1 MNQ a 1% (ver acima),
   mais trades por semana, NQ primeiro. As ideias diarias com stop de 3 ATR diario nao cabem numa conta normal.
   FOCO ANTERIOR (decidido a 2026-11-16 depois de tudo em 1m/5m dar ~0R antes de custos): ideias de PRAZO MAIS LONGO,
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
5. Atualiza `SUMMARY.md`: catalogo numerado do que passou/reprovou e a tua leitura honesta, em 10 linhas.
   CATALOGO (pedido do Antonio, 2026-11-18): cada teste de estrategia recebe o numero seguinte (#40, #41, ...) e cada
   teste de carteira o seguinte C (C9, C10, ...), sempre com a data. Os numeros nunca mudam. Usa o numero no titulo do
   `--log teste` (ex.: "#40 nome: REPROVADA, t junto +0.5"), no TODO e no commit.
6. Commit + push para `research`; se nao houver PR aberto de research -> main, abre um.
