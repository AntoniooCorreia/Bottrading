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

## 2026-11-18 Diagnostico win rate (Claude, a pedido do Antonio: quer win rate alto) - registado antes de correr
Pergunta: quanto win rate se ganha e quanto resultado se perde se a K1 fechar com alvo fixo em vez de deixar correr.
Variantes: as 4 estrategias da K1 iguais (entrada, stop 3 ATR, saida por sinal) + alvo fixo de 1R (k1-tp1) e de 2R (k1-tp2).
Periodo: so dev 2019-2024 (holdout da K1 ja foi visto: nao conta como validacao). E um diagnostico, nao uma ideia nova para operar.

## 2026-11-19 cripto - sessao 1 (4 ideias; ideias cripto testadas antes: ~12 (K1 = 4, 6 compras de quedas, 2 diagnosticos de alvo); hoje: 4 de 12) - registadas antes de correr
Diagnostico previo (so dev 2019-2024, trades da K1 ja conhecidas): 431 das 974 trades da K1 duram <= 1 dia e TODAS perdem
(-0.45R em media): sao "serras" (entra e sai logo). 315 delas sao da k-sma200-4h (cruza a media para cima e para baixo).
Sem as trades curtas o win rate das restantes seria ~44%. Na k-donchian55-4h, 64 trades sao paradas pelo stop no 1.o dia
(3 ATR de 4h e apertado para o ruido da rutura). Trades com BTC abaixo da media de 200 dias: positivas em media, mas 2022 (-50R)
e quase todo desse regime. Daqui saem 4 ideias (parametros fixos, uma mudanca de cada vez contra a K1):
- **#100 k-sma200-4h-persist** (4h): a k-sma200-4h com PERSISTENCIA contra as serras. Hipotese: um cruzamento da media que dura
  um dia inteiro e uma mudanca de tendencia; um que dura 1-2 velas e ruido. Entrada: os ultimos 6 fechos de 4h (1 dia) todos
  acima da media de 200 velas de 4h. Saida: os ultimos 6 fechos todos abaixo. Stop 3 ATR(14) de 4h, sem alvo, sem tempo maximo.
  Espera-se: muito menos trades curtas, win rate a subir de 16% para 30%+, R por trade igual ou maior.
- **#101 k-dc55-4h-btcbull** (4h): a k-donchian55-4h so com ENTRADAS quando o BTC fechou o dia anterior acima da media de 200 dias
  (filtro de regime; as moedas seguem o BTC). Saida igual (fecho abaixo do minimo de 20 velas) e stop 3 ATR(14) de 4h.
  Hipotese: as ruturas em mercado de baixa (2018, 2022) sao subidas de alivio que falham; cortar o pior ano (2022) sem perder muito.
- **#102 k-dc55-4h-wide** (4h): a k-donchian55-4h com stop de 6 ATR(14) de 4h em vez de 3 (~1 dia de volatilidade).
  Hipotese: logo a seguir a uma rutura o preco volta muitas vezes a testar o nivel; 3 ATR de 4h e apanhado por esse ruido.
  Stop mais largo -> menos stops no 1.o dia (win rate maior) e custos menores em R (posicao mais pequena). R por trade vai baixar
  mecanicamente (o mesmo movimento vale menos R): reportar os dois.
- **#103 k-dip-hold-4h** (4h): COMPRAR RECUO DENTRO DA TENDENCIA e segurar 7 dias. Entrada: BTC fechou o dia anterior acima da
  media de 200 dias E a moeda fecha acima da sua media de 600 velas de 4h (~100 dias) E o fecho de 4h e o mais baixo das ultimas
  30 velas (minimo de 5 dias). Saida: ao fim de 42 velas de 4h (7 dias) ou stop de 6 ATR(14) de 4h; sem alvo.
  Hipotese: em regime de alta a cripto sobe em media (deriva forte); comprar um minimo de 5 dias e segurar 7 dias apanha essa
  deriva -> win rate > 50%. Diferente das compras de quedas ja testadas (saiam ao fim de 1-3 dias com ganho medio < custos):
  aqui o tempo de posse e longo para o ganho medio passar bem os ~0.57% de custos. Nota do motor: se o stop for tocado e o
  sinal ainda estiver ativo, o motor volta a entrar (regra comum a todas as ideias).
Fasquia (criterio oficial cripto): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade.

## 2026-11-19 cripto - sessao 2 (:30) (4 ideias; ideias cripto testadas antes: 16; hoje: 8 de 20) - registadas antes de correr
Leitura da sessao 1: (a) trend following tem win rate 16-42% porque deixa correr; (b) o filtro BTC > media 200 dias (#101)
apagou 2022 e o stop largo (#102) cortou os stops do 1.o dia (win rate 35% -> 42%); (c) a K1 com alvo de 1R ja dava 49% de win
rate e +0.10R com stop de 3 ATR de 4h. Hipotese central: com o REGIME BTC (so entra em mercado de alta, onde a deriva e para cima)
e STOP LARGO (6 ATR de 4h, ruido nao apanha), um alvo SIMETRICO de 1R deve ganhar mais vezes do que perde (> 50%), porque a deriva
positiva empurra o preco para o alvo antes do stop. O alvo de 1R com stop de 6 ATR de 4h fica a ~6-10% do preco: custos (0.57%)
pesam ~0.07-0.1R, nao matam. Nota do motor: depois de um alvo ou stop, se o sinal ainda estiver ativo o motor volta a entrar na
abertura seguinte (regra comum). Uma mudanca registada de cada vez, parametros fixos (os mesmos ja usados: 55/20, 200, 6, 1R):
- **#104 k-dc55-4h-bw-tp1** (4h): rutura de 55 velas de 4h so com BTC acima da media de 200 dias (= #101) + stop 6 ATR(14) de 4h
  (= #102) + alvo fixo de 1R. Saida tambem ao fechar abaixo do minimo de 20 velas. Espera-se win rate >= 50% e R/trade > 0.
- **#105 k-persist-bw** (4h): #100 (6 fechos de 4h seguidos acima da media de 200 velas; sai com 6 abaixo) so com ENTRADAS
  com BTC acima da media de 200 dias + stop 6 ATR(14) de 4h, sem alvo. Junta as tres mudancas que funcionaram (proximo passo do
  SUMMARY). Espera-se win rate ~35-40% e pior ano bem melhor que o -20.8% da #100.
- **#106 k-persist-bw-tp1** (4h): a #105 com alvo fixo de 1R. Espera-se win rate >= 50%.
- **#107 k-dc20-d-bull-tp1** (diario): rutura de 20 dias (k-donchian20-d: sai abaixo do minimo de 10 dias) so com BTC acima da media
  de 200 dias, stop 3 ATR(14) diario (~ largura de 6-7 ATR de 4h) e alvo fixo de 1R. A mesma hipotese no diario (menos custos por trade).
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade, e pior ano/pior mes da carteira.

## 2026-11-19 cripto - sessao 3 (:00) (4 ideias; ideias cripto testadas antes: 20; hoje: 12 de 20) - registadas antes de correr
Leitura das sessoes 1-2: o alvo de 1R sobe o win rate para 54-60% mas corta o ganho por trade de ~+1.7R para ~+0.2-0.3R
(% ao ano cai de ~32% para 3-9%). E o regime BTC deixa a SOL abaixo de 60 trades quando a ideia segura muito tempo.
Duas perguntas desta sessao, uma mudanca de cada vez, parametros fixos:
(1) SAIDA PARCIAL: fechar METADE da posicao no alvo de 1R e passar o stop do resto para o preco de entrada + custos
    (breakeven: o resto ja nao pode perder) e deixar o resto correr ate a saida do sinal. Hipotese: o win rate fica perto do
    da versao com alvo (quase todas as trades que tocam 1R acabam positivas: +0.5R garantido) e o ganho medio sobe muito,
    porque metade apanha as tendencias grandes. Mudanca no motor: run_positions ganha 'partial' (fracao fechada no alvo) e
    'be' (stop do resto para a entrada x (1 + custos) depois do alvo). Regra conservadora: se na vela do alvo o minimo tambem
    toca o breakeven, o resto sai no breakeven nessa vela. Custos cobrados uma vez sobre a posicao inteira (como hoje).
(2) MAIS TRADES: a #107 (rutura de 20 dias + regime BTC + alvo 1R; win rate 60%, +0.28R, pior ano 0%) so falhou por a SOL ter
    57 trades. Proximo passo escrito no SUMMARY: a mesma regra em 4h (sinais ~6x mais frequentes). Rutura de 20/10 velas
    (sistema 1 das Tartarugas), stop 6 ATR(14) de 4h (igual a #102/#104/#106: ~1 dia de volatilidade).
- **#108 k-persist-bw-half** (4h): #105 (6 fechos de 4h acima da media de 200 velas, so entra com BTC > media 200 dias; sai com
  6 fechos abaixo; stop 6 ATR(14) de 4h) + saida parcial: metade em 1R, resto com stop em breakeven ate ao sinal de saida.
  Espera-se win rate ~45-55% e R/trade entre +0.22 (#106) e +1.70 (#105). Risco conhecido: #105 tinha 31-42 trades por moeda
  (sem re-entradas depois do alvo) -> provavelmente REPROVADA por trades; corre-se na mesma para medir o efeito da saida parcial.
- **#109 k-dc20-4h-bw-tp1** (4h): long ao fechar acima do maximo das 20 velas de 4h anteriores, so com BTC > media 200 dias
  (dia anterior fechado); sai ao fechar abaixo do minimo das 10 velas anteriores; stop 6 ATR(14) de 4h; alvo fixo 1R.
  Espera-se win rate >= 50%, R/trade > 0 e >= 60 trades na SOL.
- **#110 k-dc20-4h-bw-half** (4h): #109 com saida parcial (metade em 1R, resto em breakeven ate ao fecho abaixo do minimo de 10).
  Compara diretamente alvo inteiro vs parcial nas mesmas entradas.
- **#111 k-dc20-4h-bw-be** (4h): #109 SEM alvo, mas com o stop passado para breakeven (entrada + custos) quando o preco toca +1R.
  Mede o efeito do breakeven sozinho (pedido do Antonio: medir alvo parcial e breakeven separados). Espera-se win rate mais baixo
  que #109 (trades que voltam a zero contam como nao-ganhas) mas R/trade maior.
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade, pior ano e pior mes da carteira.

## 2026-11-19 cripto - sessao 4 (:30) (4 ideias; ideias cripto testadas antes: 24; hoje: 16 de 20) - registadas antes de correr
Leitura das sessoes 1-3: a melhor combinacao de win rate e resultado e a #107 (rutura de 20 dias no DIARIO + BTC > media 200 dias +
stop 3 ATR(14) diario + alvo 1R: win rate 60%, +0.28R, pior ano 0%), que so falhou por a SOL ter 57 trades (< 60). Em 4h a mesma
regra piora (saida de 10 velas de 4h curta demais). O win rate alto vem do alvo de 1R com stop largo em regime de alta e das
RE-ENTRADAS depois do alvo (o motor volta a entrar na abertura seguinte se o sinal ainda estiver ativo: regra comum).
Esta sessao fica no DIARIO (stop 3 ATR(14) diario, ~10-15% do preco: custos 0.57% pesam ~0.05R) e testa 3 formas de ter mais
trades com o mesmo mecanismo, e 1 de ganhar mais por trade com as mesmas entradas. Parametros fixos ja usados (20/10, 100, 200, 3, 1R):
- **#112 k-dc20-d-own-tp1** (1d): #107 com o regime da PROPRIA moeda em vez do BTC: so entra se a moeda fechou o dia anterior
  acima da sua media de 200 dias. Entrada: fecho acima do maximo dos 20 dias anteriores; saida: fecho abaixo do minimo dos 10
  dias anteriores; stop 3 ATR(14) diario; alvo 1R. Hipotese: o momentum que conta e o da propria moeda (a SOL teve tendencias
  proprias em 2021 e 2023 com o BTC ainda abaixo da media); mais trades na SOL, mesmo win rate. Risco: filtra menos 2022.
- **#113 k-sma100-d-bull-tp1** (1d): BRACKETS DE 1R DENTRO DA TENDENCIA. Entra quando a moeda fecha acima da media de 100 dias
  e o BTC fechou o dia anterior acima da media de 200 dias; sai ao fechar abaixo da media de 100 dias; stop 3 ATR(14) diario;
  alvo 1R; enquanto a tendencia durar o motor volta a entrar depois de cada alvo. Hipotese: em regime de alta a cripto tem
  deriva positiva forte; uma aposta simetrica (alvo = stop) com deriva a favor ganha mais de 50% das vezes; muitos mais
  trades que a rutura (cada dia de tendencia pode gerar nova entrada). Espera-se win rate >= 55%, R/trade +0.1 a +0.3.
- **#114 k-pb-d-bull-tp1** (1d): RECUO DENTRO DA TENDENCIA com alvo. Entra quando o BTC fechou o dia anterior acima da media de
  200 dias E a moeda fecha acima da media de 100 dias E o fecho e mais baixo que todos os 5 fechos anteriores (recuo de 1 semana).
  Saida por sinal: fecho acima do maximo dos 20 dias anteriores (tendencia retomada); stop 3 ATR(14) diario; alvo 1R.
  Hipotese: comprar mais barato dentro da tendencia (pedido do Antonio) e esperar o alvo de 1R (~10-15%) em vez de sair
  ao fim de 1-3 dias como as compras de quedas ja reprovadas (essas tinham ganho medio < custos).
- **#115 k-dc20-d-own-be** (1d): as entradas da #112 SEM alvo, com o stop passado para breakeven (entrada + custos) quando o
  preco toca +1R; sai ao fechar abaixo do minimo de 10 dias. Mede, nas mesmas entradas, o lado "mais % ao ano" (win rate
  esperado ~35-45%, R/trade maior). Serve para o Antonio ver a troca win rate vs resultado com numeros.
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade, pior ano e pior mes da carteira.
Nota: com qualquer filtro de media de 200 dias o pre 2017-18 fica quase vazio (os dados comecam em 2017-08; a media so existe
a partir de ~2018-03, ja em mercado de baixa). Isto e conhecido antes de correr.

## 2026-11-19 cripto - sessao 5 (:00) (ate 4 ideias; ideias cripto testadas antes: 28; hoje: 16 de 20 antes desta sessao) - registadas antes de correr
Leitura das sessoes 1-4: a #113 (moeda acima da media de 100 dias + BTC acima da media de 200 dias, alvo 1R = stop 3 ATR(14) diario,
volta a entrar depois de cada alvo enquanto a tendencia dura) e a unica com win rate > 50%, ~+10%/ano e nenhum ano negativo no
dev (247 trades, t +4.78, confirmacao 4/5). Mecanismo: aposta simetrica com deriva positiva a favor. Duas perguntas, uma mudanca
de cada vez contra a #113, parametros fixos ja usados no projeto (100, 200, 600 = 100 dias em 4h, 6 ATR de 4h, 1R).
Primeiro lote (2 ideias); o segundo lote (ate 2) so e registado depois de ler estes resultados, tambem antes de correr.
- **#116 k-sma100-d-b100-tp1** (1d): a #113 com o regime do BTC MAIS RAPIDO: BTC fechou o dia anterior acima da sua media de
  100 dias (em vez de 200). Resto igual (entra: moeda fecha acima da media de 100 dias; sai: fecha abaixo; stop 3 ATR(14) diario;
  alvo 1R; volta a entrar). Hipotese: a media de 200 dias liga tarde nas recuperacoes (2019 T2, 2020 T2, 2023 T1), que sao
  precisamente as fases de deriva forte; a de 100 liga mais cedo -> mais trades boas. Risco: liga tambem nas subidas de alivio
  de 2022 (mar-abr e jul-ago) -> pior ano pode ficar negativo. Efeito conhecido antes de correr: o pre 2017-18 passa a ter
  algumas trades (media de 100 dias existe desde ~dez 2017), quase todas em mercado de baixa.
- **#117 k-sma600-4h-bull-tp1** (4h): a #113 em velas de 4h: entra ao fechar acima da media de 600 velas de 4h (= 100 dias)
  com o BTC acima da media de 200 dias; sai ao fechar abaixo; stop 6 ATR(14) de 4h (~2.5 ATR diario, o stop largo de 4h ja
  usado); alvo 1R. Hipotese: o mesmo mecanismo, mas depois de cada alvo volta a entrar 4h depois em vez de no dia seguinte,
  e o alvo fica mais perto (~6-8%) -> mais ciclos e mais trades com a mesma deriva. Risco: serras a volta da media em 4h
  (o problema das trades curtas da k-sma200-4h) e custos maiores em R (~0.08R).
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade, pior ano e pior mes da carteira.
Resultado do primeiro lote (antes de registar o segundo): #116 passa dev (t +4.63, win rate 53%) mas 2022 fica -4.9% (o risco
previsto) e o pre e ~0 (+0.11R em 20 trades); holdout 2025-26 +0.04R/trade, win rate 46%: o efeito quase desaparece. #117 (4h)
passa o dev com win rate so 40%: as saidas no cruzamento da media em 4h sao muitas perdas pequenas (serras). Leitura: o win rate
> 50% vem da deriva forte (2020-21, 2023-24); onde a tendencia e fraca ou lateral (2025-26) a aposta simetrica e moeda ao ar, e
as saidas pelo sinal (fecho abaixo da media) transformam trades em perdas pequenas que contam como perdas.
Segundo lote (2 ideias, ultimas da noite: 20 de 20), uma mudanca de cada vez contra a #113:
- **#118 k-sma100-d-bull-bracket** (1d): entradas iguais a #113 (moeda fecha acima da media de 100 dias, BTC acima da media de
  200 dias), mas SEM saida pelo sinal: a trade so sai no alvo de 1R ou no stop de 3 ATR(14) diario (aposta simetrica pura).
  Depois de sair, so volta a entrar se a condicao de entrada ainda estiver ativa. Hipotese: o fecho abaixo da media corta trades
  que, com deriva positiva, chegariam ao alvo; sem essa saida cada trade e +1R ou -1R e o win rate mede diretamente a deriva
  -> win rate > 53%. Risco: perdas de -1R inteiras quando a tendencia acaba (2022) em vez de perdas pequenas.
  Mudanca no motor: run_positions ganha 'signal_exit' (True = como sempre; False = o sinal so serve para entrar).
- **#119 k-sma100-d-slope-tp1** (1d): a #113 so com entradas quando a media de 100 dias da moeda esta a SUBIR (media de hoje
  acima da de ha 20 dias). Saida, stop e alvo iguais. Hipotese: preco acima de uma media plana e lateral (tipo 2025-26 ou 2019 T3),
  onde a aposta simetrica e moeda ao ar; media a subir = deriva real -> win rate maior e pior ano melhor. Risco: menos trades
  (a SOL tinha 69 na #113; pode cair abaixo de 60).
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Reportar sempre win rate e R por trade, pior ano e pior mes da carteira.

## 2026-11-21 SCALPING cripto (Claude, a pedido do Antonio: "nao quero estar em trades durante dias, quero varias trades por semana") - registadas antes de correr
Ideias cripto testadas antes: 32. Hoje: 4 ideias x 2 lados (long e short) = 8 variantes (#120-#127). Mais testes = mais desconfianca.
Dados novos: velas de 5m da Binance (`TF=5m python crypto_download.py ...`), 15m = 5m agregadas. Custos oficiais iguais (Kraken taker
0.26% por lado + 0.05% slippage = 0.57% ida e volta). AVISO ANTES DE CORRER: um stop de scalping em BTC e ~0.3-0.8% do preco,
por isso os custos sozinhos valem ~0.7-2R por trade. Para passar, uma ideia precisa de ganhar MAIS do que isso por trade antes de custos.
Mostra-se tambem (so como diagnostico, nao conta para o veredicto) o resultado sem custos e com custos de maker (0.16% por lado, limit).
Shorts: spot na Kraken nao deixa; os shorts sao medidos para saber se valem a pena (precisariam de margem/futuros, com custos extra).
- **#120/#121 s-bb-rev-5m long/short**: reversao a media em 5m. Fecho fora da Bollinger (20, 2.5 desvios) contra o movimento, mas a favor
  da EMA 600 de 5m (~50h). Sai quando o fecho volta a media de 20, ou ao fim de 24 velas (2h). Stop 2 ATR(14) de 5m.
  Hipotese: excessos de poucos minutos dentro da tendencia sao ruido de liquidez que reverte.
- **#122/#123 s-orb-us-15m long/short**: rutura da 1.a hora de Nova Iorque (9:30-10:30 NY) em 15m. 1.o fecho fora do intervalo depois
  das 10:30, uma por dia e lado. Stop 1.5 ATR(14) de 15m, alvo 2R, maximo 22 velas (~16:00 NY).
  Hipotese: a abertura dos EUA traz o fluxo do dia (ETFs, institucionais); a rutura da 1.a hora segue.
- **#124/#125 s-rsi2-15m long/short**: RSI(2) de 15m < 5 (long) / > 95 (short) a favor da EMA 200 de 15m. Sai com RSI(2) > 60 / < 40
  ou ao fim de 16 velas (4h). Stop 2 ATR. Hipotese: o mesmo efeito de Connors em prazo curto.
- **#126/#127 s-burst-15m long/short**: vela de 15m com amplitude > 2.5x ATR que fecha no quarto de cima/baixo, a favor da EMA 200.
  Entra na abertura seguinte, alvo 1.5R, stop 1.5 ATR, maximo 8 velas (2h). Hipotese: explosoes de volume continuam por minutos.
Fasquia: criterio oficial cripto (>= 60 trades por moeda, positiva em cada, t junto >= 3.0, confirmacao >= 3/5).
- **Shorts da K1 (diagnostico para a conta demo)**: as 4 estrategias da K1 ao espelho (preco invertido), dev 2019-2024. So entram na demo
  se forem positivas e passarem o criterio.
- **#128 k1-short-bear (registada depois de ver os shorts da K1, por isso conta como ideia a mais e com desconfianca)**: as 4
  estrategias da K1 ao espelho, mas so com o BTC ABAIXO da media de 200 dias (espelho exato do filtro do #101 dos longs;
  sai tambem quando o regime volta a alta). Hipotese: os shorts so tem vantagem em mercado de baixa; em alta a deriva come-os.

## 2026-11-21 INTRADAY 1h-1 dia (Claude, a pedido do Antonio: 3 a 4 trades por semana, sem ficar dias em trade) - registadas antes de correr
Ideias cripto testadas antes: 42. Hoje: 4 (#129-#132). Porque 1h: o scalping (#120-#127) mostrou vantagem antes de custos mas stops de
0.4-1.7% fazem os custos valer 0.3-1.4R. Em 1h com stop de 3 ATR(14) de 1h (~2-3% do preco) os custos descem para ~0.2-0.3R.
Todas: so long (spot), velas de 1h, tempo maximo 24 velas (1 dia), stop 3 ATR(14) de 1h, so com o BTC acima da media de 200 dias
(regime de alta, o filtro que mais ajudou nos testes #101-#118), sem filtro de risco minimo (o custo entra todo no resultado).
Objetivo de frequencia: a carteira (BTC+ETH+SOL, 1 posicao por moeda) com 3-4 trades por semana (~150-200 por ano).
- **#129 h-rsi2-1h**: RSI(2) de 1h < 10 com fecho > EMA 200 de 1h. Sai com RSI(2) > 70 ou 24h. Hipotese: quedas de 2-3 horas
  dentro de uma tendencia de alta revertem (Connors), agora em cripto 1h com regime.
- **#130 h-low12-tp-1h**: fecho de 1h e o mais baixo das ultimas 12 velas com fecho > EMA 200 de 1h. Alvo 1R, stop 3 ATR, max 24h.
  Hipotese: comprar o minimo de meio dia na tendencia e sair num alvo curto da win rate alto (como #118 mas intraday).
- **#131 h-dc24-1h**: fecho acima do maximo das ultimas 24 velas de 1h (maximo do dia). Alvo 2R, stop 3 ATR, max 24h.
  Hipotese: ruturas do maximo de 24h em regime de alta continuam durante horas (momentum intradiario em cripto).
- **#132 h-squeeze-1h**: largura das Bollinger (20, 2) de 1h no minimo das ultimas 120 velas e fecho acima da banda de cima.
  Alvo 2R, stop 3 ATR, max 24h. Hipotese: depois de compressao de volatilidade a saida tende a continuar.
Fasquia: criterio oficial cripto (>= 60 trades por moeda, positiva em cada, t junto >= 3.0, confirmacao >= 3/5).

## 2026-11-21 PERPETUOS KRAKEN (decisao do Antonio: "avanca", quer a demo com mais trades: minimo 1/semana, idealmente 3) - registadas antes de correr
Custos novos (so com --venue perp; o spot fica igual): taker 0.05% por lado (tier 1 da tabela da Kraken de jul-2026) + 0.02% de
slippage por lado = 0.14% ida e volta, mais funding conservador de 0.01% a cada 8h pago tanto por long como por short.
Nota de honestidade: antes de registar isto corri UMA vez o #133 no dev para verificar o codigo novo (t +2.16, REPROVADA). Nada foi
afinado depois disso. Ideias cripto testadas antes: 46. Hoje: 5 (#133-#137).
- **#133 h-dc24-1h (perp, long)**: igual ao #131 (rutura do maximo de 24h, regime de alta, alvo 2R, stop 3 ATR, max 24h).
- **#134 h-dc24-1h-short (perp)**: espelho: fecho abaixo do minimo das ultimas 24 velas de 1h, fecho < EMA 200 de 1h e BTC ABAIXO da
  media de 200 dias. Alvo 2R, stop 3 ATR, max 24h. Hipotese: em mercado de baixa as quebras do minimo do dia continuam.
- **#135 h-rsi2-1h (perp, long)**: igual ao #129 (RSI(2) 1h < 10 na tendencia, sai com RSI > 70 ou 24h).
- **#136 h-rsi2-1h-short (perp)**: espelho: RSI(2) 1h > 90, fecho < EMA 200 de 1h e BTC abaixo da media de 200 dias; sai com RSI(2) < 30
  ou 24h. Stop 3 ATR.
- **#137 s-orb-us-15m-long (perp)**: igual ao #122 (rutura da 1.a hora de NY em 15m, alvo 2R), o scalp mais perto de zero.
Depois: carteira com as que tiverem R/trade > 0 nas 3 moedas (long + short juntas) para medir trades por semana.

## 2026-11-21 cripto - sessao :00 (19h UTC) (1 ideia; ideias cripto testadas antes: 51; hoje: 19 de 20 antes desta sessao) - registada antes de correr
Base (best.py): K20 = #118 k-sma100-d-bull-bracket (pontuacao 82: win rate 68%, total +62%, melhor ano +17.7%, pior ano -2.0%, pior mes -4.1%).
O que falha na base: SOL so 54 trades (< 60); 0.6 trades por semana (objetivo 2-3); mediana de 13 dias sem trade entre entradas;
as trades duram muito (75 de 199 entre 8 e 30 dias, 32 acima de 30 dias com so +0.11R); 2022 quase sem trades (regime BTC fechado, -2%).
Limite da noite: so cabe 1 ideia (19 de 20 ja usadas hoje), por isso escolho a que ABRE MAIS TRADES.
- **#138 k-sma600-4h-bull-bracket** (4h): a mesma regra da #118 (moeda acima da sua media de 100 dias = 600 velas de 4h, BTC acima da media
  de 200 dias, entra na abertura seguinte quando esta sem posicao; sai SO por alvo 1R ou stop, sem saida pelo sinal), mas em velas de 4h
  com stop 3 ATR(14) de 4h (~0.4x o stop diario da #118). UMA mudanca: timeframe/tamanho do stop. Hipotese: o win rate de uma aposta
  simetrica 1R/1R com deriva positiva vem da deriva, nao do tamanho do stop; com stop ~2.5x mais curto o alvo e tocado ~2.5x mais
  depressa -> trades de dias em vez de semanas e ~2-2.5x mais trades (SOL acima de 60), com reentrada 4h depois de cada saida.
  Risco: o custo (0.57% ida e volta) passa de ~0.05R para ~0.12-0.15R por trade e o ruido intradiario baixa o win rate; a #117
  (mesma entrada em 4h mas com saida pelo sinal e stop 6 ATR) deu so 40% de win rate e +0.14R.
Fasquia (criterio oficial cripto, fixo): >= 60 trades em CADA uma de BTC/ETH/SOL, meanR > 0 em cada, t junto >= 3.0, CONFIRMACAO
positiva em >= 3/5 moedas extra; depois --period pre >= 0. Comparar com a base K20: win rate, % total, melhor ano, pior ano, trades/semana.
