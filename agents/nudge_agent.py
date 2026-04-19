from langchain_core.messages import HumanMessage

from .state import AgentState


def nudge_min_tools(state: AgentState):
    tid = state.get("ticket_id", "unknown")
    reminder = (
        "Constraint: complete at least three distinct tool invocations before finishing "
        "(e.g. get_customer with the ticket email, get_order with the order id from the ticket, "
        "search_knowledge_base with a short policy question). "
        "Then decide: check_refund_eligibility, issue_refund, send_reply, escalate, or get_product as needed. "
        f"Ticket: {tid}."
    )
    return {"messages": [HumanMessage(content=reminder)]}
