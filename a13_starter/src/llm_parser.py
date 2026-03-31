from __future__ import annotations

from typing import Any

from a13_starter.src.constants import DEFAULT_GROWTH_PATHS
from a13_starter.src.llm_schemas import job_profile_schema, student_profile_schema
from a13_starter.src.models import JobProfile, StudentProfile
from a13_starter.src.openai_responses import OpenAIResponsesClient


STUDENT_SYSTEM_PROMPT = """你是一个用于大学生职业规划系统的数据抽取器。
你的任务是把简历、自我介绍、项目经历文本解析成严格结构化的学生画像 JSON。

要求：
1. 只输出符合 JSON Schema 的 JSON。
2. 没有提到的字段用 null 或空数组，不要编造。
3. skills 要尽量提取真实技术技能，soft_skills 提取职业素养和通用能力。
4. profile_completeness 和 competitiveness_score 都输出 0 到 100 的整数。
5. missing_sections 输出当前简历仍缺失的重要部分，例如 学校信息、专业信息、项目经历、实习经历、目标岗位 等。"""

JOB_SYSTEM_PROMPT = """你是一个招聘 JD 结构化抽取器。
你的任务是把岗位描述解析成严格结构化的岗位画像 JSON。

要求：
1. 只输出符合 JSON Schema 的 JSON。
2. 没有提到的字段用 null 或空数组，不要编造。
3. required_skills 要提取岗位核心技术要求，soft_skills 提取职业素养。
4. growth_path 如果文本未明确给出，可以基于岗位名称给出合理的 3 到 4 级职业成长路径。"""


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    seen: list[str] = []
    for value in values:
        text = _clean_string(value)
        if text and text not in seen:
            seen.append(text)
    return seen


def build_student_profile_llm(raw_text: str, client: OpenAIResponsesClient | None = None) -> StudentProfile:
    client = client or OpenAIResponsesClient()
    payload = client.create_structured_output(
        system_prompt=STUDENT_SYSTEM_PROMPT,
        user_prompt=raw_text,
        schema_name="student_profile",
        schema=student_profile_schema(),
        reasoning_effort="medium",
    )
    return StudentProfile(
        name=_clean_string(payload.get("name")) or "未命名学生",
        raw_text=raw_text,
        school_name=_clean_string(payload.get("school_name")),
        major=_clean_string(payload.get("major")),
        skills=_clean_string_list(payload.get("skills")),
        soft_skills=_clean_string_list(payload.get("soft_skills")),
        certificates=_clean_string_list(payload.get("certificates")),
        education_level=_clean_string(payload.get("education_level")),
        target_roles=_clean_string_list(payload.get("target_roles")),
        target_industries=_clean_string_list(payload.get("target_industries")),
        city_preference=_clean_string(payload.get("city_preference")),
        projects=_clean_string_list(payload.get("projects")),
        internships=_clean_string_list(payload.get("internships")),
        awards=_clean_string_list(payload.get("awards")),
        profile_completeness=int(payload.get("profile_completeness", 0) or 0),
        competitiveness_score=int(payload.get("competitiveness_score", 0) or 0),
        missing_sections=_clean_string_list(payload.get("missing_sections")),
    )


def build_job_profile_llm(raw_text: str, client: OpenAIResponsesClient | None = None) -> JobProfile:
    client = client or OpenAIResponsesClient()
    payload = client.create_structured_output(
        system_prompt=JOB_SYSTEM_PROMPT,
        user_prompt=raw_text,
        schema_name="job_profile",
        schema=job_profile_schema(),
        reasoning_effort="medium",
    )
    title = _clean_string(payload.get("title")) or "未命名岗位"
    growth_path = _clean_string_list(payload.get("growth_path"))
    if not growth_path:
        growth_path = DEFAULT_GROWTH_PATHS.get(title, [title, "相关岗位提升", "岗位负责人"])
    return JobProfile(
        title=title,
        raw_text=raw_text,
        required_skills=_clean_string_list(payload.get("required_skills")),
        soft_skills=_clean_string_list(payload.get("soft_skills")),
        certificates=_clean_string_list(payload.get("certificates")),
        education_requirement=_clean_string(payload.get("education_requirement")),
        experience_requirement=_clean_string(payload.get("experience_requirement")),
        city=_clean_string(payload.get("city")),
        salary_range=_clean_string(payload.get("salary_range")),
        growth_path=growth_path,
    )
