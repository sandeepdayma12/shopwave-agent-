from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolExecutor

from config.settings import settings
from tools.definitions import agent_tools

llm = ChatOpenAI(
    model=settings.llm_model,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base=settings.openrouter_base_url,
    max_tokens=settings.llm_max_tokens,
    temperature=settings.llm_temperature,
    request_timeout=settings.llm_request_timeout,
)

llm_with_tools = llm.bind_tools(agent_tools)
tool_executor = ToolExecutor(agent_tools)
