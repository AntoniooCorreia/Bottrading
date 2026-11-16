# Ideias do agente

Registo de ideias criadas pelo agente no modo ideias (ver CLAUDE.md). Cada ideia e registada aqui ANTES de ser testada.

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
