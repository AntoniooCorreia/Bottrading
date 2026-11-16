# TODO de testes (so isto se testa; o Antonio aprova itens novos)

## Fase 1 - base (parametros por defeito: tp 2R, stop 0.5 ATR, sessao rth)
- [x] `python run.py --play bounce --levels pdhl` -> REPROVADA, t junto -11.29
- [x] `python run.py --play bounce --levels pwhl` -> REPROVADA, t junto -6.90
- [x] `python run.py --play bounce --levels swing1h` -> REPROVADA, t junto -15.79
- [x] `python run.py --play bounce --levels round` -> REPROVADA, t junto -10.02
- [x] `python run.py --play break --levels pdhl` -> REPROVADA, t junto -4.55
- [x] `python run.py --play break --levels pwhl` -> REPROVADA, t junto 1.34 (NQ/ES +0.13R, Dow -0.03R)
- [x] `python run.py --play break --levels swing1h` -> REPROVADA, t junto -5.49
- [x] `python run.py --play break --levels round` -> REPROVADA, t junto -3.65
- [x] `python run.py --play fake --levels pdhl` -> REPROVADA, t junto -6.86
- [x] `python run.py --play fake --levels pwhl` -> REPROVADA, t junto -1.12 (so Dow positivo)
- [x] `python run.py --play fake --levels swing1h` -> REPROVADA, t junto -7.62
- [x] `python run.py --play fake --levels round` -> REPROVADA, t junto -4.19

## Fase 2 - robustez (so para combinacoes da fase 1 com t junto >= 1.5 no dev)
Para cada uma: tp {1, 1.5, 3} x stop-atr {0.3, 1.0} e tambem --session all.
Acrescenta aqui as linhas concretas quando a fase 1 acabar.
(2026-11-16: fase 1 concluida; nenhuma combinacao com t junto >= 1.5 -> fase 2 vazia. A melhor foi break-pwhl com t 1.34.) Uma variante so conta se a vizinhanca de
parametros tambem for positiva (nao um pico isolado).

## Fase 3 - holdout
So variantes com PASSA no dev e vizinhanca positiva. Uma vez cada. Ver CLAUDE.md.

## Ideias do agente (2026-11-16)
Registadas em IDEAS.md antes de correr. Fasquia t >= 3.0.
- [x] `python run.py --play gapfill --levels pdc` -> REPROVADA, t junto -1.34 (NQ -0.08R, ES +0.01R, Dow -0.01R)
- [x] `python run.py --play fake --levels onhl` -> REPROVADA, t junto -4.62 (negativa nos 3)
- [x] `python run.py --play break --levels nr4` -> REPROVADA, t junto -1.12 (so NQ positivo, +0.07R)
