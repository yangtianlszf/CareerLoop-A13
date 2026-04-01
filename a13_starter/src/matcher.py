from __future__ import annotations

import math
from typing import List, Tuple
from openai import OpenAI

from a13_starter.src.settings import get_openai_api_key, get_openai_base_url
from a13_starter.src.models import JobProfile, MatchBreakdown, MatchResult, StudentProfile


def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """调用大模型 Embedding API 将文本转化为高维向量"""
    if not texts:
        return []
    
    client = OpenAI(
        api_key=get_openai_api_key(),
        base_url=get_openai_base_url()
    )
    
    # 注意：如果你使用的是 DashScope (阿里云灵积)，可以使用 'text-embedding-v1' 或 'text-embedding-v2'
    # 如果是 OpenAI 原生，通常使用 'text-embedding-3-small'
    # 这里默认写 text-embedding-v1，请根据你实际支持的模型进行调整
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-v1" 
    )
    return [item.embedding for item in response.data]


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """计算两个向量的余弦相似度"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def _semantic_match_skills(student_skills: list[str], job_skills: list[str], threshold: float = 0.82) -> tuple[list[str], list[str]]:
    """
    基于语义向量的技能匹配引擎。
    返回: (共享技能列表, 缺失技能列表)
    """
    if not job_skills:
        return student_skills, []
    if not student_skills:
        return [], job_skills

    # 批量获取向量
    student_vecs = _get_embeddings(student_skills)
    job_vecs = _get_embeddings(job_skills)

    shared_skills = []
    missing_skills = []

    # 遍历企业的每一项要求，去学生的技能池里找“最相似”的一项
    for i, j_skill in enumerate(job_skills):
        j_vec = job_vecs[i]
        best_match_score = 0.0
        
        for j, s_skill in enumerate(student_skills):
            s_vec = student_vecs[j]
            score = _cosine_similarity(j_vec, s_vec)
            if score > best_match_score:
                best_match_score = score
                
        # 如果最高相似度超过阈值，认为学生掌握了该技能
        if best_match_score >= threshold:
            shared_skills.append(j_skill) 
        else:
            missing_skills.append(j_skill)

    return list(set(shared_skills)), list(set(missing_skills))


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
    # 🌟 核心升级：使用纯语义向量匹配替代规则别名匹配
    shared_skills, missing_skills = _semantic_match_skills(student.skills, job.required_skills, threshold=0.82)
    shared_soft_skills, missing_soft_skills = _semantic_match_skills(student.soft_skills, job.soft_skills, threshold=0.85)

    # 排序以保证输出结果顺序一致性
    shared_skills = sorted(shared_skills)
    missing_skills = sorted(missing_skills)
    shared_soft_skills = sorted(shared_soft_skills)
    missing_soft_skills = sorted(missing_soft_skills)

    # 计算各维度得分
    basic = _score_basic_requirements(student, job)
    skills_score = _score_overlap(set(shared_skills), set(job.required_skills))
    literacy_score = _score_overlap(set(shared_soft_skills), set(job.soft_skills))
    growth = _score_growth_potential(student)

    # 综合算分
    total = int(basic * 0.2 + skills_score * 0.4 + literacy_score * 0.2 + growth * 0.2)
    gaps = _build_gaps(student, missing_skills, missing_soft_skills, job)

    breakdown = MatchBreakdown(
        basic_requirements=basic,
        professional_skills=skills_score,
        professional_literacy=literacy_score,
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