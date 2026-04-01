from __future__ import annotations

import re

from a13_starter.src.constants import (
    CERTIFICATE_VOCAB,
    DEFAULT_GROWTH_PATHS,
    EDUCATION_LEVELS,
    SKILL_VOCAB,
    SOFT_SKILL_VOCAB,
)
from a13_starter.src.models import JobProfile, StudentProfile


def _extract_keywords(text: str, vocab: list[str]) -> list[str]:
    found = []
    lowered = text.lower()
    for item in vocab:
        item_lower = item.lower()
        if re.search(r"[a-zA-Z]", item):
            pattern = rf"(?<![a-z0-9+#./-]){re.escape(item_lower)}(?![a-z0-9+#./-])"
            if re.search(pattern, lowered):
                found.append(item)
        elif item_lower in lowered:
            found.append(item)
    return found


def _extract_labeled_value(text: str, labels: list[str]) -> str | None:
    for label in labels:
        match = re.search(rf"{label}[:：]\s*([^\n]+)", text)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return None


def _split_items(raw: str) -> list[str]:
    parts = re.split(r"[、,，/；;]", raw)
    return [part.strip() for part in parts if part.strip()]


def _extract_education(text: str) -> str | None:
    for level in EDUCATION_LEVELS:
        if level in text:
            return level
    return None


def _extract_city(text: str) -> str | None:
    return _extract_labeled_value(text, ["工作地点", "意向城市"])


def _extract_salary(text: str) -> str | None:
    match = re.search(r"(\d{1,2}k[-~]\d{1,2}k|\d{1,2}K[-~]\d{1,2}K)", text)
    if match:
        return match.group(1)
    return None


def _extract_experience(text: str) -> str | None:
    match = re.search(r"(\d+\s*年.*经验|应届生|接受实习)", text)
    if match:
        return match.group(1)
    return None


def _extract_title(text: str, default_title: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return default_title
    return lines[0]


def _extract_named_sections(text: str, prefix: str) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        stripped = re.sub(rf"^{prefix}经历[:：]\s*", "", stripped)
        stripped = re.sub(rf"^{prefix}[:：]\s*", "", stripped)
        if stripped and prefix in stripped:
            items.append(stripped)
    return items


def _extract_awards(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        stripped = re.sub(r"^(获奖经历|竞赛经历|荣誉)[:：]\s*", "", stripped)
        if any(keyword in stripped for keyword in ["获奖", "竞赛", "奖学金", "荣誉"]):
            if stripped not in {"获奖经历", "竞赛经历", "荣誉"}:
                items.append(stripped)
    return items


def _estimate_profile_completeness(
    school_name: str | None,
    major: str | None,
    education_level: str | None,
    target_roles: list[str],
    city_preference: str | None,
    skills: list[str],
    certificates: list[str],
    projects: list[str],
    internships: list[str],
) -> tuple[int, list[str]]:
    score = 0
    missing = []
    checks = [
        ("学校信息", school_name, 10),
        ("专业信息", major, 10),
        ("学历信息", education_level, 10),
        ("目标岗位", bool(target_roles), 15),
        ("意向城市", city_preference, 10),
        ("技能清单", bool(skills), 15),
        ("证书信息", bool(certificates), 10),
        ("项目经历", bool(projects), 10),
        ("实习经历", bool(internships), 10),
    ]
    for label, value, points in checks:
        if value:
            score += points
        else:
            missing.append(label)
    return score, missing


def _estimate_competitiveness(
    skills: list[str],
    certificates: list[str],
    projects: list[str],
    internships: list[str],
    awards: list[str],
) -> int:
    score = 30
    score += min(len(skills) * 4, 24)
    score += min(len(certificates) * 8, 16)
    score += min(len(projects) * 10, 20)
    score += min(len(internships) * 12, 24)
    score += min(len(awards) * 6, 12)
    return max(0, min(score, 100))


def refresh_student_profile_metrics(student: StudentProfile) -> StudentProfile:
    completeness_score, missing_sections = _estimate_profile_completeness(
        school_name=student.school_name,
        major=student.major,
        education_level=student.education_level,
        target_roles=student.target_roles,
        city_preference=student.city_preference,
        skills=student.skills,
        certificates=student.certificates,
        projects=student.projects,
        internships=student.internships,
    )
    competitiveness_score = _estimate_competitiveness(
        skills=student.skills,
        certificates=student.certificates,
        projects=student.projects,
        internships=student.internships,
        awards=student.awards,
    )
    student.profile_completeness = completeness_score
    student.competitiveness_score = competitiveness_score
    student.missing_sections = missing_sections
    return student


def build_job_profile(raw_text: str) -> JobProfile:
    title = _extract_title(raw_text, "未命名岗位")
    growth_path = DEFAULT_GROWTH_PATHS.get(title, [title, "相关岗位提升", "岗位负责人"])
    return JobProfile(
        title=title,
        raw_text=raw_text,
        required_skills=_extract_keywords(raw_text, SKILL_VOCAB),
        soft_skills=_extract_keywords(raw_text, SOFT_SKILL_VOCAB),
        certificates=_extract_keywords(raw_text, CERTIFICATE_VOCAB),
        education_requirement=_extract_education(raw_text),
        experience_requirement=_extract_experience(raw_text),
        city=_extract_city(raw_text),
        salary_range=_extract_salary(raw_text),
        growth_path=growth_path,
    )


def build_student_profile(raw_text: str) -> StudentProfile:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    name = _extract_labeled_value(raw_text, ["姓名"]) or (lines[0].replace("姓名：", "") if lines else "未命名学生")
    target_roles = []
    target_industries = []
    city_preference = _extract_city(raw_text)
    school_name = _extract_labeled_value(raw_text, ["学校", "院校"])
    major = _extract_labeled_value(raw_text, ["专业"])

    role_match = re.search(r"目标岗位[:：]\s*([^\n]+)", raw_text)
    if role_match:
        target_roles = _split_items(role_match.group(1))

    industry_match = re.search(r"目标行业[:：]\s*([^\n]+)", raw_text)
    if industry_match:
        target_industries = _split_items(industry_match.group(1))

    skills = _extract_keywords(raw_text, SKILL_VOCAB)
    soft_skills = _extract_keywords(raw_text, SOFT_SKILL_VOCAB)
    certificates = _extract_keywords(raw_text, CERTIFICATE_VOCAB)
    education_level = _extract_education(raw_text)
    projects = _extract_named_sections(raw_text, "项目")
    internships = _extract_named_sections(raw_text, "实习")
    awards = _extract_awards(raw_text)
    return refresh_student_profile_metrics(
        StudentProfile(
        name=name,
        raw_text=raw_text,
        school_name=school_name,
        major=major,
        skills=skills,
        soft_skills=soft_skills,
        certificates=certificates,
        education_level=education_level,
        target_roles=target_roles,
        target_industries=target_industries,
        city_preference=city_preference,
        projects=projects,
        internships=internships,
        awards=awards,
        )
    )
