from .llm import llm_with_tools
from .state import AgentState


def call_model(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    confidence = 0.9 if response.tool_calls else 0.5
    if "I am not sure" in response.content or "conflicting" in response.content:
        confidence = 0.4

    return {"messages": [response], "confidence": confidence}
