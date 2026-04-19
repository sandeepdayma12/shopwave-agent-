#!/usr/bin/env python3
"""POST /process_all and write audit_log.json (run with API backend up)."""
import argparse
import json
import os
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "audit_log.json"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--url",
        default=os.getenv("FASTAPI_URL", "http://127.0.0.1:8007"),
        help="Base URL of FastAPI (no trailing slash)",
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--timeout", type=float, default=600.0)
    args = p.parse_args()

    url = args.url.rstrip("/") + "/process_all"
    r = httpx.post(url, timeout=args.timeout)
    r.raise_for_status()
    data = r.json()
    args.out.write_text(json.dumps(data["audit_logs"], indent=2), encoding="utf-8")
    print(f"Wrote {args.out} ({len(data['audit_logs'])} entries)")
    print(f"Tickets processed: {data['total_processed']}, DLQ: {len(data['dlq'])}")


if __name__ == "__main__":
    main()
