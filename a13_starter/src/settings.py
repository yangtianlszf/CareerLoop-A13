from __future__ import annotations

import os


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")


def get_llm_provider() -> str:
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit in {"openai", "dashscope", "qwen"}:
        return "dashscope" if explicit == "qwen" else explicit
    if os.getenv("DASHSCOPE_API_KEY"):
        return "dashscope"
    return "openai"


def get_openai_base_url() -> str:
    if os.getenv("OPENAI_BASE_URL"):
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if os.getenv("DASHSCOPE_BASE_URL"):
        return os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1")
    if get_llm_provider() == "dashscope":
        return "https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1"
    return "https://api.openai.com/v1"


def get_openai_model() -> str:
    if os.getenv("OPENAI_MODEL"):
        return os.getenv("OPENAI_MODEL", "gpt-5-mini")
    if os.getenv("DASHSCOPE_MODEL"):
        return os.getenv("DASHSCOPE_MODEL", "qwen3.5-flash")
    if get_llm_provider() == "dashscope":
        return "qwen3.5-flash"
    return "gpt-5-mini"


def get_openai_timeout_seconds() -> int:
    raw = os.getenv("OPENAI_TIMEOUT_SECONDS", "90")
    try:
        return max(10, int(raw))
    except ValueError:
        return 90


def llm_is_configured() -> bool:
    return bool(get_openai_api_key())
