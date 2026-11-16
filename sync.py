"""
Sincroniza o estado do repo com o dashboard (Supabase).
  python sync.py                         # envia TODO, SUMMARY, NOTES, HOLDOUT_LOG e todos os results/runs/*.json
  python sync.py --log inicio "texto"    # regista um evento na atividade do agente (inicio|teste|fim|erro)
Precisa de BT_WRITE_TOKEN no ambiente; sem ele nao faz nada.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from sr import supa


def read(p: str) -> str:
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def parse_todo(text: str) -> list:
    out, sec = [], ""
    for line in text.splitlines():
        if line.startswith("## "):
            sec = line[3:].strip()
        m = re.match(r"^- \[( |x|X)\] (.*)$", line)
        if m:
            out.append({"done": m.group(1).lower() == "x", "text": m.group(2).replace("`", ""), "section": sec})
    return out


def main():
    if not os.environ.get("BT_WRITE_TOKEN"):
        print("BT_WRITE_TOKEN nao definido: nada enviado.")
        return
    if len(sys.argv) >= 4 and sys.argv[1] == "--log":
        print("log:", supa.log_event(sys.argv[2], " ".join(sys.argv[3:])))
        return
    ok = [supa.set_state("todo", parse_todo(read("TODO.md"))),
          supa.set_state("summary", read("SUMMARY.md")),
          supa.set_state("notes", read("NOTES.md")),
          supa.set_state("holdout_log", read("HOLDOUT_LOG.md")),
          supa.set_state("ideas", read("IDEAS.md"))]
    for f in sorted(glob.glob(os.path.join("results", "runs", "*.json"))):
        ok.append(supa.report_run(json.load(open(f))))
    print(f"sync: {sum(ok)}/{len(ok)} enviados")


if __name__ == "__main__":
    main()
