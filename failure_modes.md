# Failure mode analysis (ShopWave agent)

At least three failure scenarios the system is designed to handle, aligned with the hackathon “recover / explain” constraints.

## 1. Intermittent tool timeouts and malformed upstream responses

**What goes wrong:** Mock read tools (`get_order`, `get_customer`, `get_product`, `check_refund_eligibility`) randomly raise `TimeoutError` or `ValueError` with malformed JSON-style payloads to simulate flaky dependencies.

**How the system responds:** The LangGraph **tool node** wraps each invocation in `try/except`. Failures become a `ToolMessage` with an explicit error string so the LLM can **retry with a different plan** or escalate. The ticket graph does not crash solely because a tool raised.

**Explainability:** The API/UI trace includes `tool_result` steps showing the error text returned to the model.

## 2. Model stops before the minimum tool chain

**What goes wrong:** The LLM might attempt to answer or close the ticket without enough grounded lookups, violating the “≥3 tool calls in a chain” constraint.

**How the system responds:** The **router** counts completed tool messages. If the latest assistant message has **no** `tool_calls` and the tool count is fewer than **3**, control flows to **`nudge_tools`**, which injects a `HumanMessage` reminder listing the required sequence (`get_customer` → `get_order` → `search_knowledge_base`). The graph returns to the LLM until the minimum is met or a safety depth cap triggers the DLQ.

**Explainability:** Trace shows alternating thoughts, tool calls, and the nudge step as plain messages in the chain.

## 3. Refund without eligibility, or runaway tool loop

**What goes wrong:** (a) `issue_refund` could be called without a successful eligibility check — an irreversible action risk. (b) The agent could loop on tools indefinitely.

**How the system responds:** (a) **`check_refund_eligibility`** records the latest eligibility snapshot per `order_id`; **`issue_refund`** consumes that snapshot and **blocks** the refund unless the last recorded result was `eligible: true`, forcing the model to run the check first. (b) Message depth limits append a **dead-letter queue** entry (`Max iteration depth` / `Max graph depth`) and end the graph for that ticket.

**Explainability:** Blocked refunds return a structured `blocked` payload in the tool trace; DLQ entries are returned in the `/process_all` JSON payload.

## 4. Whole-graph exceptions (provider/network)

**What goes wrong:** (a) Network failures or provider errors can raise outside individual tools (e.g. during `ainvoke`). (b) LangGraph hits its **recursion step limit** when the loop (`agent` → `action` → `agent`, plus **`nudge_tools`**) runs longer than the configured budget (mock tool failures and minimum-tool nudges add steps).

**How the system responds:** `process_ticket_async` catches exceptions, records `{ticket_id, reason}` in **`dlq`**, and marks the ticket `Failed`. For (b), raise **`LANGGRAPH_RECURSION_LIMIT`** in the environment (default in code is higher than LangGraph’s stock 25) so honest long chains can finish.

**Explainability:** API returns per-ticket status plus `dlq` list for judges and operators.

## 5. Upstream LLM errors (OpenRouter)

**What goes wrong:** OpenRouter returns HTTP errors such as **`402` insufficient credits**, **`429`** rate limits, **`401`** invalid key, or an unknown / unavailable `OPENROUTER_MODEL`.

**How the system responds:** The exception is caught in `process_ticket_async`, the ticket is marked `Failed`, the reason is appended to **`dlq`**, and a **`graph_exception`** row is written to **`audit_logs`** so the failure is visible in `audit_log.json`.

**Explainability:** DLQ `reason` strings surface the provider message when present; fix `OPENROUTER_API_KEY`, model id, or account credits and re-run; optionally lower `MAX_CONCURRENT_TICKETS` if rate limits are hit.
