from langgraph.graph import END, StateGraph

from .model_agent import call_model
from .nudge_agent import nudge_min_tools
from .router import should_continue
from .state import AgentState
from .tools_agent import call_tools

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tools)
workflow.add_node("nudge_tools", nudge_min_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "action", "end": END, "nudge": "nudge_tools"},
)
workflow.add_edge("action", "agent")
workflow.add_edge("nudge_tools", "agent")
app_graph = workflow.compile()
