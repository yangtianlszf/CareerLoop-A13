from __future__ import annotations

from typing import Any

from a13_starter.src.constants import DEFAULT_GROWTH_PATHS
from a13_starter.src.llm_schemas import job_profile_schema, student_profile_schema
from a13_starter.src.models import JobProfile, StudentProfile
from a13_starter.src.openai_responses import OpenAIResponsesClient


STUDENT_SYSTEM_PROMPT = """你是一个用于大学生职业规划系统的资深HR数据抽取专家。
你的任务是将非结构化的学生简历、自我介绍、项目经历文本，解析成严格结构化的 JSON 数据。

【核心工作流（思维链）】
在输出最终的 JSON 字段前，你必须先在 `_thinking_process` 字段中进行一步步的思考：
1. 梳理学生的教育背景和基础信息。
2. 逐行扫描文本，提取出具体的技术栈和硬技能（避免泛泛而谈）。
3. 分析学生的项目和实习经历，提炼出其具备的软技能（如：沟通、抗压、领导力）。
4. 综合评估该简历的完整度和市场竞争力，并指出缺失的关键部分。

【输出要求】
1. 只输出符合 JSON Schema 的 JSON。
2. 没有提到的字段严格使用 null 或空数组，绝不编造（零幻觉）。
3. skills 字段需精简提炼为标准化技术词汇（如将 "熟练写Vue3代码" 提炼为 "Vue3"）。
4. profile_completeness 和 competitiveness_score 输出 0 到 100 的整数，评分需客观严苛。
5. missing_sections 必须具体指出缺失的部分（如：缺失实习经历、缺失GitHub主页、缺失明确的求职意向）。"""

JOB_SYSTEM_PROMPT = """你是一个资深猎头与岗位需求分析专家。
你的任务是将杂乱的企业招聘 JD（岗位描述）解析成严格结构化的 JSON 数据。

【核心工作流（思维链）】
在输出最终的 JSON 字段前，你必须先在 `_thinking_process` 字段中进行思考：
1. 明确该岗位的核心业务方向和职级定位。
2. 从“任职要求”中剥离出必须具备的“硬技能”（required_skills）。
3. 从“岗位职责”和隐含要求中提炼“软技能”（soft_skills）。
4. 分析该岗位在行业内的常规晋升路线。

【输出要求】
1. 只输出符合 JSON Schema 的 JSON。
2. 遇到不规范的文本（如带有大量HTML标签的JD），需在内部先清洗再提取。
3. growth_path 如果文本未明确给出，请基于岗位名称给出合理的 3 到 4 级垂直职业成长路径（如：初级开发 -> 中级开发 -> 高级开发/架构师）。"""


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
