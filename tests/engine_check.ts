// node --experimental-strip-types tests/engine_check.ts cases.json -> sai com erro se engine.ts != sr/demo_spec.py
import { readFileSync } from "node:fs";
import { entryAt, exitAt, type Bar } from "../supabase/functions/paper-bot/engine.ts";
const cases = JSON.parse(readFileSync(process.argv[2], "utf8"));
let bad = 0;
for (const k of cases) {
  const bars: Bar[] = k.bars.map((x: number[]) => ({ t: x[0], o: x[1], h: x[2], l: x[3], c: x[4] }));
  const btc: Bar[] = k.btc.map((x: number[]) => ({ t: x[0], o: x[1], h: x[2], l: x[3], c: x[4] }));
  const cache = {}, n = bars.length, m = k.py_entry.length;
  for (let j = 0; j < m; j++) {
    const i = n - m + j;
    const e = entryAt(bars, i, k.spec, btc, cache), x = exitAt(bars, i, k.spec, cache);
    if (e !== k.py_entry[j] || x !== k.py_exit[j]) { bad++; if (bad < 10) console.log(k.name, new Date(bars[i].t).toISOString(), "ts", e, x, "py", k.py_entry[j], k.py_exit[j]); }
  }
}
if (bad) { console.log("diferencas:", bad); process.exit(1); }
console.log("engine.ts == demo_spec.py");
