from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolInvocation

from tools.audit import log_audit

from .llm import tool_executor
from .state import AgentState


def call_tools(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    ticket_id = state.get("ticket_id", "unknown")

    tool_responses = []
    for tool_call in last_message.tool_calls:
        action = ToolInvocation(tool=tool_call["name"], tool_input=tool_call["args"])
        try:
            response = tool_executor.invoke(action)
        except Exception as e:
            response = f"TOOL ERROR: {str(e)}. Please retry or evaluate a different path."

        log_audit(
            ticket_id,
            f"invoke_{action.tool}",
            f"args={tool_call['args']!r} | result={str(response)[:1500]}",
        )

        tool_message = ToolMessage(
            content=str(response), name=action.tool, tool_call_id=tool_call["id"]
        )
        tool_responses.append(tool_message)

    return {"messages": tool_responses}
