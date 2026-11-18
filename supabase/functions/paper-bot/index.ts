// Conta demo (paper trading) do Bottrading. Le precos publicos da Kraken, aplica as estrategias de tendencia K1
// (so long) a BTC/ETH/SOL e regista trades simuladas no Supabase. Nenhuma ordem real e enviada.
// 1% de risco por trade, 1 posicao por moeda, stop de 3 ATR, comissao Kraken 0.26%/lado.
// Dois modos (pg_cron):
//   ?mode=stops  (cada minuto)  -> so le o preco atual (1 pedido) e fecha posicoes cujo stop foi tocado
//   sem mode     (de hora a hora) -> sinais de entrada/saida nas velas fechadas (como no backtest)
import { createClient } from "jsr:@supabase/supabase-js@2";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const COINS: Record<string, string> = { btc: "XBTEUR", eth: "ETHEUR", sol: "SOLEUR" };
const FEE = 0.0026;
type Bar = { t: number; o: number; h: number; l: number; c: number };
type Strat = { name: string; tf: 1440 | 240; kind: "donchian" | "sma"; a: number; b?: number };
const STRATS: Strat[] = [
  { name: "k-donchian20-d", tf: 1440, kind: "donchian", a: 20, b: 10 },
  { name: "k-sma100-d", tf: 1440, kind: "sma", a: 100 },
  { name: "k-donchian55-4h", tf: 240, kind: "donchian", a: 55, b: 20 },
  { name: "k-sma200-4h", tf: 240, kind: "sma", a: 200 },
];
const NAMES: Record<string, string> = { btc: "BTC", eth: "ETH", sol: "SOL" };

async function ohlc(pair: string, interval: number): Promise<Bar[]> {
  const r = await fetch(`https://api.kraken.com/0/public/OHLC?pair=${pair}&interval=${interval}`);
  const j = await r.json();
  if (j.error?.length) throw new Error(`Kraken ${pair}: ${j.error.join(",")}`);
  const key = Object.keys(j.result).find((k) => k !== "last")!;
  const bars: Bar[] = j.result[key].map((x: any[]) => ({ t: x[0] * 1000, o: +x[1], h: +x[2], l: +x[3], c: +x[4] }));
  return bars.slice(0, -1); // a ultima vela ainda nao fechou
}
async function ticker(): Promise<Record<string, number>> {
  const r = await fetch(`https://api.kraken.com/0/public/Ticker?pair=${Object.values(COINS).join(",")}`);
  const j = await r.json();
  if (j.error?.length) throw new Error(`Kraken ticker: ${j.error.join(",")}`);
  const out: Record<string, number> = {};
  for (const [k, v] of Object.entries<any>(j.result)) {
    const coin = k.includes("XBT") ? "btc" : k.includes("ETH") ? "eth" : k.includes("SOL") ? "sol" : null;
    if (coin) out[coin] = +v.c[0];
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
const eur = (x: number) => `${x >= 0 ? "+" : ""}${x.toFixed(2)} €`;
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
  await tg(`${pnl >= 0 ? "✅" : "❌"} <b>Demo: fechou ${NAMES[open.coin]}</b> (${open.strategy})\n• Motivo: ${reason}\n• Entrada ${entry.toFixed(2)} → saida ${exitPx.toFixed(2)} €\n• Resultado: <b>${eur(pnl)}</b> (${r >= 0 ? "+" : ""}${r.toFixed(2)}R)\n• Saldo: ${balance.toFixed(2)} €`);
  return { balance, pnl };
}

async function runStops() {
  const { data: opens } = await sb.from("paper_positions").select("*").eq("status", "open");
  if (!opens?.length) return { ok: true, mode: "stops", open: 0 };
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
  return { ok: true, mode: "stops", open: opens.length, log };
}

async function runHourly() {
  const log: string[] = [];
  const { data: acc } = await sb.from("paper_account").select("*").eq("id", 1).single();
  let balance = Number(acc.balance);
  let unreal = 0;
  for (const [coin, pair] of Object.entries(COINS)) {
    const d = await ohlc(pair, 1440), h4 = await ohlc(pair, 240), h1 = await ohlc(pair, 60);
    const bars = { 1440: d, 240: h4 } as Record<number, Bar[]>;
    const price = h1[h1.length - 1].c;
    const { data: open } = await sb.from("paper_positions").select("*").eq("coin", coin).eq("status", "open").maybeSingle();
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
    const { data: lastClosed } = await sb.from("paper_positions").select("exit_time").eq("coin", coin).eq("status", "closed")
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
      await tg(`🟢 <b>Demo: comprou ${NAMES[coin]}</b> (${s.name})\n• Preco: ${price.toFixed(2)} €\n• Stop: ${(price - stopDist).toFixed(2)} € (${(stopDist / price * 100).toFixed(1)}% abaixo)\n• Quantidade: ${qty.toPrecision(4)} (${(qty * price).toFixed(2)} €)\n• Risco: ${risk.toFixed(2)} € (${(risk / balance * 100).toFixed(2)}% do saldo)`);
      log.push(`${coin}: entrou ${s.name}`);
      break;
    }
  }
  await sb.from("paper_account").update({ balance, last_run: new Date().toISOString() }).eq("id", 1);
  await sb.from("paper_equity").insert({ balance, equity: balance + unreal });
  return { ok: true, balance, log };
}

Deno.serve(async (req) => {
  const mode = new URL(req.url).searchParams.get("mode");
  try {
    const out = mode === "stops" ? await runStops() : await runHourly();
    return new Response(JSON.stringify(out), { headers: { "Content-Type": "application/json" } });
  } catch (e) {
    if (mode !== "stops") await tg(`⚠️ <b>Demo: erro</b>\n${String(e).slice(0, 300)}`); // falhas do modo rapido nao enchem o Telegram
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 500 });
  }
});
