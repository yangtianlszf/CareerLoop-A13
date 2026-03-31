from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from a13_starter.src.extractors import build_job_profile, build_student_profile
from a13_starter.src.llm_parser import build_job_profile_llm, build_student_profile_llm
from a13_starter.src.openai_responses import OpenAIResponsesError
from a13_starter.src.settings import llm_is_configured


@dataclass
class ParserMetadata:
    requested_mode: str
    used_mode: str
    llm_configured: bool
    llm_attempted: bool
    fallback_used: bool
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_mode(parser_mode: str) -> str:
    mode = (parser_mode or "auto").strip().lower()
    if mode not in {"auto", "rule", "llm"}:
        return "auto"
    return mode


def parse_student_profile(raw_text: str, parser_mode: str = "auto"):
    mode = _normalize_mode(parser_mode)
    configured = llm_is_configured()

    if mode == "rule":
        return build_student_profile(raw_text), ParserMetadata(mode, "rule", configured, False, False, None)

    if mode == "llm":
        profile = build_student_profile_llm(raw_text)
        return profile, ParserMetadata(mode, "llm", configured, True, False, None)

    if configured:
        try:
            profile = build_student_profile_llm(raw_text)
            return profile, ParserMetadata(mode, "llm", configured, True, False, None)
        except OpenAIResponsesError as error:
            profile = build_student_profile(raw_text)
            return profile, ParserMetadata(mode, "rule", configured, True, True, str(error))

    profile = build_student_profile(raw_text)
    return profile, ParserMetadata(
        mode,
        "rule",
        configured,
        False,
        False,
        "LLM API key not configured. Set OPENAI_API_KEY or DASHSCOPE_API_KEY.",
    )


def parse_job_profile(raw_text: str, parser_mode: str = "auto"):
    mode = _normalize_mode(parser_mode)
    configured = llm_is_configured()

    if mode == "rule":
        return build_job_profile(raw_text), ParserMetadata(mode, "rule", configured, False, False, None)

    if mode == "llm":
        profile = build_job_profile_llm(raw_text)
        return profile, ParserMetadata(mode, "llm", configured, True, False, None)

    if configured:
        try:
            profile = build_job_profile_llm(raw_text)
            return profile, ParserMetadata(mode, "llm", configured, True, False, None)
        except OpenAIResponsesError as error:
            profile = build_job_profile(raw_text)
            return profile, ParserMetadata(mode, "rule", configured, True, True, str(error))

    profile = build_job_profile(raw_text)
    return profile, ParserMetadata(
        mode,
        "rule",
        configured,
        False,
        False,
        "LLM API key not configured. Set OPENAI_API_KEY or DASHSCOPE_API_KEY.",
    )
