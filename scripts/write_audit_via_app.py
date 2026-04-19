#!/usr/bin/env python3
"""Run POST /process_all in-process and write audit_log.json (needs valid OPENROUTER_API_KEY)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from main import app


def main() -> None:
    out = ROOT / "audit_log.json"
    with TestClient(app) as client:
        r = client.post("/process_all", timeout=900.0)
        r.raise_for_status()
        data = r.json()
    out.write_text(json.dumps(data["audit_logs"], indent=2), encoding="utf-8")
    print(f"Wrote {out} — audit entries: {len(data['audit_logs'])}, tickets: {data['total_processed']}, dlq: {len(data['dlq'])}")


if __name__ == "__main__":
    main()
