from tools.state import dlq

from .state import AgentState


def _tool_message_count(messages) -> int:
    return sum(1 for m in messages if getattr(m, "type", None) == "tool")


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last = messages[-1]

    if len(messages) > 40:
        dlq.append(
            {
                "ticket_id": state.get("ticket_id"),
                "reason": "Max graph depth reached (safety limit)",
            }
        )
        return "end"

    if getattr(last, "tool_calls", None):
        if len(messages) > 30:
            dlq.append(
                {
                    "ticket_id": state.get("ticket_id"),
                    "reason": "Max iteration depth reached",
                }
            )
            return "end"
        return "continue"

    if _tool_message_count(messages) < 3:
        return "nudge"

    return "end"
