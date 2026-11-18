"""
Bot da conta DEMO (MT5, STARTRADER) para a carteira C5 - corre no PC do Antonio, nunca na nuvem.

Faz o mesmo que o backtest (portfolio.py --max-open 3 --region-cap 1 --month-stop 3):
  * 4 estrategias diarias (rsi2-dip-d, ibs-dip-d, down3-d, ibs-bear-d) nos 10 indices, com o MESMO codigo
    de sr/swing_ideas.py e o MESMO motor de sr/swing.py (sinal no fecho do dia, entrada na abertura seguinte,
    stop 3 ATR, saidas por sinal ou ao fim de 10 dias)
  * 1% da conta de risco por trade (stop a 3 ATR), no maximo 3 trades abertas, 1 por indice, 1 por regiao
  * no mes em que as trades fechadas perderem 3% nao abre mais nenhuma ate ao mes seguinte

Como funciona: de minuto a minuto ve se comecou um dia novo (vela D1 nova) em cada indice. Quando comeca, corre o
motor com as velas diarias do MT5 e faz o que o backtest faria nessa abertura: fecha as trades que o motor fechou
e abre as novas (se as regras de risco deixarem).

Uso (no PC, com o MT5 aberto e ligado a conta demo):
  pip install MetaTrader5 pandas numpy
  python live/c5_live.py --check          # liga ao MT5, mostra a conta, os simbolos e os sinais de hoje (nao negoceia)
  python live/c5_live.py                  # modo ensaio: diz o que faria, nao envia ordens
  python live/c5_live.py --live           # envia ordens (SO aceita conta DEMO)
  python live/c5_live.py --live --once    # uma passagem e sai (para o Agendador de Tarefas do Windows)
Simbolos: edita live/config.json (criado na primeira corrida) se os nomes do teu MT5 forem diferentes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sr.data import CARTEIRA, SPEC  # noqa: E402
from sr.swing import FUT_COST, run_positions  # noqa: E402
from sr.swing_ideas import IDEAS  # noqa: E402

IDEIAS = ["rsi2-dip-d", "ibs-dip-d", "down3-d", "ibs-bear-d"]
REGIAO = {"nq": "eua", "es": "eua", "dow": "eua", "dax": "europa", "ftse": "europa", "estx": "europa",
          "cac": "europa", "nikkei": "asia", "asx": "asia", "hsi": "asia"}
MAX_OPEN, REGION_CAP, MONTH_STOP, RISCO_PCT = 3, 1, 3.0, 1.0
MAGIC = 50505
N_BARS = 600
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")
STATE = os.path.join(HERE, "state.json")
DIARIO = os.path.join(HERE, "diario.log")
# nomes habituais na STARTRADER (confirma com --check e corrige em live/config.json)
SIMBOLOS = {"nq": "NAS100", "es": "SP500", "dow": "DJ30", "dax": "GER40", "ftse": "UK100", "nikkei": "JP225",
            "estx": "EU50", "cac": "FRA40", "asx": "AUS200", "hsi": "HK50"}
ALTERNATIVAS = {"nq": ["NAS100", "US100", "USTEC", "NDX100"], "es": ["SP500", "US500", "SPX500"],
                "dow": ["DJ30", "US30", "WS30"], "dax": ["GER40", "DE40", "GER30", "DAX40"], "ftse": ["UK100", "FTSE100"],
                "nikkei": ["JP225", "JPN225", "NIK225"], "estx": ["EU50", "EUSTX50", "STOXX50"], "cac": ["FRA40", "F40"],
                "asx": ["AUS200", "AU200"], "hsi": ["HK50", "HSI50", "HK33"]}


# ---------------------------------------------------------------- logica (sem MT5: testada em tests/test_live.py)
def motor_agora(bars: pd.DataFrame, idea: str, mk: str, abertura: float):
    """bars: velas diarias COMPLETAS (indice = dia). abertura: preco de abertura do dia novo.
    Junta uma vela 'hoje' so com a abertura e corre o motor do backtest. Devolve a trade aberta do motor (ou None).
    Se a trade aberta comecou 'hoje', e uma entrada nova; o campo 'nova' diz isso."""
    fn, tf, st, tp, mh = IDEAS[idea]
    hoje = bars.index[-1] + pd.Timedelta(days=1)
    b = pd.concat([bars[["open", "high", "low", "close"]],
                   pd.DataFrame({"open": [abertura], "high": [abertura], "low": [abertura], "close": [abertura]},
                                index=[hoje])])
    _, cur = run_positions(b, fn(b), st, SPEC[mk]["cost_pts"], FUT_COST[mk], tp, mh, return_open=True)
    if cur is None:
        return None
    cur["nova"] = cur["t"] == hoje
    cur["dia"] = "hoje" if cur["nova"] else pd.Timestamp(cur["t"]).strftime("%Y-%m-%d")
    return cur


def decidir(estados: dict, posicoes: list, mes_pct: float, mercados_agora: list) -> list:
    """estados: {(mk, ideia): trade aberta do motor ou None} para os indices com dia novo agora.
    posicoes: [{"mk", "ideia", "dia", ...}] abertas na conta. mes_pct: resultado fechado do mes em % da conta.
    Devolve acoes pela ordem: [("fechar", pos, motivo), ("abrir", mk, ideia, trade_do_motor), ("saltar", mk, ideia, motivo)]."""
    acoes, abertas = [], []
    for p in posicoes:
        if p["mk"] in mercados_agora:
            cur = estados.get((p["mk"], p["ideia"]))
            if cur is None or cur["nova"] or cur["dia"] != p["dia"]:
                acoes.append(("fechar", p, "o motor saiu (sinal, stop ou 10 dias)"))
                continue
        abertas.append(p)
    for mk in CARTEIRA:
        if mk not in mercados_agora:
            continue
        for ideia in IDEIAS:
            cur = estados.get((mk, ideia))
            if not cur or not cur["nova"]:
                continue
            if len(abertas) >= MAX_OPEN:
                motivo = f"ja ha {MAX_OPEN} trades abertas"
            elif any(p["mk"] == mk for p in abertas):
                motivo = "ja ha uma trade neste indice"
            elif sum(REGIAO[p["mk"]] == REGIAO[mk] for p in abertas) >= REGION_CAP:
                motivo = f"ja ha uma trade na regiao {REGIAO[mk]}"
            elif mes_pct <= -MONTH_STOP:
                motivo = f"o mes ja perdeu {mes_pct:.1f}% (paragem a -{MONTH_STOP:g}%)"
            else:
                acoes.append(("abrir", mk, ideia, cur))
                abertas.append({"mk": mk, "ideia": ideia, "dia": "hoje"})
                continue
            acoes.append(("saltar", mk, ideia, motivo))
    return acoes


def lotes(risco_dinheiro: float, perda_1_lote: float, minimo: float, passo: float, maximo: float) -> float:
    """Lotes para perder `risco_dinheiro` no stop, arredondado PARA BAIXO ao passo do simbolo (nunca arrisca mais de 1%)."""
    if perda_1_lote <= 0:
        return 0.0
    v = math.floor(risco_dinheiro / perda_1_lote / passo + 1e-9) * passo
    v = min(v, maximo)
    return round(v, 8) if v >= minimo else 0.0


# ---------------------------------------------------------------- MT5
def log(msg: str, painel: bool = False, pontos: list | None = None):
    linha = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(linha + ("".join(f"\n    - {p}" for p in pontos) if pontos else ""))
    with open(DIARIO, "a", encoding="utf-8") as f:
        f.write(linha + "".join(f" | {p}" for p in (pontos or [])) + "\n")
    if painel and os.environ.get("BT_WRITE_TOKEN"):
        try:
            from sr import supa
            supa.log_event("demo", msg, pontos or [])
        except Exception as e:  # o painel nunca pode parar o bot
            print(f"   (painel falhou: {e})")


def ler_json(path, defeito):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return defeito


def gravar_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


class MT5:
    def __init__(self, live: bool):
        import MetaTrader5 as mt5
        self.mt5, self.live = mt5, live
        if not mt5.initialize():
            raise SystemExit(f"Nao consegui ligar ao MT5 (esta aberto e com sessao iniciada?): {mt5.last_error()}")
        self.conta = mt5.account_info()
        if live and self.conta.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            raise SystemExit("Esta conta NAO e demo. Este bot so envia ordens em conta demo.")
        cfg = ler_json(CONFIG, None)
        if cfg is None:
            cfg = {"simbolos": self.adivinhar_simbolos()}
            gravar_json(CONFIG, cfg)
            log(f"Criei {CONFIG}; confirma os simbolos.")
        self.sim = cfg["simbolos"]

    def adivinhar_simbolos(self):
        todos = {s.name for s in (self.mt5.symbols_get() or [])}
        out = {}
        for mk, alts in ALTERNATIVAS.items():
            out[mk] = next((a for a in alts if a in todos), next((s for s in todos for a in alts if s.startswith(a)), SIMBOLOS[mk]))
        return out

    def velas(self, mk):
        s = self.sim[mk]
        self.mt5.symbol_select(s, True)
        r = self.mt5.copy_rates_from_pos(s, self.mt5.TIMEFRAME_D1, 0, N_BARS)
        if r is None or len(r) < 260:
            return None, None
        df = pd.DataFrame(r)
        df.index = pd.to_datetime(df["time"], unit="s").dt.normalize()
        df = df[df.index.dayofweek < 5]          # so dias de semana (igual ao backtest C10, --sem-domingos)
        completas, hoje = df.iloc[:-1], df.iloc[-1]
        return completas[["open", "high", "low", "close"]].astype(float), (hoje.name, float(hoje["open"]))

    def posicoes(self, estado):
        out = []
        for p in self.mt5.positions_get() or []:
            if p.magic != MAGIC:
                continue
            info = estado["posicoes"].get(str(p.ticket))
            if info is None:      # sem registo local: tenta ler o comentario "C5|ideia|AAAAMMDD"
                parts = (p.comment or "").split("|")
                mk = next((k for k, v in self.sim.items() if v == p.symbol), None)
                if len(parts) < 3 or mk is None:
                    continue
                d = parts[2]
                info = {"mk": mk, "ideia": parts[1], "dia": f"{d[:4]}-{d[4:6]}-{d[6:8]}"}
            out.append({**info, "ticket": p.ticket, "volume": p.volume, "simbolo": p.symbol, "lucro": p.profit})
        return out

    def resultado_mes(self):
        agora = datetime.now()
        ini = datetime(agora.year, agora.month, 1)
        deals = self.mt5.history_deals_get(ini, agora + timedelta(days=1)) or []
        tot = sum(d.profit + d.commission + d.swap for d in deals
                  if d.magic == MAGIC and d.entry == self.mt5.DEAL_ENTRY_OUT)
        conta = self.mt5.account_info()
        base = conta.balance - tot
        return tot, (tot / base * 100 if base > 0 else 0.0)

    def _enchimento(self, s):
        fm = self.mt5.symbol_info(s).filling_mode
        return self.mt5.ORDER_FILLING_FOK if fm & 1 else self.mt5.ORDER_FILLING_IOC if fm & 2 else self.mt5.ORDER_FILLING_RETURN

    def abrir(self, mk, ideia, risco_pts, dia):
        mt5, s = self.mt5, self.sim[mk]
        info, tick = mt5.symbol_info(s), mt5.symbol_info_tick(s)
        preco = tick.ask
        sl = preco - risco_pts
        perda = -(mt5.order_calc_profit(mt5.ORDER_TYPE_BUY, s, 1.0, preco, sl) or 0.0)
        conta = mt5.account_info()
        vol = lotes(conta.equity * RISCO_PCT / 100, perda, info.volume_min, info.volume_step, info.volume_max)
        if vol <= 0:
            return None, f"conta pequena demais para 1% neste indice (minimo {info.volume_min} lotes arrisca {perda * info.volume_min:.0f})"
        sl = round(sl, info.digits)
        if not self.live:
            return None, f"ENSAIO: comprava {vol} lotes de {s} a ~{preco}, stop {sl} (arrisca ~{perda * vol:.0f} {conta.currency})"
        req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": s, "volume": vol, "type": mt5.ORDER_TYPE_BUY, "price": preco,
               "sl": sl, "deviation": 50, "magic": MAGIC, "comment": f"C5|{ideia}|{dia.replace('-', '')}",
               "type_time": mt5.ORDER_TIME_GTC, "type_filling": self._enchimento(s)}
        r = mt5.order_send(req)
        if r is None or r.retcode != mt5.TRADE_RETCODE_DONE:
            return None, f"ordem recusada: {getattr(r, 'retcode', None)} {getattr(r, 'comment', mt5.last_error())}"
        return r.order, f"comprou {vol} lotes de {s} a {r.price}, stop {sl} (arrisca ~{perda * vol:.0f} {conta.currency})"

    def fechar(self, pos):
        mt5, s = self.mt5, pos["simbolo"]
        if not self.live:
            return True, f"ENSAIO: fechava {pos['volume']} lotes de {s} (resultado atual {pos['lucro']:.0f})"
        tick = mt5.symbol_info_tick(s)
        req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": s, "volume": pos["volume"], "type": mt5.ORDER_TYPE_SELL,
               "position": pos["ticket"], "price": tick.bid, "deviation": 50, "magic": MAGIC,
               "comment": "C5|saida", "type_time": mt5.ORDER_TIME_GTC, "type_filling": self._enchimento(s)}
        r = mt5.order_send(req)
        if r is None or r.retcode != mt5.TRADE_RETCODE_DONE:
            return False, f"fecho recusado: {getattr(r, 'retcode', None)} {getattr(r, 'comment', mt5.last_error())}"
        return True, f"fechou {pos['volume']} lotes de {s} a {r.price} (resultado ~{pos['lucro']:.0f})"


def passagem(b: MT5, estado: dict, forcar: bool = False):
    """Ve que indices comecaram um dia novo e trata deles."""
    estados, agora_mks, dias = {}, [], {}
    for mk in CARTEIRA:
        bars, hoje = b.velas(mk)
        if bars is None:
            continue
        dia_novo = hoje[0].strftime("%Y-%m-%d")
        if not forcar and estado["ultimo_dia"].get(mk) == dia_novo:
            continue
        agora_mks.append(mk)
        dias[mk] = dia_novo
        for ideia in IDEIAS:
            estados[(mk, ideia)] = motor_agora(bars, ideia, mk, hoje[1])
    if not agora_mks:
        return
    pos = b.posicoes(estado)
    eur, mes_pct = b.resultado_mes()
    acoes = decidir(estados, pos, mes_pct, agora_mks)
    for a in acoes:
        if a[0] == "fechar":
            ok, txt = b.fechar(a[1])
            log(f"SAIDA {a[1]['mk']} {a[1]['ideia']}: {txt}", painel=b.live, pontos=[a[2]])
            if ok and b.live:
                estado["posicoes"].pop(str(a[1]["ticket"]), None)
        elif a[0] == "abrir":
            _, mk, ideia, cur = a
            ticket, txt = b.abrir(mk, ideia, cur["risk"], dias[mk])
            log(f"ENTRADA {mk} {ideia}: {txt}", painel=b.live,
                pontos=[f"stop a 3 ATR = {cur['risk']:.1f} pontos; risco 1% da conta"])
            if ticket:
                estado["posicoes"][str(ticket)] = {"mk": mk, "ideia": ideia, "dia": dias[mk]}
        else:
            log(f"SINAL IGNORADO {a[1]} {a[2]}: {a[3]}")
    for mk in agora_mks:
        estado["ultimo_dia"][mk] = dias[mk]
    if not acoes:
        log(f"Dia novo em {', '.join(agora_mks)}: nada a fazer (mes {mes_pct:+.1f}%, {len(pos)} trades abertas)")
    gravar_json(STATE, estado)


def check(b: MT5):
    c = b.conta
    print(f"Conta {c.login} {c.server} | {'DEMO' if c.trade_mode == b.mt5.ACCOUNT_TRADE_MODE_DEMO else 'REAL (o bot nao negoceia aqui)'}"
          f" | saldo {c.balance:.2f} {c.currency} | capital {c.equity:.2f}")
    print(f"Simbolos (de {CONFIG}):")
    for mk in CARTEIRA:
        s = b.sim[mk]
        info = b.mt5.symbol_info(s)
        bars, hoje = b.velas(mk) if info else (None, None)
        if info is None:
            print(f"  {mk:7s} {s:10s} NAO EXISTE neste MT5 -> corrige em config.json")
            continue
        sinais = []
        if bars is not None:
            for ideia in IDEIAS:
                cur = motor_agora(bars, ideia, mk, hoje[1])
                if cur:
                    sinais.append(f"{ideia}: {'ENTRADA HOJE' if cur['nova'] else 'em trade desde ' + cur['dia']}")
        print(f"  {mk:7s} {s:10s} ok | {len(bars) if bars is not None else 0} dias | ultimo dia completo "
              f"{bars.index[-1]:%Y-%m-%d} | {'; '.join(sinais) or 'sem sinal'}" if bars is not None else
              f"  {mk:7s} {s:10s} poucas velas diarias")
    tot, pct = b.resultado_mes()
    print(f"Resultado fechado do mes (bot): {tot:.2f} ({pct:+.2f}%) | trades do bot abertas: {len(b.posicoes(ler_json(STATE, {'posicoes': {}})))}")


def main():
    ap = argparse.ArgumentParser(description="Bot da conta demo para a carteira C5")
    ap.add_argument("--live", action="store_true", help="envia ordens (so em conta demo)")
    ap.add_argument("--once", action="store_true", help="uma passagem e sai")
    ap.add_argument("--check", action="store_true", help="mostra conta, simbolos e sinais; nao negoceia")
    a = ap.parse_args()
    b = MT5(live=a.live)
    if a.check:
        check(b)
        return
    estado = ler_json(STATE, {"ultimo_dia": {}, "posicoes": {}})
    log(f"Bot C5 iniciado ({'DEMO - envia ordens' if a.live else 'ENSAIO - nao envia ordens'}) na conta {b.conta.login}",
        painel=a.live)
    primeira = True
    while True:
        try:
            passagem(b, estado, forcar=False)
        except Exception as e:
            log(f"ERRO: {e}", painel=a.live)
        if a.once:
            break
        if primeira:
            primeira = False
        time.sleep(60)


if __name__ == "__main__":
    main()
