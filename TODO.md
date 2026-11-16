# TODO de testes (so isto se testa; o Antonio aprova itens novos)

## Fase 1 - base (parametros por defeito: tp 2R, stop 0.5 ATR, sessao rth)
- [ ] `python run.py --play bounce --levels pdhl`
- [ ] `python run.py --play bounce --levels pwhl`
- [ ] `python run.py --play bounce --levels swing1h`
- [ ] `python run.py --play bounce --levels round`
- [ ] `python run.py --play break --levels pdhl`
- [ ] `python run.py --play break --levels pwhl`
- [ ] `python run.py --play break --levels swing1h`
- [ ] `python run.py --play break --levels round`
- [ ] `python run.py --play fake --levels pdhl`
- [ ] `python run.py --play fake --levels pwhl`
- [ ] `python run.py --play fake --levels swing1h`
- [ ] `python run.py --play fake --levels round`

## Fase 2 - robustez (so para combinacoes da fase 1 com t junto >= 1.5 no dev)
Para cada uma: tp {1, 1.5, 3} x stop-atr {0.3, 1.0} e tambem --session all.
Acrescenta aqui as linhas concretas quando a fase 1 acabar. Uma variante so conta se a vizinhanca de
parametros tambem for positiva (nao um pico isolado).

## Fase 3 - holdout
So variantes com PASSA no dev e vizinhanca positiva. Uma vez cada. Ver CLAUDE.md.
