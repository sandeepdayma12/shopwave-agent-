import asyncio
import os

from fastapi import FastAPI
from pydantic import BaseModel

from agents import app_graph, create_initial_message
from config.settings import settings
from db.mock_db import db
from tools import audit_logs, dlq
from tools.audit import log_audit
from tools.definitions import clear_eligibility_cache

app = FastAPI(title="ShopWave Autonomous Support API")


@app.get("/health")
async def health():
    return {"status": "ok", "tickets_loaded": len(db.tickets)}


# Bound in-flight LLM graphs to reduce provider rate limits while staying concurrent.
_MAX_IN_FLIGHT = max(1, int(os.getenv("MAX_CONCURRENT_TICKETS", "6")))
_ticket_sem = asyncio.Semaphore(_MAX_IN_FLIGHT)


class ProcessResponse(BaseModel):
    message: str
    total_processed: int
    audit_logs: list
    dlq: list
    results: list


async def process_ticket_async(ticket):
    initial_message = create_initial_message(ticket)
    inputs = {"messages": [initial_message], "ticket_id": ticket["ticket_id"], "confidence": 1.0}
    try:
        async with _ticket_sem:
            result = await app_graph.ainvoke(
                inputs,
                config={"recursion_limit": settings.langgraph_recursion_limit},
            )
        trace = []
        for msg in result["messages"]:
            if msg.type == "ai" and msg.tool_calls:
                trace.append({"type": "tool_call", "calls": msg.tool_calls})
            elif msg.type == "ai" and msg.content:
                trace.append({"type": "thought", "content": msg.content})
            elif msg.type == "tool":
                trace.append({"type": "tool_result", "name": msg.name, "result": msg.content})

        return {
            "ticket_id": ticket["ticket_id"],
            "status": "Success",
            "confidence": result["confidence"],
            "trace": trace,
        }
    except Exception as e:
        dlq.append({"ticket_id": ticket["ticket_id"], "reason": str(e)})
        log_audit(ticket["ticket_id"], "graph_exception", str(e)[:2000])
        return {"ticket_id": ticket["ticket_id"], "status": "Failed", "error": str(e)}


@app.post("/process_all", response_model=ProcessResponse)
async def process_all_tickets():
    clear_eligibility_cache()
    audit_logs.clear()
    dlq.clear()

    tasks = [process_ticket_async(t) for t in db.tickets]
    results = await asyncio.gather(*tasks)

    return ProcessResponse(
        message="Batch processing complete",
        total_processed=len(results),
        audit_logs=audit_logs,
        dlq=dlq,
        results=results,
    )
