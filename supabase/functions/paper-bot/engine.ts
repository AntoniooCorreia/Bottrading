// Motor de sinais da conta demo EXPERIMENTAL. Espelho exato de sr/demo_spec.py (tests/test_demo_spec.py compara os dois).
// Sem dependencias: corre no Deno (Edge Function) e no node (teste).
export type Bar = { t: number; o: number; h: number; l: number; c: number };
export type Spec = {
  tf: "1h" | "4h" | "1d"; side: 1 | -1;
  entry: { kind: "breakout" | "rsi2" | "lowclose" | "above_sma"; n?: number; lo?: number; hi?: number };
  trend_ema: number; btc: "bull" | "bear" | "" | null; stop_atr: number; tp_r: number; max_hold: number; signal_exit: boolean;
};
export const TF_MIN: Record<string, number> = { "1h": 60, "4h": 240, "1d": 1440 };

export function emaSeries(c: number[], n: number): number[] {
  const a = 2 / (n + 1), out: number[] = [];
  c.forEach((x, i) => out.push(i === 0 ? x : a * x + (1 - a) * out[i - 1]));
  return out;
}
export function rsiSeries(c: number[], n = 2): number[] {
  const a = 1 / n, out: number[] = [NaN];
  let up = 0, dn = 0;
  for (let i = 1; i < c.length; i++) {
    const d = c[i] - c[i - 1];
    const u = Math.max(d, 0), v = Math.max(-d, 0);
    if (i === 1) { up = u; dn = v; } else { up = a * u + (1 - a) * up; dn = a * v + (1 - a) * dn; }
    out.push(dn === 0 ? NaN : 100 - 100 / (1 + up / dn));
  }
  return out;
}
// BTC fechou o dia anterior (UTC) acima da media de 200 dias? (valor do dia D vale a partir de D+1 00:00)
export function btcBullAt(btcDaily: Bar[], t: number): boolean | null {
  let k = -1;
  for (let i = btcDaily.length - 1; i >= 0; i--) if (btcDaily[i].t + 86400000 <= t) { k = i; break; }
  if (k < 199) return null;
  let s = 0;
  for (let i = k - 199; i <= k; i++) s += btcDaily[i].c;
  return btcDaily[k].c > s / 200;
}
export function atr(b: Bar[], n = 14): number {
  const m = b.length;
  let s = 0;
  for (let i = m - n; i < m; i++) {
    const pc = b[i - 1].c;
    s += Math.max(b[i].h - b[i].l, Math.abs(b[i].h - pc), Math.abs(b[i].l - pc));
  }
  return s / n;
}
// sinal de entrada na vela i (fechada); a entrada e na abertura da vela seguinte
export function entryAt(b: Bar[], i: number, s: Spec, btcDaily: Bar[], cache: { ema?: number[]; rsi?: number[] } = {}): boolean {
  const c = b.map((x) => x.c), e = s.entry;
  let sig = false;
  if (e.kind === "breakout") {
    const n = e.n!;
    if (i < n) return false;
    const prev = b.slice(i - n, i);
    sig = s.side === 1 ? c[i] > Math.max(...prev.map((x) => x.h)) : c[i] < Math.min(...prev.map((x) => x.l));
  } else if (e.kind === "rsi2") {
    const r = (cache.rsi ??= rsiSeries(c, 2))[i];
    sig = !isNaN(r) && (s.side === 1 ? r < e.lo! : r > 100 - e.lo!);
  } else if (e.kind === "lowclose") {
    const n = e.n!;
    if (i < n - 1) return false;
    sig = c[i] <= Math.min(...c.slice(i - n + 1, i + 1));
  } else if (e.kind === "above_sma") {
    const n = e.n!;
    if (i < n - 1) return false;
    const m = c.slice(i - n + 1, i + 1).reduce((a, x) => a + x, 0) / n;
    sig = s.side === 1 ? c[i] > m : c[i] < m;
  }
  if (!sig) return false;
  if (s.trend_ema) {
    const t = (cache.ema ??= emaSeries(c, s.trend_ema))[i];
    if (s.side === 1 ? !(c[i] > t) : !(c[i] < t)) return false;
  }
  if (s.btc) {
    const bull = btcBullAt(btcDaily, b[i].t);
    if (bull === null) return false;
    if ((s.btc === "bull") !== bull) return false;
  }
  return true;
}
export function exitAt(b: Bar[], i: number, s: Spec, cache: { rsi?: number[] } = {}): boolean {
  if (!s.signal_exit || s.entry.kind !== "rsi2") return false;
  const r = (cache.rsi ??= rsiSeries(b.map((x) => x.c), 2))[i];
  return !isNaN(r) && (s.side === 1 ? r > s.entry.hi! : r < 100 - s.entry.hi!);
}
