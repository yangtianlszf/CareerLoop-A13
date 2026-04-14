from __future__ import annotations

import math
import re
from typing import List, Tuple

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency for semantic matching
    OpenAI = None

from a13_starter.src.role_normalizer import normalize_job_title
from a13_starter.src.settings import get_openai_api_key, get_openai_base_url, llm_is_configured
from a13_starter.src.models import JobProfile, MatchBreakdown, MatchResult, StudentProfile
from a13_starter.src.skill_taxonomy import normalize_skill_alias, normalize_skill_list


_ROLE_TAG_SIGNALS: dict[str, tuple[tuple[str, int], ...]] = {
    "backend": (
        ("后端", 4),
        ("java开发", 4),
        ("服务端", 4),
        ("python开发", 3),
        ("spring", 2),
        ("spring boot", 3),
        ("接口开发", 3),
        ("接口设计", 3),
        ("数据库设计", 2),
    ),
    "frontend": (
        ("前端", 4),
        ("web前端", 4),
        ("vue", 3),
        ("react", 3),
        ("javascript", 2),
        ("typescript", 2),
        ("html", 1),
        ("css", 1),
        ("交互", 1),
    ),
    "testing": (
        ("测试开发", 4),
        ("自动化测试", 4),
        ("功能测试", 3),
        ("接口测试", 3),
        ("测试用例", 3),
        ("回归测试", 2),
        ("缺陷", 2),
        ("selenium", 2),
        ("pytest", 2),
        ("jmeter", 2),
        ("联调测试", 2),
    ),
    "product": (
        ("产品", 4),
        ("prd", 3),
        ("原型", 3),
        ("axure", 3),
        ("需求分析", 2),
        ("用户研究", 2),
        ("需求文档", 2),
    ),
    "implementation": (
        ("实施", 4),
        ("交付", 4),
        ("上线", 3),
        ("部署", 3),
        ("系统部署", 4),
        ("培训", 3),
        ("现场", 2),
        ("环境配置", 2),
        ("初始化", 2),
        ("使用手册", 2),
    ),
    "support": (
        ("技术支持", 4),
        ("售前", 4),
        ("售后", 3),
        ("解决方案", 4),
        ("故障排查", 3),
        ("问题定位", 3),
        ("工单", 2),
        ("客户", 1),
        ("服务意识", 2),
    ),
    "data": (
        ("数据分析师", 5),
        ("商业分析", 4),
        ("bi", 3),
        ("数据分析", 3),
        ("数据清洗", 3),
        ("可视化", 3),
        ("指标", 3),
        ("报表", 3),
        ("数据看板", 3),
        ("excel", 3),
        ("ppt", 2),
        ("留存", 2),
        ("复购", 2),
        ("流失", 2),
        ("用户分层", 2),
        ("经营分析", 2),
        ("异常指标", 2),
    ),
    "operations": (
        ("运营专员", 5),
        ("内容运营", 4),
        ("用户运营", 4),
        ("社区运营", 4),
        ("新媒体运营", 4),
        ("运营", 3),
        ("增长", 2),
        ("活动运营", 3),
        ("活动策划", 2),
        ("内容策划", 2),
        ("裂变", 2),
        ("转化", 2),
        ("seo", 2),
        ("粉丝", 2),
    ),
    "project": (
        ("项目专员", 5),
        ("项目经理", 5),
        ("项目管理", 3),
        ("里程碑", 2),
        ("风险控制", 2),
        ("资源分配", 2),
        ("会议纪要", 2),
        ("跨部门", 1),
        ("行动项", 1),
    ),
    "embedded": (
        ("硬件", 4),
        ("嵌入式", 4),
        ("单片机", 3),
        ("c/c++", 3),
        ("c++", 3),
        ("电路", 2),
        ("硬件调试", 3),
    ),
}


def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """调用大模型 Embedding API 将文本转化为高维向量"""
    if not texts:
        return []
    if OpenAI is None or not llm_is_configured():
        raise RuntimeError("Embedding client is unavailable")
    
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


def _normalize_skill_text(text: str) -> str:
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff+#.]+", "", text).lower()


def _canonicalize_skills_for_matching(skills: list[str]) -> list[tuple[str, str]]:
    canonical_skills = normalize_skill_list(skills)
    canonical_lookup = {normalize_skill_alias(skill): skill for skill in skills}
    pairs: list[tuple[str, str]] = []
    for canonical in canonical_skills:
        display = canonical_lookup.get(canonical, canonical)
        pairs.append((display, _normalize_skill_text(canonical)))
    return pairs


def _rule_based_match_skills(student_skills: list[str], job_skills: list[str]) -> tuple[list[str], list[str]]:
    if not job_skills:
        return student_skills, []
    if not student_skills:
        return [], job_skills

    normalized_student_skills = _canonicalize_skills_for_matching(student_skills)
    normalized_job_skills = _canonicalize_skills_for_matching(job_skills)

    shared_skills: list[str] = []
    missing_skills: list[str] = []
    for job_skill, job_skill_normalized in normalized_job_skills:
        matched = any(
            job_skill_normalized == student_skill_normalized
            or job_skill_normalized in student_skill_normalized
            or student_skill_normalized in job_skill_normalized
            for _, student_skill_normalized in normalized_student_skills
            if job_skill_normalized and student_skill_normalized
        )
        if matched:
            shared_skills.append(job_skill)
        else:
            missing_skills.append(job_skill)
    return list(dict.fromkeys(shared_skills)), list(dict.fromkeys(missing_skills))


def _semantic_match_skills(student_skills: list[str], job_skills: list[str], threshold: float = 0.82) -> tuple[list[str], list[str]]:
    """
    基于语义向量的技能匹配引擎。
    返回: (共享技能列表, 缺失技能列表)
    """
    if not job_skills:
        return student_skills, []
    if not student_skills:
        return [], job_skills

    canonical_student_skills = normalize_skill_list(student_skills)
    canonical_job_skills = normalize_skill_list(job_skills)
    if not canonical_student_skills or not canonical_job_skills:
        return _rule_based_match_skills(student_skills, job_skills)

    try:
        # 优先使用语义向量匹配；依赖缺失或调用失败时回退到规则匹配，保证服务可用。
        student_vecs = _get_embeddings(canonical_student_skills)
        job_vecs = _get_embeddings(canonical_job_skills)
    except Exception:
        return _rule_based_match_skills(student_skills, job_skills)

    shared_skills = []
    missing_skills = []

    # 遍历企业的每一项要求，去学生的技能池里找“最相似”的一项
    for i, j_skill in enumerate(canonical_job_skills):
        j_vec = job_vecs[i]
        best_match_score = 0.0
        
        for j, _ in enumerate(canonical_student_skills):
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


def _merge_tag_scores(base: dict[str, int], extra: dict[str, int]) -> dict[str, int]:
    for tag, score in extra.items():
        base[tag] = base.get(tag, 0) + score
    return base


def _role_tag_scores_from_text(text: str, multiplier: int = 1) -> dict[str, int]:
    source = str(text or "").strip()
    if not source:
        return {}

    lowered = source.lower()
    scores: dict[str, int] = {}
    for tag, signals in _ROLE_TAG_SIGNALS.items():
        tag_score = 0
        for keyword, weight in signals:
            if keyword.lower() in lowered:
                tag_score += weight
        if tag_score > 0:
            scores[tag] = tag_score * max(1, multiplier)
    return scores


def _primary_role_tags(scores: dict[str, int]) -> set[str]:
    if not scores:
        return set()
    max_score = max(scores.values())
    threshold = max(4, max_score - 2)
    return {tag for tag, score in scores.items() if score >= threshold}


def _normalize_role_title(text: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    return normalize_job_title(cleaned, detail=cleaned, industry="")


def _role_tags_from_text(text: str) -> set[str]:
    return set(_role_tag_scores_from_text(text))


def _collect_student_evidence_tag_scores(student: StudentProfile) -> dict[str, int]:
    scores: dict[str, int] = {}
    for internship in student.internships:
        _merge_tag_scores(scores, _role_tag_scores_from_text(internship, multiplier=3))
    for project in student.projects:
        _merge_tag_scores(scores, _role_tag_scores_from_text(project, multiplier=2))
    for award in student.awards:
        _merge_tag_scores(scores, _role_tag_scores_from_text(award, multiplier=1))
    if not scores and student.skills:
        _merge_tag_scores(scores, _role_tag_scores_from_text(" ".join(student.skills), multiplier=1))
    return scores


def _role_alignment_adjustment(student: StudentProfile, job: JobProfile) -> int:
    if not student.target_roles and not student.projects and not student.internships:
        return 0

    job_scores: dict[str, int] = {}
    _merge_tag_scores(job_scores, _role_tag_scores_from_text(job.title, multiplier=3))
    _merge_tag_scores(job_scores, _role_tag_scores_from_text(job.raw_text, multiplier=2))
    _merge_tag_scores(job_scores, _role_tag_scores_from_text(" ".join(job.required_skills), multiplier=1))
    if not job_scores:
        return 0

    target_scores = _role_tag_scores_from_text(" ".join(student.target_roles), multiplier=2)
    evidence_scores = _collect_student_evidence_tag_scores(student)

    normalized_job_title = _normalize_role_title(job.title)
    normalized_targets = {
        normalized
        for normalized in (_normalize_role_title(target) for target in student.target_roles)
        if normalized
    }

    job_primary_tags = _primary_role_tags(job_scores)
    target_primary_tags = _primary_role_tags(target_scores)
    evidence_primary_tags = _primary_role_tags(evidence_scores)

    adjustment = 0
    if normalized_job_title and normalized_job_title in normalized_targets:
        adjustment += 4

    if target_primary_tags:
        if job_primary_tags & target_primary_tags:
            adjustment += 3
        else:
            adjustment -= 2

    if evidence_primary_tags:
        if job_primary_tags & evidence_primary_tags:
            adjustment += 6
        else:
            adjustment -= 4

    return max(-8, min(adjustment, 12))


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
    
    # 🌟 修复证书智障匹配：引入向上兼容机制（如 CET-6 覆盖 CET-4）
    missing_certificates = []
    student_certs_str = " ".join(student.certificates).lower()
    
    for required_cert in job.certificates:
        req_lower = required_cert.lower()
        
        # 1. 如果企业要求四级，但学生画像里有六级，则算作满足要求，跳过
        if "四级" in req_lower and "六级" in student_certs_str:
            continue
            
        # 2. 如果企业要求软考初级，学生有中级/高级，跳过（可在此扩展更多规则）
        if "初级" in req_lower and ("中级" in student_certs_str or "高级" in student_certs_str):
            continue

        # 如果确实没有，且不满足覆盖条件，再加入缺失名单
        if required_cert not in student.certificates:
            missing_certificates.append(required_cert)

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
    if len(suggestions) < 2:
        suggestions.append("挑 3 份真实 JD 做定制化简历改写，并准备 1 套项目讲稿")
    if len(suggestions) < 3:
        suggestions.append("围绕目标岗位完成 8 到 10 道高频面试题复盘，形成下一轮复测清单")
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
    else:
        parts.append("当前更适合先补一个可展示项目，再进入集中投递。")
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
    alignment_adjustment = _role_alignment_adjustment(student, job)

    # 综合算分
    total = int(basic * 0.2 + skills_score * 0.4 + literacy_score * 0.2 + growth * 0.2) + alignment_adjustment
    total = max(0, min(total, 100))
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
