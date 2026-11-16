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
