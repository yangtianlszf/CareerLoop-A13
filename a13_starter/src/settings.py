from __future__ import annotations

import os
from pathlib import Path

from a13_starter.src.paths import resolve_project_root


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        clean_key = key.strip()
        if not clean_key:
            continue
        clean_value = value.strip()
        if len(clean_value) >= 2 and clean_value[0] == clean_value[-1] and clean_value[0] in {"'", '"'}:
            clean_value = clean_value[1:-1]
        parsed[clean_key] = clean_value
    return parsed


def _load_project_env_files() -> None:
    project_root = resolve_project_root(__file__, 2)
    merged: dict[str, str] = {}
    for candidate in (project_root / ".env", project_root / ".env.local"):
        merged.update(_read_env_file(candidate))

    for key, value in merged.items():
        os.environ.setdefault(key, value)


_load_project_env_files()


def get_openai_api_key() -> str | None:
    return os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")


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
        # 🌟 核心修改点：去掉了 /api/v2/apps/protocols/，替换为标准的模型调用接口
        return os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    if get_llm_provider() == "dashscope":
        # 🌟 核心修改点：去掉了 /api/v2/apps/protocols/，替换为标准的模型调用接口
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"
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
