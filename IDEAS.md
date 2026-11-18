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

## 2026-11-17 - sessao 2 (3 ideias; total de ideias do agente ate agora: 18; hoje: 6 de 8) - registadas antes de correr
Objetivo: sinais DIFERENTES das compras de quedas por RSI/IBS (a carteira precisa de trades pouco correlacionadas).
Uma e de calendario (opcoes), uma de volatilidade e uma de reversao semanal (horizonte diferente). Parametros fixos, sem grelhas.
Criterio oficial: run_swing.py (>= 60 trades por indice, meanR > 0 nos 3, t junto >= 3.0, CFD). Depois `--period pre` como confirmacao.
Nota de dados: as velas diarias tem uma vela de domingo (fim de semana, precos parados). Os sinais de semana/NR7 sao
calculados so com velas de segunda a sexta; a vela de domingo herda a posicao de sexta.

### Ideia 16 - `opex-week-d`: semana de vencimento das opcoes mensais
- Hipotese: os indices dos EUA sobem mais na semana que acaba na 3.a sexta-feira do mes (vencimento mensal de opcoes).
  Explicacao conhecida: os market makers, longos em opcoes, recompram a cobertura a medida que o vencimento se aproxima
  (Stivers & Sun 2013, "Returns and option activity over the option-expiration week"). Calendario, nao depende de quedas.
- Entrada: long na abertura do 1.o dia util da semana de vencimento (sinal no fecho do dia anterior; calendario seg-sex).
- Saida: no fecho da 3.a sexta-feira do mes. Stop 3 ATR(14) diario, sem alvo, sem max (a janela tem 5 dias).
- Timeframe: diario. Long-only. ~12 trades por ano por indice.

### Ideia 17 - `nr7-up-d`: dia mais estreito de 7 em tendencia de alta
- Hipotese: depois de um dia de amplitude muito pequena (o mais estreito dos ultimos 7, NR7) a volatilidade volta a subir
  (Crabel 1990); em tendencia de alta (fecho > media de 200) a expansao tende a ser para cima. Sinal de calma, nao de queda.
- Entrada: long na abertura seguinte quando a amplitude do dia e menor que a de cada um dos 6 dias anteriores e fecho > media de 200.
- Saida: no fecho do 5.o dia de semana depois do sinal (um novo NR7 prolonga a janela). Stop 3 ATR(14), sem alvo.
- Timeframe: diario. Long-only.

### Ideia 18 - `week-rev-d`: reversao semanal
- Hipotese: reversao de curto prazo ao horizonte de 1 semana (Lehmann 1990, Jegadeesh 1990): depois de uma semana em
  queda, em tendencia de alta (fecho > media de 200), a semana seguinte tende a ser positiva. Horizonte diferente do RSI(2)/IBS (diario).
- Entrada: no fecho de sexta, se o fecho de sexta < fecho do ultimo dia da semana anterior e fecho > media de 200,
  long na abertura seguinte. Saida no fecho da sexta seguinte (se a condicao se repetir, mantem). Stop 3 ATR(14), sem alvo.
- Timeframe: diario. Long-only. ~15-20 trades por ano por indice.

## 2026-11-17 - sessao 3 (1 ideia; total de ideias do agente ate agora: 19; hoje: 7 de 8) - registada antes de correr
Objetivo: a carteira so tem compras (long) de quedas; os meses maus sao quedas em tendencia (2020, 2022).
Uma ideia do lado VENDEDOR, so em tendencia de baixa, daria trades pouco correlacionadas. So 1 ideia nesta sessao
(nao ha outra com hipotese forte e trades suficientes; nao vale a pena gastar o limite).
Verificacao de frequencia (contagem de sinais, sem olhar a resultados): a versao diaria teria ~20 sinais por indice
em 2019-2024 (< 60, nao pode passar), por isso regista-se so a versao 4h (~200 sinais por indice).

### Ideia 19 - `rsi2-pop-short-4h`: vender subidas curtas em tendencia de baixa (4h)
- Hipotese: em tendencia de baixa as subidas curtas e fortes (short covering, "bear market rallies") tendem a falhar e
  o preco volta a cair (reversao de curto prazo, espelho do Connors RSI(2) do lado curto). Diversifica a carteira
  (so vende quando os indices estao abaixo da media longa, que e quando as compras de quedas perdem).
- Expectativa honesta: baixa. A versao long em 4h (rsi2-dip-4h) deu ~0R e os indices tem deriva para cima.
- Entrada: short na abertura da vela seguinte quando RSI(2) > 90 e fecho < media de 200 velas de 4h.
- Saida: quando o fecho fica abaixo da media de 5 velas. Stop 3 ATR(14) de 4h, sem alvo, max 30 velas.
- Timeframe: 4h, todas as sessoes. Short-only. Parametros fixos (os mesmos do rsi2-dip-4h, espelhados).

## 2026-11-17 - sessao 4 (1 ideia; total de ideias do agente ate agora: 20; hoje: 8 de 8) - registada antes de correr
Objetivo: a carteira so compra quedas ACIMA da media de 200 dias; quando os indices estao abaixo dela fica parada
(2020, 2022). Uma compra de quedas so ABAIXO da media de 200 da trades noutros meses (pouco correlacionadas por construcao).
Verificacao de frequencia (contagem de sinais, sem olhar a resultados, dev 2019-2024): RSI(2) < 10 abaixo da media
de 200 da ~28 sinais por indice (pouco); IBS < 0.2 abaixo da media de 200 da 50 (NQ), 57 (S&P), 63 (Dow).
Regista-se a versao IBS, com os MESMOS parametros do ibs-dip-d (so muda o lado da media). Fica abaixo de 60 trades no NQ,
por isso quase de certeza nao passa no criterio oficial; so pode entrar na carteira pela outra regra do CLAUDE.md
(positiva nos 3 dos EUA em 2012-2018 e em 2019-2024). Se nao for, fica reprovada.

### Ideia 20 - `ibs-bear-d`: comprar quedas curtas em tendencia de BAIXA
- Hipotese: a reversao de curto prazo e mais forte quando a volatilidade e alta, porque quem da liquidez exige mais
  premio (Nagel 2012, "Evaporating liquidity"; Avramov-Chordia-Goyal 2006). Abaixo da media de 200 a volatilidade e alta,
  por isso um fecho perto do minimo do dia (IBS baixo) deve recuperar no(s) dia(s) seguinte(s). Risco conhecido:
  quedas em cascata (marco 2020); o stop de 3 ATR limita.
- Entrada: long na abertura seguinte quando IBS < 0.2 e fecho < media de 200 dias.
- Saida: quando IBS > 0.7. Stop 3 ATR(14), sem alvo, max 10 dias.
- Timeframe: diario. Long-only. Parametros fixos (iguais ao ibs-dip-d).

## 2026-11-18 - sessao 1 (1 ideia; total de ideias do agente ate agora: 21; hoje: 1 de 8) - registada antes de correr
Objetivo: mais trades por semana com um mecanismo diferente das compras de quedas por IBS/RSI (horizonte de 1 dia,
ancorado no dia da semana). So 1 ideia nesta sessao: as outras que pensei (IBS/RSI em 4h, quedas grandes, dias antes
de feriados) ou repetem o que ja deu ~0R ou tem trades a menos; nao vale a pena gastar o limite.
Verificacao de frequencia (contagem de sinais, sem olhar a resultados, dev 2019-2024): segunda-feira a fechar abaixo
de sexta da ~115 (NQ), 120 (S&P), 131 (Dow) sinais; com filtro de media de 200 so 67-85. Regista-se SEM filtro de
tendencia (mais trades e e nas fases de volatilidade alta que a reversao e mais forte, Nagel 2012).

### Ideia 21 - `turnaround-tue-d`: comprar a terca depois de uma segunda em queda
- Hipotese: efeito de segunda-feira / "turnaround Tuesday" (French 1980; Abraham & Ikenberry 1994: a segunda tende a
  ser fraca e, quando cai, a terca recupera; vendas de pequenos investidores a segunda, depois revertidas).
  Horizonte de 1 dia, ancorado no calendario: deve dar trades em semanas diferentes das do IBS/RSI(2).
- Expectativa honesta: baixa a media. Efeitos de calendario ja testados (tom-d, opex-week-d) deram ~0R em 2019-2024.
- Entrada: no fecho de segunda (dia CME, seg-sex), se fecho de segunda < fecho de sexta -> long na abertura seguinte.
- Saida: no fecho de terca (posicao so durante 1 dia). Stop 3 ATR(14) diario, sem alvo.
- Timeframe: diario. Long-only. Sem filtro de tendencia. Parametros fixos (stop igual as outras ideias diarias).

## 2026-11-18 - sessao 2 (1 ideia; total de ideias do agente ate agora: 22; hoje: 2 de 8) - registada antes de correr
Objetivo: um sinal de compra que NAO coincida com os da carteira. Todas as compras atuais (RSI(2), IBS, down3, IBS abaixo
da media) entram quando o dia FECHA FRACO. Esta entra quando o dia fecha FORTE depois de um novo minimo (dia de reversao),
por isso a sobreposicao com a carteira deve ser pequena. So 1 ideia: as outras que pensei (Bollinger sem filtro ~22-27
sinais, conjuntos de IBS/RSI em 4h, overnight condicionado) ou tem trades a menos ou repetem o que ja deu ~0R.
Verificacao de frequencia (contagem de sinais, sem olhar a resultados, dev 2019-2024): 54 (NQ), 58 (S&P), 58 (Dow);
com filtro de media de 200 so 30-38. Regista-se SEM filtro de tendencia. Fica abaixo de 60 trades, por isso quase de
certeza nao passa no criterio oficial; so pode entrar na carteira pela outra regra do CLAUDE.md (positiva nos 3 dos EUA
em 2012-2018 e em 2019-2024) e se melhorar a carteira. Se nao, fica reprovada.

### Ideia 22 - `keyrev-d`: dia de reversao depois de um novo minimo de 10 dias
- Hipotese: um dia que faz um minimo novo de 10 dias (vendas forcadas / stops) mas fecha ACIMA do fecho anterior mostra
  que os compradores absorveram a venda (capitulacao seguida de procura; padrao "key reversal" classico, e o premio de
  liquidez de Nagel 2012 pago a quem compra nas vendas forcadas). Espera-se continuacao para cima nos dias seguintes.
- Expectativa honesta: baixa a media. Padroes de velas tem pouca evidencia academica; poucas trades.
- Entrada: no fecho do dia d (dia CME, so seg-sex), se minimo(d) < minimo dos 10 dias anteriores e fecho(d) > fecho(d-1)
  -> long na abertura seguinte.
- Saida: no fecho do 5.o dia de semana depois do sinal (um novo sinal prolonga a janela). Stop 3 ATR(14) diario, sem alvo.
- Timeframe: diario. Long-only. Sem filtro de tendencia. Parametros fixos (stop igual as outras ideias diarias).

## 2026-11-18 - sessao 3 (1 ideia; total de ideias do agente ate agora: 23; hoje: 3 de 8) - registada antes de correr
Objetivo: a carteira compra quedas de 1-3 dias (RSI(2), IBS, down3). Nos anos de subida forte e calma (2017, 2021, 2023-24)
essas quedas curtas quase nao aparecem. Esta ideia compra recuos de 1-3 SEMANAS dentro de uma tendencia forte (horizonte mais
longo, outro momento de entrada). So 1 ideia: as outras que pensei (vender subidas em baixa no diario, dias antes de feriados,
fim de mes por rebalanceamento de fundos) ou repetem algo que deu negativo ou tem trades a menos.
Verificacao de frequencia (contagem de sinais, sem olhar a resultados, dev 2019-2024): fecho a cruzar abaixo da media de 20
com medias alinhadas da 46 (NQ), 45 (S&P), 48 (Dow); a versao com a media de 50 da 37-40. Regista-se a versao da media de 20
(mais trades). Fica abaixo de 60 trades, por isso quase de certeza nao passa no criterio oficial; so pode entrar na carteira
pela outra regra do CLAUDE.md (positiva nos 3 dos EUA em 2012-2018 e em 2019-2024) e se melhorar a carteira. Se nao, reprovada.

### Ideia 23 - `pullback20-d`: comprar o recuo a media de 20 dias numa tendencia forte
- Hipotese: momentum de serie temporal (Moskowitz, Ooi & Pedersen 2012): tendencias fortes tendem a continuar; um recuo
  ate a media de 20 dias com as medias alinhadas (20 > 50 > 200) e uma pausa (realizacao de lucros), nao uma inversao.
  Comprar o recuo da melhor relacao risco/retorno do que comprar a rutura (donchian20-d deu ~0R).
- Expectativa honesta: baixa a media. Seguir tendencias com CFDs deu Sharpe ~0 (historico); aqui so long e trades curtas.
- Entrada: no fecho do dia d (dia CME, so seg-sex), se fecho(d) < media20(d) e fecho(d-1) >= media20(d-1) e
  media20 > media50 > media200 -> long na abertura seguinte.
- Saida: no primeiro fecho acima do maior fecho dos 10 dias anteriores (a tendencia retomou). Stop 3 ATR(14) diario,
  sem alvo, maximo 20 dias.
- Timeframe: diario. Long-only. Parametros fixos (stop igual as outras ideias diarias; 10 e 20 dias sao os valores
  classicos, nao afinados).

## 2026-11-18 - sessao 4 (1 ideia; total de ideias do agente ate agora: 24; hoje: 4 de 8) - registada antes de correr
Objetivo: todas as compras da carteira entram em QUEDAS; nas subidas calmas a carteira fica parada. Esta ideia entra
precisamente nesses dias (novo maximo de 10 dias com volatilidade baixa), por isso a sobreposicao e quase nula.
So 1 ideia: a outra que pensei (comprar depois de um dia de choque, amplitude > 2x ATR a fechar em queda) da 51-93
sinais mas 70-80% coincidem com dias em que a carteira ja esta comprada; nao acrescenta nada.
Verificacao de frequencia e sobreposicao (contagem de sinais, sem olhar a resultados, dev 2019-2024): 86 (NQ), 105 (S&P),
88 (Dow); so 2-3% dos sinais caem em dias em que rsi2-dip-d/ibs-dip-d/down3-d/ibs-bear-d estao em posicao.
Diferente do donchian20-d (reprovado): so long, so em tendencia de alta (media de 200) e volatilidade baixa, saida por tempo.

### Ideia 24 - `calmhigh-d`: comprar um novo maximo de 10 dias numa subida calma
- Hipotese: momentum de serie temporal (Moskowitz, Ooi & Pedersen 2012) e retornos geridos pela volatilidade (Moreira &
  Muir 2017: com volatilidade baixa o retorno por unidade de risco dos indices e maior). Um maximo novo numa subida calma
  vem de compra continua (fundos, recompras), nao de um pico de fecho de shorts, e tende a continuar alguns dias.
- Expectativa honesta: baixa. Nos indices o curto prazo costuma reverter (por isso as compras de quedas funcionam);
  donchian20-d deu ~0R.
- Entrada: no fecho do dia d (dia CME, so seg-sex), se fecho(d) > maior fecho dos 10 dias anteriores e fecho(d-1) nao o era
  (primeiro dia do maximo novo), fecho(d) > media de 200 dias, e media do true range de 5 dias < media do true range de 50
  dias -> long na abertura seguinte.
- Saida: no fecho do 5.o dia de semana depois do sinal (um novo sinal prolonga a janela). Stop 3 ATR(14) diario, sem alvo.
- Timeframe: diario. Long-only. Parametros fixos (10 dias e 5 dias iguais as ideias anteriores; 5/50 sao a medida curta/longa
  de volatilidade mais comum; stop igual as outras ideias diarias).

## 2026-11-18 - sessao 5 (1 ideia; total de ideias do agente ate agora: 25; hoje: 5 de 8) - registada antes de correr
Objetivo (TODO: modo ideias com foco 1h/4h): um sinal em 1h que NAO dependa do preco, para nao coincidir com as compras
de quedas da carteira, e com stops de 1h (cabem num MNQ). Efeitos de CALENDARIO conhecidos com antecedencia.
So 1 ideia nesta sessao (outra sessao correu C14-C20 em paralelo; nao quero gastar o limite da noite).
Verificacao de frequencia (contagem de sinais, sem olhar a resultados): dev 2019-2024: 104 (NQ), 104 (S&P), 104 (Dow);
2012-2018: 118, 118, 90 (os dados do Dow comecam mais tarde).
Diferente do tom-d (viragem do mes, reprovado) e do overnight-us-1h (todas as noites, reprovado): so ~17 janelas por ano,
ligadas a eventos especificos.

### Ideia 25 - `fomc-holiday-1h`: long antes do FOMC e na vespera de feriados
- Hipotese: (a) deriva antes do FOMC (Lucca & Moench 2015, Journal of Finance): o S&P subiu em media ~0.5% nas 24h antes
  do comunicado programado do FOMC (1994-2011), explicado por premio de risco antes do anuncio; (b) efeito vespera de
  feriado (Ariel 1990; Lakonishok & Smidt 1988): o ultimo dia de bolsa antes de um feriado rende varias vezes um dia normal
  (fecho de posicoes curtas, otimismo, pouca oferta). Os dois juntos dao ~17 trades por ano por indice.
- Expectativa honesta: baixa a media. A deriva pre-FOMC enfraqueceu depois de 2015 (estudos posteriores) e o efeito
  vespera de feriado tambem diminuiu desde que foi publicado.
- Entrada: (a) long as 14:00 NY do dia de bolsa anterior ao comunicado do FOMC (sinal no fecho da vela de 1h das 13:00);
  (b) long as 16:00 NY do dia anterior a vespera de feriado da NYSE (sinal no fecho da vela das 15:00).
- Saida: (a) as 14:00 NY do dia do comunicado (antes do anuncio); (b) as 16:00 NY da vespera do feriado. Stop 3 ATR(14) de 1h,
  sem alvo.
- Datas: reunioes PROGRAMADAS do FOMC 2012-2026 (lista fixa em sr/swing_ideas.py); feriados da NYSE por regras fixas
  (Ano Novo, MLK, Presidents, Sexta-feira Santa, Memorial, Juneteenth desde 2022, 4 de julho, Labor, Thanksgiving, Natal).
- Timeframe: 1h, horas de Nova Iorque. Long-only. Parametros fixos (nenhum por afinar; stop igual ao overnight-us-1h).

## 2026-11-18 - sessao 6 (1 ideia; total de ideias do agente ate agora: 26; hoje: 6 de 8) - registada antes de correr
Objetivo (FOCO ATUAL): 1h com stop que caiba em 1 MNQ a 1% e mais trades por semana no NQ.
Pensei tambem em comprar a abertura europeia (02:00-04:00 NY) depois de um dia de queda nos EUA ("overnight drift",
Boyarchenko, Larsen & Whelan 2023), mas os proprios autores (Liberty Street Economics, julho de 2026, "The Disappearing
Overnight Drift") mostram que o efeito desapareceu desde 2021 no S&P, Nasdaq e Dow; o nosso dev e 2019-2024. Nao a registo
(seria gastar um teste numa ideia que ja se sabe morta) e o overnight-us-1h ja reprovou.
Verificacao de frequencia (contagem de sinais, sem olhar a resultados): dev 2019-2024: 327 (NQ), 320 (S&P), 286 (Dow);
2012-2018: 561, 544, 339. Stop mediano no NQ (dev) ~128 pontos = ~256 USD por MNQ: cabe numa conta de 50 000 USD.
Sobreposicao: ~44% dos dias de sinal no NQ caem em dias em que a carteira diaria (C20) ja esta comprada (com 1 trade por
indice isso tira algumas trades a uma das duas).

### Ideia 26 - `flush-1h`: comprar uma vela de 1h de queda violenta a meio da sessao, em tendencia de alta
- Hipotese: reversao de curto prazo como pagamento por fornecer liquidez (Nagel 2012, "Evaporating Liquidity"; Grossman &
  Miller 1988): uma hora de venda forcada (stops, margens, ordens grandes) empurra o preco para baixo do valor e quem compra
  e pago com uma recuperacao parcial nas horas seguintes. Em tendencia de alta os vendedores forcados sao a excecao, nao
  o inicio de uma queda. E a mesma logica das compras de quedas diarias que funcionam (ibs-dip-d, rsi2-dip-d), em 1h.
- Expectativa honesta: baixa a media. Em 1m/5m as reversoes junto a niveis nao sobreviveram (#1-#4, #9-#12) e o
  rsi2-dip-4h deu ~0R; a diferenca aqui e exigir uma vela anormal (> 2x ATR) e segurar ~6 horas com stop largo.
- Entrada: no fecho de uma vela de 1h (horas de Nova Iorque) que comeca entre as 10:00 e as 14:00 (sessao cash, sem a
  vela da abertura), se: amplitude (maximo - minimo) > 2 x ATR(14) de 1h, fecho < abertura, fecho no quarto inferior da
  vela ((fecho - minimo) / (maximo - minimo) < 0.25), e fecho > media das ultimas 4600 velas de 1h (~200 dias de
  negociacao, filtro de tendencia). Long na abertura da vela seguinte.
- Saida: no fecho da 6.a vela de 1h depois do sinal (um novo sinal prolonga a janela). Stop 3 ATR(14) de 1h, sem alvo.
- Timeframe: 1h. Long-only. Parametros fixos (2x ATR = vela anormal; 0.25 = quarto inferior, como o IBS < 0.2-0.25
  classico; 6 horas = resto da sessao e inicio da noite; stop igual as outras ideias de 1h).

## 2026-11-18 - sessao 7 (1 ideia; total de ideias do agente ate agora: 27; hoje: 7 de 8) - registada antes de correr
Objetivo (FOCO ATUAL): stops que caibam em 1 MNQ a 1% sem perder a unica vantagem que temos (comprar quedas no diario).
O IBS classico (Pagonidis 2014; estudos em SPY/QQQ) e medido na sessao CASH (09:30-16:00) e a compra e feita ao fecho
das 16:00. O nosso ibs-dip-d (#26) usa o dia CME (18:00-17:00, inclui a noite) e entra as 18:00 com stop de 3 ATR diarios
(1 MNQ precisa de ~120 mil USD). Aqui: o mesmo efeito, medido como na literatura, com stop de 1h.
Verificacao de frequencia (contagem de dias de sinal, sem olhar a resultados): dev 2019-2024: 197 (NQ), 191 (S&P),
183 (Dow); 2012-2018: 200, 204, 142. Stop mediano no NQ (dev) ~139 pontos = ~280 USD por MNQ.
Sobreposicao: alta com ibs-dip-d (mesmo efeito); se passar, entra NO LUGAR do ibs-dip-d no NQ, nao em cima dele.

### Ideia 27 - `ibs-cash-1h`: IBS da sessao cash, comprar ao fecho das 16:00, stop de 1h
- Hipotese: reversao de curto prazo nos indices (fecho perto do minimo do dia -> subida nos dias seguintes), documentada
  na sessao cash; ao medir na sessao cash e entrar ao fecho, o sinal fica mais limpo e o stop de 1h cabe em 1 MNQ.
- Expectativa honesta: media. O efeito diario e real mas pequeno (+0.05 a +0.2R); com stop mais curto (3 ATR de 1h, ~1/2
  do ATR diario) as noites com gap podem tocar o stop mais vezes e comer a vantagem.
- Entrada: no fecho da vela de 1h das 15:00 NY (= 16:00), se IBS da sessao de hoje < 0.2 e fecho > media dos ultimos 200
  fechos das 16:00. Sessao = velas de 1h das 09:00 as 15:00 NY (09:00-16:00; a vela das 09:00 inclui 30 min de
  pre-abertura, aproximacao). Long na abertura da vela das 16:00.
- Saida: no fecho da vela das 15:00 (16:00) de um dia com IBS > 0.7; ou ao fim de 115 velas de 1h (~5 dias). Stop 3 ATR(14)
  de 1h na vela de sinal, sem alvo.
- Timeframe: 1h. Long-only. Parametros fixos (0.2 / 0.7 / media 200 iguais ao ibs-dip-d; stop igual as outras ideias de 1h).

## 2026-11-18 - sessao 8 (1 ideia; total de ideias do agente ate agora: 28; hoje: 8 de 8) - registada antes de correr
Objetivo (FOCO ATUAL): stops que caibam em 1 MNQ a 1%. O #42 (ibs-cash-1h) mostrou que medir o IBS na sessao cash e
comprar as 16:00 com stop de 1h mantem a vantagem do diario no NQ. Aqui faz-se o mesmo ao rsi2-dip-d (#23), cujo stop de
3 ATR diarios tambem nao cabe num MNQ. E a ultima ideia que o limite da noite permite (8 de 8).
Verificacao de frequencia (contagem de sinais, sem olhar a resultados): dias com RSI(2) < 10 acima da media de 200 fechos
das 16:00, dev 2019-2024: 102 (NQ), 112 (S&P), 124 (Dow); entradas novas (primeiro dia de cada sequencia): 63, 63, 61.
2012-2018: 69, 70, 51. Fica perto dos 60 trades: pode reprovar por poucas trades.
Sobreposicao: 56-68% dos dias de sinal caem em dias em que o ibs-cash-1h ja esta comprado (mesmo efeito de reversao).
Se passar, entra NO LUGAR do rsi2-dip-d no NQ, nao em cima dele.

### Ideia 28 - `rsi2-cash-1h`: RSI(2) de Connors nos fechos das 16:00, stop de 1h
- Hipotese: reversao de curto prazo nos indices (Connors & Alvarez 2009, "Short Term Trading Strategies That Work": RSI(2)
  < 10 acima da media de 200 em SPY/QQQ, medido nos fechos da sessao cash). Medir como na literatura e entrar ao fecho
  das 16:00 deve manter a vantagem do rsi2-dip-d com um stop de 1h (~1/2 do ATR diario).
- Expectativa honesta: media a baixa. A vantagem do rsi2-dip-d e pequena (t +0.89 no dev); com stop mais curto as noites
  com gap podem tocar o stop mais vezes. Poucas trades.
- Entrada: no fecho da vela de 1h das 15:00 NY (= 16:00): serie dos fechos das 16:00; se RSI(2) dessa serie < 10 e fecho
  das 16:00 > media dos ultimos 200 fechos das 16:00 -> long na abertura da vela das 16:00.
- Saida: no fecho das 16:00 de um dia em que o fecho > media dos ultimos 5 fechos das 16:00; ou ao fim de 115 velas de 1h
  (~5 dias). Stop 3 ATR(14) de 1h na vela de sinal, sem alvo.
- Timeframe: 1h. Long-only. Parametros fixos (RSI(2) < 10, media 200, media 5 iguais ao rsi2-dip-d e a Connors; 115 velas e
  stop iguais ao ibs-cash-1h).

## 2026-11-18 Crypto (Claude, a pedido do Antonio: so crypto a partir de agora) - registadas antes de correr
Hipotese: em crypto o momentum/tendencia e o efeito com mais evidencia; spot na Kraken so permite long.
- **k-donchian20-d**: long ao fechar acima do maximo de 20 dias; sai abaixo do minimo de 10. Stop 3 ATR.
- **k-sma100-d**: long acima da media de 100 dias, fora abaixo. Stop 3 ATR.
- **k-donchian55-4h**: long ao fechar acima do maximo de 55 velas de 4h; sai abaixo do minimo de 20. Stop 3 ATR.
- **k-sma200-4h**: long acima da media de 200 velas de 4h. Stop 3 ATR.
Custos Kraken spot 0.26% por lado + 0.05% slippage. Mercados: BTC, ETH, SOL.
