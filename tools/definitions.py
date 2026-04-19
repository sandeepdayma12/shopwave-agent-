import random
from typing import Any

from langchain.tools import tool

from db.mock_db import db

# Last successful eligibility snapshot per order (consumed on refund).
_eligibility_by_order: dict[str, dict[str, Any]] = {}


def clear_eligibility_cache() -> None:
    _eligibility_by_order.clear()


def simulate_failure() -> None:
    """Simulates realistic API failures to test agent recovery (Retry Budgets)."""
    chance = random.random()
    if chance < 0.10:
        raise TimeoutError("Tool execution timed out. Please retry.")
    elif chance < 0.15:
        raise ValueError('{"error": "Malformed JSON response from upstream API"}')


@tool
def get_order(order_id: str) -> dict:
    """Fetches order details, status, and timestamps."""
    simulate_failure()
    for order in db.orders:
        if order["order_id"] == order_id:
            return order
    return {"error": "Order not found"}


@tool
def get_customer(email: str) -> dict:
    """Fetches customer profile, tier, and history."""
    simulate_failure()
    for cust in db.customers:
        if cust["email"].lower() == email.lower():
            return cust
    return {"error": "Customer not found"}


@tool
def get_product(product_id: str) -> dict:
    """Fetches product metadata, category, and warranty."""
    simulate_failure()
    for prod in db.products:
        if prod["product_id"] == product_id:
            return prod
    return {"error": "Product not found"}


@tool
def search_knowledge_base(query: str) -> str:
    """Semantic search against the policy and FAQ knowledge base."""
    return db.kb


@tool
def check_refund_eligibility(order_id: str) -> dict:
    """Returns refund eligibility + reason. May throw errors."""
    simulate_failure()
    order = next((o for o in db.orders if o["order_id"] == order_id), None)
    if not order:
        r = {"eligible": False, "reason": "Order not found."}
        _eligibility_by_order[order_id] = r
        return r
    if order["refund_status"] == "refunded":
        r = {"eligible": False, "reason": "Already refunded."}
        _eligibility_by_order[order_id] = r
        return r
    if not order["return_deadline"]:
        r = {"eligible": False, "reason": "Not delivered yet."}
        _eligibility_by_order[order_id] = r
        return r

    today = "2024-03-15"
    if today > order["return_deadline"]:
        result = {
            "eligible": False,
            "reason": f"Return window expired on {order['return_deadline']}.",
        }
        _eligibility_by_order[order_id] = result
        return result
    result = {"eligible": True, "reason": "Within return window."}
    _eligibility_by_order[order_id] = result
    return result


@tool
def issue_refund(order_id: str, amount: float, ticket_id: str) -> dict:
    """IRREVERSIBLE - Issues a refund to the customer. Must check eligibility first."""
    prior = _eligibility_by_order.pop(order_id, None)
    if not prior or not prior.get("eligible"):
        return {
            "status": "blocked",
            "message": "Call check_refund_eligibility for this order_id first; last result must be eligible=True.",
        }
    return {
        "status": "success",
        "message": f"Successfully refunded ${amount} for order {order_id}",
    }


@tool
def send_reply(ticket_id: str, message: str) -> dict:
    """Sends the final response to the customer resolving the ticket."""
    return {"status": "success", "message": "Reply sent successfully."}


@tool
def escalate(ticket_id: str, summary: str, priority: str) -> dict:
    """Routes the ticket to a human agent with a structured summary."""
    return {"status": "success", "message": "Ticket escalated to human support."}


agent_tools = [
    get_order,
    get_customer,
    get_product,
    search_knowledge_base,
    check_refund_eligibility,
    issue_refund,
    send_reply,
    escalate,
]
