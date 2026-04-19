import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings:
    # --- OpenRouter (OpenAI-compatible API) ---
    openrouter_api_key: str = os.environ.get("OPENROUTER_API_KEY", "dummy")
    openrouter_base_url: str = os.environ.get(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    llm_model: str = os.environ.get(
        "OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct"
    )
    llm_max_tokens: int = int(os.environ.get("LLM_MAX_TOKENS", "1500"))
    llm_temperature: float = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
    llm_request_timeout: float = float(os.environ.get("LLM_REQUEST_TIMEOUT", "120"))

    # LangGraph stops after this many super-steps (each node transition counts).
    # Tool retries + nudge_min_tools loops can exceed the library default of 25.
    langgraph_recursion_limit: int = int(os.environ.get("LANGGRAPH_RECURSION_LIMIT", "120"))

    fastapi_url: str = os.getenv("FASTAPI_URL", "http://localhost:8007")
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8007"))
    frontend_host: str = os.getenv("FRONTEND_HOST", "0.0.0.0")
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "8502"))


settings = Settings()
