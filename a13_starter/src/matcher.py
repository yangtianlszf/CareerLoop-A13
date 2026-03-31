from __future__ import annotations

from a13_starter.src.constants import SKILL_ALIASES, SOFT_SKILL_ALIASES
from a13_starter.src.models import JobProfile, MatchBreakdown, MatchResult, StudentProfile


def _normalize_by_aliases(values: list[str], aliases: dict[str, list[str]]) -> tuple[set[str], dict[str, str]]:
    normalized: set[str] = set()
    evidence: dict[str, str] = {}
    for raw_value in values:
        lowered = raw_value.strip().lower()
        if not lowered:
            continue
        matched = False
        for canonical, candidates in aliases.items():
            if lowered == canonical.lower() or lowered in {item.lower() for item in candidates}:
                normalized.add(canonical)
                evidence.setdefault(canonical, raw_value)
                matched = True
                break
        if not matched:
            normalized.add(raw_value)
            evidence.setdefault(raw_value, raw_value)
    return normalized, evidence


def _role_tags_from_text(text: str) -> set[str]:
    tags = set()
    lowered = text.lower()
    if any(keyword in text for keyword in ["后端", "Java", "服务端"]) or "spring" in lowered:
        tags.add("backend")
    if any(keyword in text for keyword in ["前端"]) or any(
        keyword in lowered for keyword in ["vue", "react", "javascript", "typescript", "html", "css"]
    ):
        tags.add("frontend")
    if "测试" in text or any(keyword in lowered for keyword in ["selenium", "jmeter", "postman", "pytest"]):
        tags.add("testing")
    if any(keyword in text for keyword in ["产品", "prd", "原型", "axure", "需求"]):
        tags.add("product")
    if "实施" in text:
        tags.add("implementation")
    if any(keyword in text for keyword in ["支持", "售前", "解决方案"]):
        tags.add("support")
    if any(keyword in text for keyword in ["数据", "分析"]) or any(
        keyword in lowered for keyword in ["sql", "python", "machine learning"]
    ):
        tags.add("data")
    if any(keyword in text for keyword in ["硬件", "嵌入式", "单片机", "c/c++"]) or "c++" in lowered:
        tags.add("embedded")
    return tags


def _role_alignment_bonus(student: StudentProfile, job: JobProfile) -> int:
    if not student.target_roles:
        return 0

    job_text = job.title + " " + " ".join(job.required_skills)
    job_tags = _role_tags_from_text(job_text)

    best_bonus = 0
    for target in student.target_roles:
        if target in job.title or job.title in target:
            best_bonus = max(best_bonus, 20)
            continue

        target_tags = _role_tags_from_text(target)
        if target_tags & job_tags:
            best_bonus = max(best_bonus, 12)

    return best_bonus


def _score_basic_requirements(student: StudentProfile, job: JobProfile) -> int:
    score = 60
    if job.education_requirement:
        if student.education_level == job.education_requirement:
            score += 20
        elif student.education_level in {"硕士", "博士"} and job.education_requirement in {"本科", "大专"}:
            score += 20
        else:
            score -= 20

    if job.certificates:
        shared_certificates = set(student.certificates) & set(job.certificates)
        if shared_certificates:
            score += 20

    score += _role_alignment_bonus(student, job)
    return max(0, min(score, 100))


def _score_overlap(shared: set[str], required: set[str], empty_default: int = 60) -> int:
    if not required:
        return empty_default
    return int(len(shared) / len(required) * 100)


def _score_growth_potential(student: StudentProfile) -> int:
    score = 40
    score += min(len(student.projects) * 15, 30)
    score += min(len(student.internships) * 15, 30)
    score += min(len(student.certificates) * 10, 20)
    score += min(len(student.skills) * 2, 20)
    return max(0, min(score, 100))


def _confidence_label(total: int) -> str:
    if total >= 80:
        return "高"
    if total >= 60:
        return "中"
    return "低"


def _build_strengths(
    student: StudentProfile,
    shared_skills: list[str],
    shared_soft_skills: list[str],
) -> list[str]:
    strengths = []
    if shared_skills:
        strengths.append("技能重合较好：" + "、".join(shared_skills[:5]))
    if shared_soft_skills:
        strengths.append("职业素养较契合：" + "、".join(shared_soft_skills[:4]))
    if student.projects:
        strengths.append("有项目经历，可以支撑面试中的能力举证")
    if student.internships:
        strengths.append("有实习经历，具备一定岗位适应基础")
    if not strengths:
        strengths.append("具备基础申请条件，但需要补强可证明的经历")
    return strengths


def _build_gaps(
    student: StudentProfile,
    missing_skills: list[str],
    missing_soft_skills: list[str],
    job: JobProfile,
) -> list[str]:
    gaps = []
    if missing_skills:
        gaps.append("缺少关键技能：" + "、".join(missing_skills[:5]))
    if missing_soft_skills:
        gaps.append("职业素养还可加强：" + "、".join(missing_soft_skills[:5]))
    missing_certificates = sorted(set(job.certificates) - set(student.certificates))
    if missing_certificates:
        gaps.append("证书储备不足：" + "、".join(missing_certificates))
    if student.missing_sections:
        gaps.append("简历信息不完整：" + "、".join(student.missing_sections[:4]))
    return gaps


def _build_suggestions(student: StudentProfile, missing_skills: list[str], gaps: list[str]) -> list[str]:
    suggestions = []
    if missing_skills:
        suggestions.append("优先补齐岗位核心技能：" + "、".join(missing_skills[:3]))
    if not student.internships:
        suggestions.append("尽快补充 1 段实习或真实项目经历")
    if not student.projects:
        suggestions.append("准备 1 到 2 个可展示项目，强化成果证明")
    if student.missing_sections:
        suggestions.append("先把简历基础信息补全：" + "、".join(student.missing_sections[:3]))
    if not suggestions and not gaps:
        suggestions.append("可以直接冲刺该岗位，并同步准备更高一级岗位的能力储备")
    return suggestions


def _build_explanation(
    job: JobProfile,
    total: int,
    shared_skills: list[str],
    missing_skills: list[str],
    shared_soft_skills: list[str],
    student: StudentProfile,
) -> str:
    parts = [f"学生与 {job.title} 的综合匹配度为 {total} 分。"]
    if shared_skills:
        parts.append("当前已有的关键技能包括：" + "、".join(shared_skills[:4]) + "。")
    if shared_soft_skills:
        parts.append("职业素养中较匹配的部分有：" + "、".join(shared_soft_skills[:3]) + "。")
    if missing_skills:
        parts.append("下一步最需要补强的是：" + "、".join(missing_skills[:3]) + "。")
    if student.projects or student.internships:
        parts.append("已有项目或实习经历，可以作为岗位申请时的证据支撑。")
    return "".join(parts)


def match_student_to_job(student: StudentProfile, job: JobProfile) -> MatchResult:
    student_skills, _ = _normalize_by_aliases(student.skills, SKILL_ALIASES)
    job_skills, _ = _normalize_by_aliases(job.required_skills, SKILL_ALIASES)
    student_soft, _ = _normalize_by_aliases(student.soft_skills, SOFT_SKILL_ALIASES)
    job_soft, _ = _normalize_by_aliases(job.soft_skills, SOFT_SKILL_ALIASES)

    shared_skills = sorted(student_skills & job_skills)
    missing_skills = sorted(job_skills - student_skills)
    shared_soft_skills = sorted(student_soft & job_soft)
    missing_soft_skills = sorted(job_soft - student_soft)

    basic = _score_basic_requirements(student, job)
    skills = _score_overlap(set(shared_skills), set(job_skills))
    literacy = _score_overlap(set(shared_soft_skills), set(job_soft))
    growth = _score_growth_potential(student)

    total = int(basic * 0.2 + skills * 0.4 + literacy * 0.2 + growth * 0.2)
    gaps = _build_gaps(student, missing_skills, missing_soft_skills, job)

    breakdown = MatchBreakdown(
        basic_requirements=basic,
        professional_skills=skills,
        professional_literacy=literacy,
        growth_potential=growth,
    )
    return MatchResult(
        score=total,
        breakdown=breakdown,
        strengths=_build_strengths(student, shared_skills, shared_soft_skills),
        gaps=gaps,
        suggestions=_build_suggestions(student, missing_skills, gaps),
        shared_skills=shared_skills,
        missing_skills=missing_skills,
        explanation=_build_explanation(job, total, shared_skills, missing_skills, shared_soft_skills, student),
        confidence_label=_confidence_label(total),
    )
