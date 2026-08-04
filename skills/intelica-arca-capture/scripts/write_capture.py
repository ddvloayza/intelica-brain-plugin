#!/usr/bin/env python3
"""Guarda un fragmento de captura en el staging local de la sesion.

Se llama justo antes de que Claude Code compacte el contexto. Lo que decide
que guardar es el skill (eso necesita criterio); este script hace solo la
parte determinista: en que carpeta va, con que numero de secuencia, y con que
timestamp. Son exactamente las cosas que un LLM genera mal razonando.

Los fragmentos son staging, no conocimiento: viven local, nunca van a GitHub,
y sobreviven al PR para poder re-curar si hace falta.

Uso:
    python3 write_capture.py --session <session_id> <<'EOF'
    {
      "summary": "...",
      "facts": ["...", "..."],
      "entities": [{"type": "Resource", "id": "i-0abc", "resource_type": "ec2_instance"}],
      "relations": [{"from": "i-0abc", "type": "BELONGS_TO", "to": "Portal-Prod"}],
      "open_questions": ["..."]
    }
    EOF

Imprime en stdout el path escrito y cuantos fragmentos acumula la sesion.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STAGING_ROOT = Path(
    os.environ.get("INTELICA_ARCA_STAGING", "~/.intelica-arca/sessions")
).expanduser()

# El session_id viene del hook; se sanea antes de usarlo como nombre de
# carpeta para que no pueda escapar del directorio de staging.
SAFE_SESSION = re.compile(r"[^A-Za-z0-9._-]")


def session_dir(session_id: str) -> Path:
    safe = SAFE_SESSION.sub("_", session_id.strip()) or "unknown-session"
    return STAGING_ROOT / safe


def next_sequence(directory: Path) -> int:
    existing = sorted(directory.glob("[0-9][0-9][0-9].json"))
    if not existing:
        return 1
    return int(existing[-1].stem) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, help="session_id que paso el hook")
    args = parser.parse_args()

    try:
        fragment = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"El fragmento no es JSON valido: {exc}", file=sys.stderr)
        return 1

    if not isinstance(fragment, dict):
        print("Se esperaba un objeto JSON en stdin.", file=sys.stderr)
        return 1

    directory = session_dir(args.session)
    directory.mkdir(parents=True, exist_ok=True)

    seq = next_sequence(directory)
    fragment["captured_at"] = datetime.now(timezone.utc).isoformat()
    fragment["sequence"] = seq
    fragment["session_id"] = args.session

    path = directory / f"{seq:03d}.json"
    path.write_text(json.dumps(fragment, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(list(directory.glob("[0-9][0-9][0-9].json")))
    entities = len(fragment.get("entities") or [])
    facts = len(fragment.get("facts") or [])
    print(f"Guardado {path} — {facts} hechos, {entities} entidades. "
          f"La sesion acumula {total} fragmento(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
