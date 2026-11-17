# Ideias do agente

Registo de ideias criadas pelo agente no modo ideias (ver CLAUDE.md). Cada ideia e registada aqui ANTES de ser testada.

## 2026-11-16 - sessao 1 (3 ideias; total de ideias do agente ate agora: 3)

### Ideia 1 - `gapfill-pdc`: fade do gap de abertura ate ao fecho anterior
- Hipotese: o movimento overnight (Globex) acontece com pouca liquidez; quando o mercado a vista abre (09:30 NY)
  entra liquidez institucional e os gaps PEQUENOS tendem a ser parcialmente revertidos ("gap fill"), um efeito
  documentado nos futuros de indices. Gaps grandes (noticias) tendem a continuar, por isso ficam de fora.
- Nivel `pdc`: fecho RTH do dia anterior (fecho da vela das 15:55), activo a partir das 16:00.
- Entrada: na abertura da vela das 09:30, se 0.10% <= |abertura - pdc| / pdc <= 0.60%, entra CONTRA o gap
  (gap para cima -> short; gap para baixo -> long). Uma trade por dia no maximo.
- Alvo: o pdc (gap totalmente fechado). Stop: a mesma distancia do gap para la da entrada (1:1, ou seja 1R).
- Saida: alvo, stop ou fecho da sessao RTH (15:55). Sessao rth. Parametros fixos (0.10%, 0.60%, stop 1x gap).
- Comando: `python run.py --play gapfill --levels pdc`

### Ideia 2 - `fake-onhl`: falso rompimento da maxima/minima overnight
- Hipotese: a maxima e a minima da sessao overnight (18:00-09:30) sao niveis muito vigiados; ha stops acumulados
  logo para la delas. Nas primeiras horas RTH o preco varre esses stops e, se nao houver procura real, volta para
  dentro (liquidity sweep). Diferente do historico "sweep de sessao + FVG" (que exigia FVG e nao deu sinais):
  aqui e so o falso rompimento, sem FVG.
- Nivel `onhl`: maxima e minima das velas de 18:00 (dia anterior) ate 09:25, activas a partir das 09:30.
- Entrada/stop/alvo: jogada `fake` existente com os parametros por defeito (passa >= 0.3 ATR e fecha de volta,
  entra contra na abertura seguinte, stop no extremo + 0.1 ATR, alvo 2R), sessao rth.
- Comando: `python run.py --play fake --levels onhl`

### Ideia 3 - `break-nr4`: rompimento da maxima/minima do dia anterior so apos um dia NR4
- Hipotese: compressao de volatilidade antecede expansao (clustering de volatilidade; padrao NR4 de Toby Crabel).
  O rompimento do dia anterior em geral falhou (break-pdhl t -4.55), mas depois de um dia estreito a probabilidade
  de um dia de tendencia e maior.
- Nivel `nr4`: maxima e minima do dia de negociacao anterior (estilo CME, como pdhl), so quando esse dia teve a
  menor amplitude dos ultimos 4 dias (dias com amplitude 0, feriados, ignorados). Nos outros dias nao ha niveis.
- Entrada/stop/alvo: jogada `break` existente com parametros por defeito (tp 2R, stop 0.5 ATR), sessao rth.
- Comando: `python run.py --play break --levels nr4`

## 2026-11-16 - sessao 2 (3 ideias; total de ideias do agente ate agora: 6; hoje: 6 de 8)

### Ideia 4 - `break-lunchhl`: rompimento do intervalo da hora de almoco
- Hipotese: entre as 12:00 e as 13:30 NY a liquidez cai e o preco comprime-se num intervalo. A tarde volta o fluxo
  institucional (e os desequilibrios do fecho), e a saida desse intervalo comprimido tende a ter seguimento
  (compressao -> expansao). Diferente do opening range (ja testado): e um intervalo do meio do dia.
- Nivel `lunchhl`: maxima e minima das velas das 12:00 ate a vela das 13:25 (RTH), activas a partir das 13:30.
- Entrada/stop/alvo: jogada `break` existente, parametros por defeito (tp 2R, stop 0.5 ATR), sessao rth.
- Comando: `python run.py --play break --levels lunchhl`

### Ideia 5 - `gapgo-pdc`: seguir os gaps de abertura GRANDES
- Hipotese (ja escrita na ideia 1, antes de qualquer resultado): gaps grandes vem de noticias/reavaliacao e tendem
  a continuar em vez de fechar; o mercado a vista confirma a reavaliacao overnight.
- Nivel `pdc` (fecho RTH anterior). Entrada na abertura da vela das 09:30 se |abertura - pdc| / pdc > 0.60%,
  A FAVOR do gap. Stop: metade do gap para tras da entrada (risco = 0.5 x gap). Alvo 2R. Saida no fim da sessao RTH.
  Uma trade por dia. Parametros fixos (0.60%, 0.5 x gap, 2R).
- Comando: `python run.py --play gapgo --levels pdc`

### Ideia 6 - `break-monhl`: rompimento do intervalo de segunda-feira
- Hipotese: a segunda-feira define o "balanco inicial" da semana (posicionamento depois do fim de semana); um
  rompimento desse intervalo mais tarde na semana sinaliza que um lado ganhou e tende a ter seguimento.
  Diferente de pwhl (semana anterior) e pdhl (dia anterior).
- Nivel `monhl`: maxima e minima RTH (09:30-16:00) da segunda-feira, activas de terca as 09:30 ate sexta.
  Se segunda for feriado (sem amplitude), nao ha niveis nessa semana.
- Entrada/stop/alvo: jogada `break` existente, parametros por defeito (tp 2R, stop 0.5 ATR), sessao rth.
- Comando: `python run.py --play break --levels monhl`

## 2026-11-16 (registadas pelo Claude ao mudar o foco para prazo mais longo; corridas uma vez, sem afinar)
- **trend-sma100-d** (diario): long acima da media de 100 dias, fora abaixo. Hipotese: tendencia de medio prazo
  nos indices (literatura de trend following). Stop 3 ATR(14), sem alvo.
- **rsi2-dip-d** (diario): long quando RSI(2) < 10 e fecho > media de 200 dias; sai quando fecha acima da media de 5.
  Hipotese: compra de quedas curtas em tendencia de alta (Connors). Stop 3 ATR, max 10 dias.
- **donchian20-d** (diario): rutura de 20 dias long/short, saida no canal de 10 (tartarugas). Stop 3 ATR.

## 2026-11-16 (Claude, a pedido do Antonio: mais trades, 2-3 por semana) - registadas antes de correr
- **rsi2-dip-4h** (4h): RSI(2) < 10 e fecho > media de 200 velas -> long; sai acima da media de 5. Stop 3 ATR, max 30 velas.
- **ibs-dip-d** (diario): IBS < 0.2 e fecho > media de 200 dias -> long; sai com IBS > 0.7. Stop 3 ATR, max 10 dias.
- **down3-d** (diario): 3 fechos seguidos em queda, acima da media de 200 -> long; sai ao fechar acima do maximo anterior.

## 2026-11-17 - sessao 1 (3 ideias; total de ideias do agente ate agora: 15; hoje: 3 de 8) - registadas antes de correr
Objetivo: mais trades por ano e POUCO correlacionadas com as compras de quedas (rsi2/ibs/down3). Duas sao efeitos de
calendario/horario documentados na literatura (nao dependem de olhar para graficos), a terceira e outra forma de comprar quedas.
Parametros fixos, sem grelhas. Criterio oficial: run_swing.py (>= 60 trades por indice, meanR > 0 nos 3, t junto >= 3.0, CFD).

### Ideia 13 - `tom-d`: efeito de viragem do mes (turn of the month)
- Hipotese: os indices sobem mais no ultimo dia util do mes e nos 3 primeiros do mes seguinte (entradas de salarios,
  planos de pensoes e fundos que investem no inicio do mes; Lakonishok-Smidt 1988, McConnell-Xu 2008). Nao depende de quedas.
- Entrada: long na abertura do ultimo dia util do mes (sinal no fecho do dia anterior, calendario de dias uteis seg-sex,
  conhecido com antecedencia; sem calendario de feriados).
- Saida: no fecho do 3.o dia util do mes seguinte. Stop 3 ATR(14) diario, sem alvo, max 6 dias.
- Timeframe: diario (dia CME). Long-only. ~12 trades por ano por indice.

### Ideia 14 - `overnight-us-1h`: deriva da noite nos indices dos EUA
- Hipotese: quase todo o retorno historico das acoes dos EUA acontece entre o fecho e a abertura (Cliff-Cooper-Gulen
  "Return differences between trading and non-trading hours"; Lou-Polk-Skouras 2019 "A tug of war"). Comprar ao fecho
  e vender a abertura captura isso. Muitas trades (~250 por ano por indice); risco: financiamento de 1 noite do CFD.
- Entrada: long na abertura da vela de 1h das 16:00 NY (sinal no fecho da vela das 15:00).
- Saida: no fecho da vela das 08:00 NY (09:00), antes da abertura do cash. Stop 3 ATR(14) de 1h, sem alvo, max 24 velas.
- Timeframe: 1h, horas de Nova Iorque: so faz sentido para NQ/S&P/Dow (nao entra na carteira de outros indices).

### Ideia 15 - `double7-d`: comprar o minimo de 7 dias em tendencia de alta
- Hipotese: reversao de curto prazo em indices em tendencia (Connors "Double 7s"): um fecho no minimo de 7 dias
  acima da media de 200 tende a recuperar. Outra forma de comprar quedas (pedido no CLAUDE.md), sinal diferente do RSI/IBS.
- Entrada: long na abertura seguinte quando o fecho e o mais baixo dos ultimos 7 fechos e fecho > media de 200 dias.
- Saida: quando o fecho e o mais alto dos ultimos 7 fechos. Stop 3 ATR(14), sem alvo, max 10 dias.
- Timeframe: diario. Long-only.
- Nota de implementacao (antes de correr): como em todas as ideias do motor, se o stop for tocado e o sinal continuar
  ligado, o motor volta a entrar na vela seguinte (overnight: na mesma noite; tom-d: dentro da mesma janela). E raro com stop de 3 ATR.
