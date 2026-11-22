# Registo do holdout (2025-2026) - cada variante so la vai UMA vez

- 2026-11-17 `double7-d` (diario, ideia 15 do agente; PASSA no dev t 3.07 e em 2012-2018 t 3.46) -> holdout CFD:
  NQ 25 trades +0.036R (t 0.31), S&P 26 +0.070R (t 0.68), Dow 27 +0.156R (t 1.71); junto 78 trades +0.089R, t 1.51.
  Veredicto automatico: REPROVADA (poucas trades, < 60 - o holdout so tem ~2 anos). Leitura: positiva nos 3 indices,
  na mesma direcao do dev, mas amostra pequena e NQ fraco. Nao se afina mais nada depois disto.

- 2026-11-18 carteira C9 (= carteira C5: rsi2-dip-d + ibs-dip-d + down3-d + ibs-bear-d, 10 indices, max 3 abertas, 1 por regiao,
  paragem mensal -3%; decisao do Antonio antes da demo) -> holdout 2025-01-01 a 2026-11-15, CFD, 1% por trade:
  2025 +17.2%, 2026 +34.5% (10.5 meses), pior mes -3.6%, pior queda -7.4%, 16/23 meses positivos; positiva em 8 de 10 indices
  (ASX e Hang Seng ligeiramente negativos). Indicadores aquecidos com dados de antes de 2025; so trades com entrada >= 2025.
  Leitura: passa a regra combinada antes de ver (positiva e pior mes > -6%). Muito acima do dev (+12.5%/ano): 2025-26 foram
  anos de subida forte, por isso parte disto e sorte do periodo. Nao se afina nada depois disto.
  Nota: o holdout do double7-d (2026-11-17) foi corrido SEM aquecimento (run_swing.py carrega so 2025+), por isso a media de 200
  so existia a partir de ~out/2025 e teve menos trades do que devia. Nao se repete (uma vez por variante); fica registado.

- 2026-11-18 NOTA sobre o C9: o resultado acima foi calculado com o erro de portfolio.py (trades sobrepostas no mesmo indice
  no mesmo dia), encontrado no mesmo dia ao construir o bot da demo. Os +17.2%/+34.5% estao inflacionados e NAO contam como
  aprovacao. Nao se volta a correr o holdout desta carteira sem decisao explicita do Antonio.

- 2026-11-18 `fomc-holiday-1h` (1h, ideia 25 do agente, #40; PASSA no dev com futuros t 3.81, CFD t 3.45; 2012-2018 t 0.85) -> holdout
  2025-01-01 a 2026-11-15, futuros: NQ 38 trades +0.053R (t 0.45), S&P 41 -0.041R (t -0.35), Dow 42 +0.051R (t 0.40); junto
  121 trades +0.020R, t 0.29. CFD: junto +0.003R, t 0.04. Veredicto automatico: REPROVADA (poucas trades, < 60).
  Leitura: o resultado forte de 2019-2024 nao se repete nem em 2012-2018 nem no holdout: provavelmente sorte do periodo dev.
  Nao se afina nada depois disto.
- 2026-11-18 crypto K1 (k-donchian20-d,k-sma100-d,k-donchian55-4h,k-sma200-4h; BTC/ETH/SOL) holdout 2025-26 aberto UMA vez
- 2026-11-19 cripto #100 `k-sma200-4h-persist` (PASSA no dev: t 3.06, confirmacao 5/5; pre 2017-18 positivo: BTC +0.80R/23,
  ETH +0.33R/19, carteira 2017 +26.0%, 2018 +4.9%) -> holdout 2025-01-01 ate ao fim dos dados, UMA vez, custos Kraken:
  BTC +0.112R/19, ETH +1.330R/18, SOL +0.962R/19; junto 56 trades +0.79R, t 1.53, win rate 34%. Carteira (so #100):
  2025 +15.7%, 2026 +32.0%, pior mes -5.3%, pior queda -15.8%. CONFIRMACAO no holdout: so 1/5 positivas (XRP -0.31R, ADA -0.37R,
  DOGE -0.26R, LINK +0.03R, AVAX -0.10R). Veredicto automatico REPROVADA (poucas trades em 2 anos, < 60 por moeda).
  Leitura: positiva nas 3 moedas principais (a K1 deu -10.9% em 2025), mas falha nas moedas de confirmacao -> sinal misto, nao
  conta como robusta. Win rate continua baixo (~30%) e o pior ano no dev e -20.8%. Aquecimento: a media de 200 velas de 4h so
  existe a partir de ~fev/2025 (o laboratorio carrega so 2025+). Nao se afina nada depois disto; o holdout desta variante fica gasto.
- 2026-11-19 cripto #116 `k-sma100-d-b100-tp1` (a #113 com regime BTC > media de 100 dias; PASSA no dev: t 4.63, win rate 53%,
  confirmacao 4/5; pre 2017-18 +0.006R/trade em 20 trades, >= 0) -> holdout 2025-01-01 ate ao fim dos dados, UMA vez, custos Kraken:
  BTC -0.016R/17, ETH +0.185R/17, SOL -0.019R/22; junto 56 trades +0.044R, t 0.37, win rate 46%. Confirmacao 3/5 (XRP +0.07,
  ADA -0.14, DOGE -0.11, LINK +0.06, AVAX +0.04). Carteira: 2025 +4.3%, 2026 -1.8%, pior mes -4.6%, pior queda -6.9%.
  Veredicto automatico REPROVADA (< 60 trades por moeda). Leitura: positiva mas quase zero; o win rate cai de 53% para 46%.
  A aposta simetrica precisa de deriva forte, que 2025-26 nao teve. Holdout gasto; nada se afina depois disto.
- 2026-11-22 cripto #155 `k-sma50-d-btc50-bracket-s2-rx` (moeda > media 50, BTC > media 50, alvo 1R / stop 2 ATR, sai de tudo quando
  o BTC perde a media 50; PASSA no dev: t 5.05, win rate 60%, confirmacao 5/5; pre 2017-18 +0.048R/trade em 54 trades, >= 0:
  BTC -0.07R/33, ETH +0.23R/21, 2017 +8.9%, 2018 -6.3%) -> holdout 2025-01-01 ate ao fim dos dados, UMA vez, custos Kraken:
  BTC +0.025R/38, ETH +0.019R/36, SOL -0.061R/40; junto 114 trades -0.007R, t -0.09, win rate 47%. Confirmacao 1/5.
  Carteira: 2025 +4.7%, 2026 -5.5%, pior mes -5.8%, pior queda -20.0%. Veredicto automatico REPROVADA.
  Leitura: a vantagem do dev (+0.22R, win rate 60%) desaparece fora do dev (pre ~+0.05R, holdout ~0R). Holdout gasto; nada se afina.
- 2026-11-22 cripto #157 `k-sma50-d-btc50-bracket-s15` (a #151 com stop 1.5 ATR; PASSA no dev: t 3.77, win rate 61%, conf. 4/5;
  pre +0.034R/trade em 77 trades, >= 0) -> holdout UMA vez: BTC -0.043R/49, ETH -0.071R/47, SOL -0.106R/45; junto 141 trades
  -0.072R, t -0.86, win rate 52%; confirmacao 0/5. Carteira: 2025 +0.9%, 2026 -11.1%, pior queda -25.8%. REPROVADA.
  Leitura: o stop mais curto so acrescenta custo; fora do dev perde. Holdout gasto; nada se afina.
