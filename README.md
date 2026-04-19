# ShopWave — Autonomous Support Resolution Agent

Hackathon 2026 submission: an agentic support pipeline that ingests mock tickets, classifies intent internally, resolves with **LangGraph** + tool calls (with realistic mock failures), processes tickets **concurrently**, and emits an **audit trail** plus optional **dead-letter queue** entries.

## Tech stack

- **Python 3.10+**
- **FastAPI** + **Uvicorn** — batch API `POST /process_all`
- **LangGraph** + **LangChain** — ReAct-style loop (`agent` → `action` → `agent`, with `nudge_tools` when fewer than three tool results exist)
- **OpenRouter** (OpenAI-compatible) — default model `meta-llama/llama-3.1-70b-instruct` (`OPENROUTER_MODEL` to override)
- **Streamlit** — one-click UI to trigger processing and inspect traces
- **Docker** — single image runs API + UI (see below)

## Prerequisites

- `OPENROUTER_API_KEY` in the environment or in a local `.env` file (see `.env.example`). **Do not commit real keys.**
- Python 3.10+ if running locally without Docker.

## Run with one command (Docker)

From the repository root:

```bash
docker compose up --build
```

Then open:

- **Streamlit:** http://localhost:8502 — click the button to process all tickets and download/save `audit_log.json` locally.
- **API docs:** http://localhost:8007/docs

Inside the container the UI calls `http://localhost:8007` (both processes share the same network namespace).

## Run locally (development)

Terminal 1 — API:

```bash
cd /path/to/shopwave_agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then add OPENROUTER_API_KEY
uvicorn main:app --host 0.0.0.0 --port 8007
```

Terminal 2 — UI (set `FASTAPI_URL` if the API is not on localhost:8007):

```bash
export FASTAPI_URL=http://127.0.0.1:8007
streamlit run app.py --server.port 8502
```

## Generate deliverable files

| Deliverable | How |
|-------------|-----|
| `architecture.png` | `python scripts/generate_architecture.py` (requires `matplotlib`; included in `requirements.txt`) |
| `audit_log.json` | **Recommended:** `python scripts/write_audit_via_app.py` — runs `POST /process_all` in-process (needs `OPENROUTER_API_KEY`, can take several minutes). Alternatively, with the API already up: `python scripts/export_audit.py`. The Streamlit button also writes `audit_log.json` to the process working directory. **Commit the JSON from a full run** so it reflects all 20 tickets. |
| `failure_modes.md` | Maintained in-repo (see file). |

Optional: set `MAX_CONCURRENT_TICKETS` (default `6`) to tune parallelism vs OpenRouter rate limits; `PROCESS_ALL_HTTP_TIMEOUT` for the Streamlit client (default `900` seconds); **`LANGGRAPH_RECURSION_LIMIT`** (default `120`) if graphs hit LangGraph’s step cap during long tool + nudge loops.

## Project layout

- `main.py` — FastAPI app, concurrent ticket workers
- `app.py` — Streamlit dashboard
- `config/` — settings and env loading
- `agents/` — graph nodes, router, prompts, LLM wiring
- `tools/` — mock tools, audit log list, eligibility gate for refunds
- `db/` — mock JSON + markdown knowledge base
- `data/` — `tickets.json` (20 tickets), customers, orders, products, `knowledge-base.md`
- `scripts/` — architecture image + audit export helpers

## Official sample data

If you want to diff against the hackathon’s canonical JSON, compare with:  
https://github.com/ksolves/agentic_ai_hackthon_2026_sample_data/

## Security

- `.env` is listed in `.gitignore`. Use `.env.example` as a template only.
- If an API key was ever committed, **rotate it** in the provider dashboard before publishing the repo.
# shopwave-agent-
