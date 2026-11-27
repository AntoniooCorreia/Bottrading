// Conta demo (paper trading) do Bottrading. Le precos publicos da Kraken, aplica as estrategias de tendencia K1
// (so long) a BTC/ETH/SOL e regista trades simuladas no Supabase. Nenhuma ordem real e enviada.
// Tudo em dolares (pares USD da Kraken; pedido do Antonio). 1% de risco por trade, 1 posicao por moeda, stop de 3 ATR, comissao Kraken 0.26%/lado.
// Conta 2 = demo EXPERIMENTAL (2026-11-22): perpetuos simulados (long/short), estrategias escolhidas SOZINHAS pelo agente
// (demo_pick.py -> state.demo_exp); sinais em engine.ts (igual a sr/demo_spec.py, testado). A conta 1 (K1) nao muda.
// Tres modos (pg_cron): ?mode=fast (de 5 em 5 min) = estrategias de scalping (5m/15m) das contas demo por estilo.
//   ?mode=stops  (cada minuto)  -> so le o preco atual (1 pedido) e fecha posicoes cujo stop foi tocado
//   sem mode     (de hora a hora) -> sinais de entrada/saida nas velas fechadas (como no backtest)
import { createClient } from "jsr:@supabase/supabase-js@2";
import { atr as atrN, entryAt, exitAt, TF_MIN, type Spec } from "./engine.ts";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const COINS: Record<string, string> = { btc: "XBTUSD", eth: "ETHUSD", sol: "SOLUSD" };   // K1 (conta 1)
// contas experimentais: uma estrategia pode correr em mais moedas (spec.coins; carteira de 8, #221)
const ALL_COINS: Record<string, string> = { ...COINS, xrp: "XRPUSD", ada: "ADAUSD", doge: "XDGUSD", link: "LINKUSD", avax: "AVAXUSD" };
const TICKER_KEY: [string, string][] = [["XBT", "btc"], ["ETH", "eth"], ["SOL", "sol"], ["XRP", "xrp"], ["ADA", "ada"], ["XDG", "doge"], ["LINK", "link"], ["AVAX", "avax"]];
const FEE = 0.0026;
type Bar = { t: number; o: number; h: number; l: number; c: number; v?: number };
type Strat = { name: string; tf: 1440 | 240; kind: "donchian" | "sma"; a: number; b?: number };
const STRATS: Strat[] = [
  { name: "k-donchian20-d", tf: 1440, kind: "donchian", a: 20, b: 10 },
  { name: "k-sma100-d", tf: 1440, kind: "sma", a: 100 },
  { name: "k-donchian55-4h", tf: 240, kind: "donchian", a: 55, b: 20 },
  { name: "k-sma200-4h", tf: 240, kind: "sma", a: 200 },
];
const NAMES: Record<string, string> = { btc: "BTC", eth: "ETH", sol: "SOL", xrp: "XRP", ada: "ADA", doge: "DOGE", link: "LINK", avax: "AVAX" };

async function ohlc(pair: string, interval: number): Promise<Bar[]> {
  const r = await fetch(`https://api.kraken.com/0/public/OHLC?pair=${pair}&interval=${interval}`);
  const j = await r.json();
  if (j.error?.length) throw new Error(`Kraken ${pair}: ${j.error.join(",")}`);
  const key = Object.keys(j.result).find((k) => k !== "last")!;
  const bars: Bar[] = j.result[key].map((x: any[]) => ({ t: x[0] * 1000, o: +x[1], h: +x[2], l: +x[3], c: +x[4], v: +x[6] }));
  return bars.slice(0, -1); // a ultima vela ainda nao fechou
}
async function ticker(): Promise<Record<string, number>> {
  const r = await fetch(`https://api.kraken.com/0/public/Ticker?pair=${Object.values(ALL_COINS).join(",")}`);
  const j = await r.json();
  if (j.error?.length) throw new Error(`Kraken ticker: ${j.error.join(",")}`);
  const out: Record<string, number> = {};
  for (const [k, v] of Object.entries<any>(j.result)) {
    const hit = TICKER_KEY.find(([s]) => k.includes(s));
    if (hit) out[hit[1]] = +v.c[0];
  }
  return out;
}
const sma = (b: Bar[], n: number) => b.slice(-n).reduce((s, x) => s + x.c, 0) / n;
function atr(b: Bar[], n = 14) {
  const tr = b.slice(-n).map((x, i, arr) => {
    const pc = i === 0 ? b[b.length - n - 1].c : arr[i - 1].c;
    return Math.max(x.h - x.l, Math.abs(x.h - pc), Math.abs(x.l - pc));
  });
  return tr.reduce((s, v) => s + v, 0) / n;
}
function entrySignal(s: Strat, b: Bar[]) {
  const last = b[b.length - 1];
  if (s.kind === "sma") return b.length > s.a && last.c > sma(b, s.a);
  const prev = b.slice(-s.a - 1, -1);
  return prev.length === s.a && last.c > Math.max(...prev.map((x) => x.h));
}
function exitSignal(s: Strat, b: Bar[]) {
  const last = b[b.length - 1];
  if (s.kind === "sma") return last.c < sma(b, s.a);
  const prev = b.slice(-s.b! - 1, -1);
  return last.c < Math.min(...prev.map((x) => x.l));
}
// ===================== DIARIO DO BOT (pedido do Antonio, 2026-11-27) =====================
// Cada trade fechada e analisada: quanto andou a favor (MFE) e contra (MAE) em R, quanto custaram as comissoes, quanto tempo durou.
// Numa perda, a causa decide a MUDANCA proposta (so parametros que o backtest consegue testar). O agente testa a mudanca no
// backtest 2019-2024 (journal_lab.py) e so a aplica se melhorar (regra fixa). Nunca se muda a estrategia ao vivo so por 1 perda.
const f2 = (x: number) => `${x >= 0 ? "+" : ""}${x.toFixed(2)}`;
async function analyze(p: any, exitPx: number, reason: string, pnl: number, fee: number) {
  const spec: any = p.spec ?? {}, side = Number(p.side ?? 1), entry = Number(p.entry_price), stop = Number(p.stop);
  const risk = Math.abs(entry - stop) || 1e-9, qty = Number(p.qty), riskEur = Number(p.risk_eur) || 1;
  const t0 = new Date(p.entry_time).getTime(), t1 = p.exit_time ? new Date(p.exit_time).getTime() : Date.now(), horas = (t1 - t0) / 3600000;
  const iv = horas < 55 ? 5 : 60;
  let mfe = 0, mae = 0;
  try {
    const bars = (await ohlc(ALL_COINS[p.coin] ?? COINS[p.coin], iv)).filter((x) => x.t + iv * 60000 > t0 && x.t < t1);
    for (const x of bars) { mfe = Math.max(mfe, side === 1 ? x.h - entry : entry - x.l); mae = Math.max(mae, side === 1 ? entry - x.l : x.h - entry); }
  } catch (_) { /* sem velas: segue so com o resultado */ }
  mfe = Math.max(mfe, side * (exitPx - entry)); mae = Math.max(mae, -side * (exitPx - entry));
  const mfeR = mfe / risk, maeR = mae / risk, r = pnl / riskEur, brutoR = side * qty * (exitPx - entry) / riskEur, custoR = fee / riskEur;
  const maxH = spec.max_hold && spec.tf ? spec.max_hold * TF_MIN[spec.tf] / 60 : null;
  const e = spec.entry ?? {}, base = { tp_r: spec.tp_r, stop_atr: spec.stop_atr, max_hold: spec.max_hold, vol_mult: spec.vol_mult, lo: e.lo, hi: e.hi };
  const metricas = { mfe_r: +mfeR.toFixed(2), mae_r: +maeR.toFixed(2), bruto_r: +brutoR.toFixed(2), custo_r: +custoR.toFixed(2), horas: +horas.toFixed(1), max_horas: maxH };
  const mk = (param: string, para: number, texto: string) => spec.tf ? { param, de: (base as any)[param] ?? null, para, texto,
    variante: `${p.strategy}~${param}${String(para).replace(".", "_")}` } : null;
  let causa = "ganho", porque = "", licao = "", mudanca: any = null;
  if (r >= 0) {
    porque = `Ganhou ${f2(r)}R (${reason}). Chegou a ${f2(mfeR)}R a favor e a ${f2(-maeR)}R contra, em ${horas.toFixed(1)}h.`;
    licao = "A estrategia fez o que o backtest espera.";
  } else if (brutoR > 0 && custoR > 0) {
    causa = "custos";
    porque = `O preco ate andou a favor (${f2(brutoR)}R antes de custos), mas comissoes, slippage e funding custaram ${custoR.toFixed(2)}R e a trade fechou em ${f2(r)}R.`;
    licao = "Ganhos pequenos nao pagam os custos: a saida tem de esperar por um movimento maior.";
    mudanca = e.kind === "rsi2" && spec.signal_exit ? mk("hi", Math.min(90, (e.hi ?? 65) + 10), `So sair quando o RSI(2) passar ${Math.min(90, (e.hi ?? 65) + 10)} (era ${e.hi}), para o ganho cobrir os custos.`)
      : spec.tp_r > 0 ? mk("tp_r", spec.tp_r + 1, `Alvo de ${spec.tp_r + 1}R em vez de ${spec.tp_r}R.`) : null;
  } else if (reason === "stop" && mfeR < 0.3) {
    causa = "falsa_partida";
    porque = `Bateu no stop em ${horas.toFixed(1)}h sem nunca ir a favor (no maximo ${f2(mfeR)}R). O sinal de entrada foi falso.`;
    licao = "Entrar so quando o sinal tem mais forca.";
    mudanca = e.kind === "breakout" ? mk("vol_mult", +((spec.vol_mult || 1) + 0.5).toFixed(1), `Pedir volume ${((spec.vol_mult || 1) + 0.5).toFixed(1)}x a media na rutura (era ${spec.vol_mult || "sem filtro"}).`)
      : e.kind === "rsi2" ? mk("lo", Math.max(2, Math.round((e.lo ?? 10) / 2)), `So entrar com RSI(2) abaixo de ${Math.max(2, Math.round((e.lo ?? 10) / 2))} (era ${e.lo}): sobrevenda mais extrema.`)
      : spec.stop_atr ? mk("stop_atr", spec.stop_atr + 1, `Stop de ${spec.stop_atr + 1} ATR em vez de ${spec.stop_atr} (menos ruido).`) : null;
  } else if (mfeR >= 1) {
    causa = "devolveu_lucro";
    porque = `Chegou a ${f2(mfeR)}R a favor e acabou em ${f2(r)}R (${reason}): devolveu o lucro todo.`;
    licao = "Quando a trade ja vai bem, convem fechar mais cedo.";
    const para = spec.tp_r > 1 || !spec.tp_r ? 1 : Math.max(0.75, spec.tp_r - 0.25);
    mudanca = mk("tp_r", para, `Alvo de ${para}R (era ${spec.tp_r || "sem alvo"}).`);
  } else if (reason.startsWith("tempo")) {
    causa = "sem_forca";
    porque = `Ficou ${horas.toFixed(1)}h sem chegar ao alvo nem ao stop (maximo a favor ${f2(mfeR)}R) e fechou no tempo maximo em ${f2(r)}R.`;
    licao = "Se o movimento nao vem depressa, normalmente nao vem: sair mais cedo.";
    mudanca = spec.max_hold > 2 ? mk("max_hold", Math.max(2, Math.round(spec.max_hold / 2)), `Tempo maximo de ${Math.max(2, Math.round(spec.max_hold / 2))} velas (era ${spec.max_hold}).`) : null;
  } else {
    causa = "perda_normal";
    porque = `Foi a favor ate ${f2(mfeR)}R, o mercado virou e fechou em ${f2(r)}R (${reason}). Perda normal: com o win rate do backtest, perdas destas sao esperadas.`;
    licao = "Nada a corrigir nesta trade; so muda se as perdas passarem o normal do backtest.";
  }
  return { causa, porque, licao, mudanca, metricas, r };
}
async function journal(p: any, exitPx: number, reason: string, pnl: number, fee: number, notify: boolean) {
  const a = await analyze(p, exitPx, reason, pnl, fee);
  const acc = Number(p.account ?? 1);
  const estado = a.mudanca ? (acc === 1 ? "precisa do OK do Antonio" : "proposta") : "sem mudanca";
  await sb.from("paper_journal").upsert({ account: acc, position_id: p.id, coin: p.coin, strategy: p.strategy, side: Number(p.side ?? 1),
    r: a.r, pnl, causa: a.causa, porque: a.porque, licao: a.licao, mudanca: a.mudanca, estado, metricas: a.metricas }, { onConflict: "position_id" });
  // pausa automatica: perdas acima do normal nesta conta/estrategia (6 seguidas ou -5R no total ao vivo)
  let pausa = "";
  if (acc >= 2 && a.r < 0) {
    const { data: hist } = await sb.from("paper_positions").select("r").eq("account", acc).eq("strategy", p.strategy).eq("status", "closed")
      .order("exit_time", { ascending: false }).limit(200);
    const rs = (hist ?? []).map((x: any) => Number(x.r));
    let seg = 0; for (const x of rs) { if (x < 0) seg++; else break; }
    const tot = rs.reduce((s, x) => s + x, 0);
    if (seg >= 6 || tot <= -5) {
      pausa = `${seg} perdas seguidas, ${f2(tot)}R no total ao vivo`;
      await sb.from("paper_pause").upsert({ account: acc, strategy: p.strategy, motivo: pausa, at: new Date().toISOString(),
        ate: new Date(Date.now() + 7 * 86400000).toISOString() });
    }
  }
  const txt = `\n\n📓 <b>Diario do bot</b>\n• Porque: ${a.porque}\n• Licao: ${a.licao}` +
    (a.mudanca ? `\n• Vai testar: ${a.mudanca.texto} ${acc === 1 ? "(K1 so muda com o teu OK)" : "(testa no backtest 2019-2024; so aplica se melhorar)"}` : "") +
    (pausa ? `\n• ⏸ Estrategia PAUSADA 7 dias nesta conta: ${pausa} (acima do normal)` : "");
  return notify ? txt : "";
}
async function journalMissing() {   // trades fechadas sem entrada no diario (ex.: antes de o diario existir)
  const { data: done } = await sb.from("paper_journal").select("position_id");
  const have = new Set((done ?? []).map((x: any) => Number(x.position_id)));
  const { data: cl } = await sb.from("paper_positions").select("*").eq("status", "closed").gte("exit_time", new Date(Date.now() - 7 * 86400000).toISOString());
  for (const p of cl ?? []) if (!have.has(Number(p.id))) {
    try { await journal({ ...p, account: p.account ?? 1 }, Number(p.exit_price), p.exit_reason ?? "", Number(p.pnl_eur), Number(p.fee_eur), false); } catch (_) { /* segue */ }
  }
}
const eur = (x: number) => `${x >= 0 ? "+" : ""}${x.toFixed(2)} $`;
async function tg(text: string) { await sb.rpc("paper_notify", { p_text: text }); }

async function closePos(open: any, exitPx: number, reason: string, balance: number) {
  const qty = Number(open.qty), entry = Number(open.entry_price);
  const fee = Number(open.fee_eur) + qty * exitPx * FEE;
  const pnl = qty * (exitPx - entry) - fee;
  const r = pnl / Number(open.risk_eur);
  balance += pnl;
  const { data: upd } = await sb.from("paper_positions").update({ status: "closed", exit_time: new Date().toISOString(),
    exit_price: exitPx, exit_reason: reason, pnl_eur: pnl, r, fee_eur: fee }).eq("id", open.id).eq("status", "open").select("id");
  if (!upd?.length) return null; // outra corrida ja fechou esta posicao
  const jt = await journal({ ...open, account: 1 }, exitPx, reason, pnl, fee, true).catch(() => "");
  await tg(`${pnl >= 0 ? "✅" : "❌"} <b>Demo: fechou ${NAMES[open.coin]}</b> (${open.strategy})\n• Motivo: ${reason}\n• Entrada ${entry.toFixed(2)} → saida ${exitPx.toFixed(2)} $\n• Resultado: <b>${eur(pnl)}</b> (${r >= 0 ? "+" : ""}${r.toFixed(2)}R)\n• Saldo: ${balance.toFixed(2)} $${jt}`);
  return { balance, pnl };
}

async function runStops() {
  const exp = await runStopsExp().catch((e) => ({ erro: String(e) }));
  const { data: opens } = await sb.from("paper_positions").select("*").eq("status", "open").eq("account", 1);
  if (!opens?.length) return { ok: true, mode: "stops", open: 0, exp };
  const px = await ticker();
  const { data: acc } = await sb.from("paper_account").select("*").eq("id", 1).single();
  let balance = Number(acc.balance), changed = false;
  const log: string[] = [];
  for (const p of opens) {
    const price = px[p.coin];
    if (price && price <= Number(p.stop)) {
      const res = await closePos(p, price, "stop", balance);
      if (res) { balance = res.balance; changed = true; log.push(`${p.coin}: stop ${res.pnl.toFixed(2)}`); }
    }
  }
  if (changed) await sb.from("paper_account").update({ balance }).eq("id", 1);
  return { ok: true, mode: "stops", open: opens.length, log, exp };
}

async function runHourly() {
  const log: string[] = [];
  const { data: acc } = await sb.from("paper_account").select("*").eq("id", 1).single();
  let balance = Number(acc.balance);
  let unreal = 0;
  let exp: any = null;
  try { exp = await runHourlyExp(); } catch (e) { exp = { erro: String(e) }; await tg(`⚠️ <b>Demo experimental: erro</b>\n${String(e).slice(0, 300)}`); }
  for (const [coin, pair] of Object.entries(COINS)) {
    const d = await ohlc(pair, 1440), h4 = await ohlc(pair, 240), h1 = await ohlc(pair, 60);
    const bars = { 1440: d, 240: h4 } as Record<number, Bar[]>;
    const price = h1[h1.length - 1].c;
    const { data: open } = await sb.from("paper_positions").select("*").eq("coin", coin).eq("status", "open").eq("account", 1).maybeSingle();
    if (open) {
      const s = STRATS.find((x) => x.name === open.strategy)!;
      const since = h1.filter((x) => x.t >= new Date(open.entry_time).getTime());
      const hitBar = since.find((x) => x.l <= Number(open.stop));
      let exitPx: number | null = null, reason = "";
      if (hitBar) { exitPx = Math.min(hitBar.o, Number(open.stop)); reason = "stop"; }
      else if (exitSignal(s, bars[s.tf])) { exitPx = price; reason = "sinal de saida"; }
      if (exitPx !== null) {
        const res = await closePos(open, exitPx, reason, balance);
        if (res) { balance = res.balance; log.push(`${coin}: fechou ${reason} ${res.pnl.toFixed(2)}`); }
        continue; // nao reabre na mesma corrida
      }
      unreal += Number(open.qty) * (price - Number(open.entry_price));
      continue;
    }
    // sem posicao: procura entrada (por ordem de prioridade)
    const { data: lastClosed } = await sb.from("paper_positions").select("exit_time").eq("coin", coin).eq("status", "closed").eq("account", 1)
      .order("exit_time", { ascending: false }).limit(1).maybeSingle();
    for (const s of STRATS) {
      const b = bars[s.tf];
      const candleClose = b[b.length - 1].t + s.tf * 60000;
      if (lastClosed && new Date(lastClosed.exit_time).getTime() >= candleClose) continue; // espera nova vela
      if (!entrySignal(s, b)) continue;
      const stopDist = 3 * atr(b);
      let risk = balance * 0.01;
      let qty = risk / stopDist;
      const maxNotional = balance / 3; // spot sem alavancagem: no maximo 1/3 do saldo por moeda
      if (qty * price > maxNotional) { qty = maxNotional / price; risk = qty * stopDist; }
      const fee = qty * price * FEE;
      await sb.from("paper_positions").insert({ coin, strategy: s.name, entry_price: price, stop: price - stopDist, qty,
        risk_eur: risk, fee_eur: fee });
      await tg(`🟢 <b>Demo: comprou ${NAMES[coin]}</b> (${s.name})\n• Preco: ${price.toFixed(2)} $\n• Stop: ${(price - stopDist).toFixed(2)} $ (${(stopDist / price * 100).toFixed(1)}% abaixo)\n• Quantidade: ${qty.toPrecision(4)} (${(qty * price).toFixed(2)} $)\n• Risco: ${risk.toFixed(2)} $ (${(risk / balance * 100).toFixed(2)}% do saldo)`);
      log.push(`${coin}: entrou ${s.name}`);
      break;
    }
  }
  await sb.from("paper_account").update({ balance, last_run: new Date().toISOString() }).eq("id", 1);
  await sb.from("paper_equity").insert({ balance, equity: balance + unreal, account: 1 });
  return { ok: true, balance, log, exp };
}

// ===================== CONTAS 2-4: DEMO EXPERIMENTAL POR ESTILO (perpetuos simulados) =====================
// 2 = swing (dias), 3 = day trade (horas), 4 = scalping (minutos). O agente escolhe as estrategias (demo_pick.py -> state.demo_exp.contas).
type ExpSpec = Spec & { ideia: string; num?: string };
type Conta = { id: number; nome: string; estrategias: ExpSpec[] };
type ExpCfg = { contas?: Conta[]; estrategias?: ExpSpec[]; fee: number; slip: number; funding_8h: number; risco: number };
const DIR = (s: number) => (s === 1 ? "LONG" : "SHORT");
const FAST = new Set(["5m", "15m"]);
const DEF = { fee: 0.0005, slip: 0.0002, funding_8h: 0.0001, risco: 0.01 };
async function expCfg(): Promise<ExpCfg | null> {
  const { data } = await sb.from("state").select("value").eq("key", "demo_exp").maybeSingle();
  const v = data?.value;
  if (!v) return null;
  if (!v.contas && v.estrategias?.length) v.contas = [{ id: 2, nome: "Experimental", estrategias: v.estrategias }];
  return v;
}
async function accName(id: number) {
  const { data } = await sb.from("paper_account").select("name").eq("id", id).maybeSingle();
  return data?.name ?? `Conta ${id}`;
}
async function closeExp(p: any, exitPx: number, reason: string, balance: number, cfg: typeof DEF, nome: string) {
  const qty = Number(p.qty), entry = Number(p.entry_price), side = Number(p.side);
  const hrs = (Date.now() - new Date(p.entry_time).getTime()) / 3600000;
  const fee = Number(p.fee_eur) + qty * exitPx * (cfg.fee + cfg.slip) + (hrs / 8) * cfg.funding_8h * qty * entry;
  const pnl = side * qty * (exitPx - entry) - fee;
  const r = pnl / Number(p.risk_eur);
  const { data: upd } = await sb.from("paper_positions").update({ status: "closed", exit_time: new Date().toISOString(),
    exit_price: exitPx, exit_reason: reason, pnl_eur: pnl, r, fee_eur: fee }).eq("id", p.id).eq("status", "open").select("id");
  if (!upd?.length) return null;
  balance += pnl;
  const jt = await journal(p, exitPx, reason, pnl, fee, true).catch(() => "");
  await tg(`🧪 ${pnl >= 0 ? "✅" : "❌"} <b>${nome}: fechou ${DIR(side)} ${NAMES[p.coin]}</b> (${p.strategy})\n• Motivo: ${reason}\n• Entrada ${entry.toFixed(2)} → saida ${exitPx.toFixed(2)} $\n• Resultado: <b>${eur(pnl)}</b> (${r >= 0 ? "+" : ""}${r.toFixed(2)}R)\n• Saldo: ${balance.toFixed(2)} $${jt}`);
  return { balance, pnl };
}
async function runStopsExp() {
  const { data: opens } = await sb.from("paper_positions").select("*").eq("status", "open").gte("account", 2);
  if (!opens?.length) return { open: 0 };
  const cfg = { ...DEF, ...((await expCfg()) ?? {}) } as any;
  const px = await ticker();
  for (const acc of [...new Set(opens.map((p: any) => Number(p.account)))]) {
    const { data: a } = await sb.from("paper_account").select("*").eq("id", acc).single();
    let balance = Number(a.balance), changed = false;
    for (const p of opens.filter((x: any) => Number(x.account) === acc)) {
      const price = px[p.coin], side = Number(p.side);
      if (!price) continue;
      let reason = "";
      if (side === 1 ? price <= Number(p.stop) : price >= Number(p.stop)) reason = "stop";
      else if (p.tp && (side === 1 ? price >= Number(p.tp) : price <= Number(p.tp))) reason = "alvo";
      if (!reason) continue;
      const res = await closeExp(p, price, reason, balance, cfg, a.name ?? `Conta ${acc}`);
      if (res) { balance = res.balance; changed = true; }
    }
    if (changed) await sb.from("paper_account").update({ balance }).eq("id", acc);
  }
  return { open: opens.length };
}
// fast=true: so estrategias de 5m/15m (cron de 5 em 5 min); fast=false: as outras (cron de hora a hora)
async function runExp(fast: boolean) {
  const cfg = await expCfg();
  const C = { ...DEF, ...(cfg ?? {}) } as any;
  const out: Record<string, any> = {};
  const btcD = await ohlc("XBTUSD", 1440);
  const cache: Record<string, Record<number, Bar[]>> = {};
  const bars = async (coin: string, tf: number) => {
    cache[coin] ??= {};
    if (!cache[coin][tf]) cache[coin][tf] = coin === "btc" && tf === 1440 ? btcD : await ohlc(ALL_COINS[coin], tf);
    return cache[coin][tf];
  };
  const { data: accs } = await sb.from("paper_account").select("*").gte("id", 2).order("id");
  const { data: pz } = await sb.from("paper_pause").select("account,strategy").gt("ate", new Date().toISOString());
  const paused = new Set((pz ?? []).map((x: any) => `${x.account}|${x.strategy}`));
  if (!fast) await journalMissing().catch(() => null);
  for (const a of accs ?? []) {
    const nome = a.name ?? `Conta ${a.id}`, log: string[] = [];
    let balance = Number(a.balance), unreal = 0;
    const conta = cfg?.contas?.find((x) => Number(x.id) === Number(a.id));
    // 1) gerir posicoes abertas desta conta (cada uma com a sua spec gravada)
    const { data: opens } = await sb.from("paper_positions").select("*").eq("status", "open").eq("account", a.id);
    for (const p of opens ?? []) {
      const s: Spec = p.spec, side = Number(p.side), tfm = TF_MIN[s.tf];
      if (FAST.has(s.tf) !== fast) {   // a outra corrida trata desta; aqui so conta para o saldo com posicoes
        const h1 = await bars(p.coin, fast ? 5 : 60);
        unreal += side * Number(p.qty) * (h1[h1.length - 1].c - Number(p.entry_price));
        continue;
      }
      const fine = await bars(p.coin, fast ? 5 : 60), price = fine[fine.length - 1].c;
      const since = fine.filter((x) => x.t >= new Date(p.entry_time).getTime());
      let exitPx: number | null = null, reason = "";
      for (const x of since) {   // conservador: na mesma vela, o stop conta antes do alvo
        if (side === 1 ? x.l <= Number(p.stop) : x.h >= Number(p.stop)) { exitPx = side === 1 ? Math.min(x.o, Number(p.stop)) : Math.max(x.o, Number(p.stop)); reason = "stop"; break; }
        if (p.tp && (side === 1 ? x.h >= Number(p.tp) : x.l <= Number(p.tp))) { exitPx = Number(p.tp); reason = "alvo"; break; }
      }
      if (exitPx === null) {
        const b = await bars(p.coin, tfm);
        const held = b.filter((x) => x.t >= new Date(p.entry_time).getTime() - 1).length;
        if (s.max_hold && held >= s.max_hold) { exitPx = price; reason = `tempo maximo (${s.max_hold} velas)`; }
        else if (exitAt(b, b.length - 1, s)) { exitPx = price; reason = "sinal de saida"; }
      }
      if (exitPx !== null) {
        const res = await closeExp(p, exitPx, reason, balance, C, nome);
        if (res) { balance = res.balance; log.push(`${p.coin} ${p.strategy}: ${reason}`); }
        continue;
      }
      unreal += side * Number(p.qty) * (price - Number(p.entry_price));
    }
    // 2) entradas das estrategias escolhidas pelo agente para esta conta
    if (conta) {
      const { data: stillOpen } = await sb.from("paper_positions").select("coin,strategy").eq("status", "open").eq("account", a.id);
      const busy = new Set((stillOpen ?? []).map((x: any) => `${x.coin}|${x.strategy}`));
      for (const s of conta.estrategias) {
        if (FAST.has(s.tf) !== fast) continue;
        if (paused.has(`${a.id}|${s.ideia}`)) continue;   // pausa automatica do diario (perdas acima do normal)
        const tfm = TF_MIN[s.tf];
        const coins: string[] = (s as any).coins ?? Object.keys(COINS), maxOpen = Number((s as any).max_open ?? 0);
        for (const coin of coins) {
          if (busy.has(`${coin}|${s.ideia}`)) continue;
          if (maxOpen && [...busy].filter((k) => k.endsWith(`|${s.ideia}`)).length >= maxOpen) break;   // como o --max-open do backtest
          const b = await bars(coin, tfm), last = b[b.length - 1];
          const candleClose = last.t + tfm * 60000;
          if (Date.now() - candleClose > Math.min(2 * 3600000, tfm * 60000)) continue;   // so logo a seguir ao fecho da vela
          const { data: lc } = await sb.from("paper_positions").select("exit_time").eq("account", a.id).eq("coin", coin)
            .eq("strategy", s.ideia).eq("status", "closed").order("exit_time", { ascending: false }).limit(1).maybeSingle();
          if (lc && new Date(lc.exit_time).getTime() >= candleClose) continue;
          if (!entryAt(b, b.length - 1, s, btcD)) continue;
          const fine = await bars(coin, fast ? 5 : 60), price = fine[fine.length - 1].c;
          const stopDist = s.stop_atr * atrN(b);
          let risk = balance * C.risco, qty = risk / stopDist;
          if (qty * price > balance) { qty = balance / price; risk = qty * stopDist; }   // no maximo 1x o saldo por posicao
          const side = s.side, stop = price - side * stopDist, tp = s.tp_r > 0 ? price + side * s.tp_r * stopDist : null;
          const fee = qty * price * (C.fee + C.slip);
          await sb.from("paper_positions").insert({ account: a.id, coin, strategy: s.ideia, side, entry_price: price, stop, tp, qty,
            risk_eur: risk, fee_eur: fee, spec: s });
          busy.add(`${coin}|${s.ideia}`);
          await tg(`🧪 ${side === 1 ? "🟢" : "🔴"} <b>${nome}: ${DIR(side)} ${NAMES[coin]}</b> (${s.num ?? ""} ${s.ideia})\n• Preco: ${price.toFixed(2)} $\n• Stop: ${stop.toFixed(2)} $ (${(stopDist / price * 100).toFixed(1)}%)${tp ? `\n• Alvo: ${tp.toFixed(2)} $` : ""}\n• Risco: ${risk.toFixed(2)} $ (${(risk / balance * 100).toFixed(2)}% do saldo)\n• Escolhida pelo agente (nao aprovada; teste ao vivo)`);
          log.push(`${coin}: entrou ${DIR(side)} ${s.ideia}`);
        }
      }
    }
    await sb.from("paper_account").update({ balance, last_run: new Date().toISOString() }).eq("id", a.id);
    if (!fast) await sb.from("paper_equity").insert({ balance, equity: balance + unreal, account: a.id });
    out[a.id] = { balance, log };
  }
  return out;
}
async function runHourlyExp() { return await runExp(false); }

Deno.serve(async (req) => {
  const mode = new URL(req.url).searchParams.get("mode");
  try {
    const out = mode === "journal" ? (await journalMissing(), { ok: true, mode: "journal" }) : mode === "stops" ? await runStops() : mode === "fast" ? { ok: true, mode: "fast", exp: await runExp(true) } : await runHourly();
    return new Response(JSON.stringify(out), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    if (mode !== "stops") await tg(`⚠️ <b>Demo: erro</b>\n${String(e).slice(0, 300)}`); // falhas do modo rapido nao enchem o Telegram
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }
});
