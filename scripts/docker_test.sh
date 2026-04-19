#!/usr/bin/env bash
# Build and run the stack with Docker Compose, then hit /health and optionally POST /process_all.
# Usage (from repo root):
#   ./scripts/docker_test.sh              # health only (default)
#   RUN_FULL_BATCH=1 ./scripts/docker_test.sh   # also run full agent batch (needs OPENROUTER_API_KEY; long)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Cannot talk to the Docker daemon. Add your user to the 'docker' group or use sudo, then retry."
  exit 1
fi

echo "==> docker compose build"
docker compose build

echo "==> docker compose up -d"
docker compose up -d

cleanup() {
  echo "==> docker compose down"
  docker compose down
}
trap cleanup EXIT

echo "==> wait for /health (host -> container)"
ok=0
for i in $(seq 1 40); do
  if curl -sf "http://127.0.0.1:8007/health" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 2
done
if [[ "$ok" != "1" ]]; then
  echo "ERROR: /health did not become ready on http://127.0.0.1:8007"
  docker compose logs --no-color --tail=80
  exit 1
fi

echo "==> GET /health"
curl -sS "http://127.0.0.1:8007/health"
echo ""

echo "==> GET /docs (status only)"
curl -sS -o /dev/null -w "OpenAPI HTTP %{http_code}\n" "http://127.0.0.1:8007/docs"

if [[ "${RUN_FULL_BATCH:-0}" == "1" ]]; then
  echo "==> POST /process_all (this can take several minutes; needs valid OPENROUTER_API_KEY in .env)"
  curl -sS -m 900 -X POST "http://127.0.0.1:8007/process_all" -o "${ROOT}/.docker_test_batch.json"
  ./venv/bin/python - <<'PY'
import json, pathlib
p = pathlib.Path(".docker_test_batch.json")
d = json.loads(p.read_text())
print("total_processed:", d["total_processed"])
print("audit_logs:", len(d["audit_logs"]))
print("dlq:", len(d["dlq"]))
failed = sum(1 for r in d["results"] if r.get("status") == "Failed")
print("results Failed:", failed)
PY
  echo "Wrote ${ROOT}/.docker_test_batch.json"
else
  echo "==> Skipping POST /process_all (set RUN_FULL_BATCH=1 to run full LLM batch)"
fi

echo "==> Streamlit UI should respond on http://127.0.0.1:8502 (HTML status)"
curl -sS -o /dev/null -w "Streamlit HTTP %{http_code}\n" "http://127.0.0.1:8502/" || true

echo "OK: Docker stack responded to health checks."
