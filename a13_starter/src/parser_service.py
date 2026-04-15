from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from a13_starter.src.extractors import build_job_profile, build_student_profile, refresh_student_profile_metrics
from a13_starter.src.llm_parser import build_job_profile_llm, build_student_profile_llm
from a13_starter.src.models import StudentProfile
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


def _merge_unique_strings(primary: list[str] | None, fallback: list[str] | None) -> list[str]:
    merged: list[str] = []
    for value in list(primary or []) + list(fallback or []):
        text = str(value or "").strip()
        if text and text not in merged:
            merged.append(text)
    return merged


def _prefer_non_empty_list(primary: list[str] | None, fallback: list[str] | None) -> list[str]:
    primary_items = [str(value or "").strip() for value in list(primary or []) if str(value or "").strip()]
    if primary_items:
        return primary_items
    return [str(value or "").strip() for value in list(fallback or []) if str(value or "").strip()]


def _merge_student_profiles(llm_profile: StudentProfile, rule_profile: StudentProfile) -> StudentProfile:
    merged = StudentProfile(
        name=(llm_profile.name or rule_profile.name),
        raw_text=llm_profile.raw_text or rule_profile.raw_text,
        school_name=llm_profile.school_name or rule_profile.school_name,
        major=llm_profile.major or rule_profile.major,
        skills=_merge_unique_strings(llm_profile.skills, rule_profile.skills),
        soft_skills=_merge_unique_strings(llm_profile.soft_skills, rule_profile.soft_skills),
        certificates=_merge_unique_strings(llm_profile.certificates, rule_profile.certificates),
        education_level=llm_profile.education_level or rule_profile.education_level,
        target_roles=_merge_unique_strings(llm_profile.target_roles, rule_profile.target_roles),
        target_industries=_merge_unique_strings(llm_profile.target_industries, rule_profile.target_industries),
        city_preference=llm_profile.city_preference or rule_profile.city_preference,
        projects=_prefer_non_empty_list(llm_profile.projects, rule_profile.projects),
        internships=_prefer_non_empty_list(llm_profile.internships, rule_profile.internships),
        awards=_prefer_non_empty_list(llm_profile.awards, rule_profile.awards),
        agent_answers=dict(llm_profile.agent_answers or rule_profile.agent_answers),
    )
    return refresh_student_profile_metrics(merged)


def parse_student_profile(raw_text: str, parser_mode: str = "auto"):
    mode = _normalize_mode(parser_mode)
    configured = llm_is_configured()

    if mode == "rule":
        return build_student_profile(raw_text), ParserMetadata(mode, "rule", configured, False, False, None)

    if mode == "llm":
        if not configured:
            profile = build_student_profile(raw_text)
            return profile, ParserMetadata(
                mode,
                "rule",
                configured,
                False,
                True,
                "LLM 模式未配置 API key，已自动回退到规则解析。",
            )
        try:
            profile = _merge_student_profiles(build_student_profile_llm(raw_text), build_student_profile(raw_text))
            return profile, ParserMetadata(mode, "llm", configured, True, False, None)
        except OpenAIResponsesError as error:
            profile = build_student_profile(raw_text)
            return profile, ParserMetadata(mode, "rule", configured, True, True, str(error))

    if configured:
        try:
            profile = _merge_student_profiles(build_student_profile_llm(raw_text), build_student_profile(raw_text))
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
        if not configured:
            profile = build_job_profile(raw_text)
            return profile, ParserMetadata(
                mode,
                "rule",
                configured,
                False,
                True,
                "LLM 模式未配置 API key，已自动回退到规则解析。",
            )
        try:
            profile = build_job_profile_llm(raw_text)
            return profile, ParserMetadata(mode, "llm", configured, True, False, None)
        except OpenAIResponsesError as error:
            profile = build_job_profile(raw_text)
            return profile, ParserMetadata(mode, "rule", configured, True, True, str(error))

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
