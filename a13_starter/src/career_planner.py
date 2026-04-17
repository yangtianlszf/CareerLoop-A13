from __future__ import annotations

import re
from typing import Any

from a13_starter.src.analysis_storage import find_similar_analyses
from a13_starter.src.citation_utils import annotate_text_with_citations, build_term_citation_map
from a13_starter.src.evidence_retrieval import build_grounded_evidence_bundle
from a13_starter.src.extractors import refresh_student_profile_metrics
from a13_starter.src.jd_search import load_role_templates
from a13_starter.src.matcher import match_student_to_job, role_primary_tags
from a13_starter.src.models import CareerPlan, JobProfile, StudentProfile
from a13_starter.src.openai_responses import OpenAIResponsesClient  # 🌟 新增：引入大模型客户端
from a13_starter.src.role_normalizer import normalize_job_title
from a13_starter.src.skill_taxonomy import normalize_skill_alias, normalize_skill_list


def template_to_job_profile(template: dict[str, object]) -> JobProfile:
    summary = str(template.get("summary", ""))
    raw_text = "\n".join(
        [
            str(template.get("canonical_title", "")),
            "岗位说明：",
            summary,
            "核心技能：" + "、".join(template.get("core_skills", [])),
            "软技能：" + "、".join(template.get("soft_skills", [])),
            "证书要求：" + "、".join(template.get("certificates", [])),
            "学历要求：" + str(template.get("education_requirement", "")),
            "经验要求：" + str(template.get("experience_requirement", "")),
        ]
    )
    return JobProfile(
        title=str(template.get("canonical_title", "")),
        raw_text=raw_text,
        required_skills=list(template.get("core_skills", [])),
        soft_skills=list(template.get("soft_skills", [])),
        certificates=list(template.get("certificates", [])),
        education_requirement=str(template.get("education_requirement", "")),
        experience_requirement=str(template.get("experience_requirement", "")),
        city=None,
        salary_range=None,
        growth_path=list(template.get("vertical_growth_path", [])),
    )


def rank_student_against_templates(
    student: StudentProfile,
    templates: list[dict[str, object]],
    top_k: int | None = None,
) -> list[dict[str, object]]:
    matches = []
    for template in templates:
        job_profile = template_to_job_profile(template)
        match = match_student_to_job(student, job_profile)
        ranking_context_bonus = _ranking_context_bonus(student, template, match)
        final_score = min(100, int(match.score) + ranking_context_bonus)
        explanation = str(match.explanation)
        if final_score != int(match.score):
            explanation = explanation.replace(
                f"综合匹配度为 {int(match.score)} 分",
                f"综合匹配度为 {final_score} 分",
                1,
            )
        matches.append(
            {
                "role_title": template["canonical_title"],
                "role_family": template["role_family"],
                "score": final_score,
                "base_score": match.score,
                "ranking_context_bonus": ranking_context_bonus,
                "breakdown": match.breakdown.to_dict(),
                "strengths": match.strengths,
                "gaps": match.gaps,
                "suggestions": match.suggestions,
                "shared_skills": match.shared_skills,
                "missing_skills": match.missing_skills,
                "explanation": explanation,
                "confidence_label": _confidence_label(final_score),
                "transition_paths": template["transition_paths"],
                "growth_path": template["vertical_growth_path"],
                "summary": template["summary"],
                "core_skills": template["core_skills"],
                "preferred_skills": template["preferred_skills"],
            }
        )
    matches.sort(
        key=lambda item: (
            int(item.get("score", 0)),
            int(item.get("base_score", 0)),
            len(item.get("shared_skills", [])),
            -len(item.get("missing_skills", [])),
        ),
        reverse=True,
    )
    if top_k is None:
        return matches
    return matches[:top_k]


def _normalize_role_label(role_title: str) -> str:
    cleaned = str(role_title or "").strip()
    if not cleaned:
        return ""
    return normalize_job_title(cleaned, detail=cleaned, industry="")


def _normalized_role_labels(role_titles: list[str] | None) -> set[str]:
    normalized: set[str] = set()
    for role_title in role_titles or []:
        role = _normalize_role_label(str(role_title))
        if role:
            normalized.add(role)
    return normalized


def _primary_target_role(student: StudentProfile) -> str:
    if not student.target_roles:
        return ""
    return _normalize_role_label(str(student.target_roles[0]))


def _confidence_label(total: int) -> str:
    if total >= 80:
        return "高"
    if total >= 60:
        return "中"
    return "低"


def _normalize_city_label(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text.split("-")[0].replace("市", "").strip().lower()


def _city_preference_matches(student: StudentProfile, template: dict[str, object]) -> bool:
    preferred_city = _normalize_city_label(student.city_preference or "")
    if not preferred_city:
        return False
    for city in list(template.get("typical_cities", [])) or []:
        template_city = _normalize_city_label(str(city))
        if template_city and (preferred_city in template_city or template_city in preferred_city):
            return True
    return False


def _industry_overlap(student: StudentProfile, template: dict[str, object]) -> bool:
    target_industries = [str(item).strip().lower() for item in student.target_industries if str(item).strip()]
    if not target_industries:
        return False
    for industry in list(template.get("typical_industries", [])) or []:
        lowered_industry = str(industry).strip().lower()
        if not lowered_industry:
            continue
        if any(
            target in lowered_industry or lowered_industry in target
            for target in target_industries
            if target
        ):
            return True
    return False


def _ranking_context_bonus(
    student: StudentProfile,
    template: dict[str, object],
    match: MatchResult,
) -> int:
    shared_count = len(match.shared_skills)
    role_title = str(template.get("canonical_title", ""))
    normalized_role = _normalize_role_label(role_title)
    normalized_targets = _normalized_role_labels(student.target_roles)
    primary_target = _primary_target_role(student)
    candidate_tags = role_primary_tags(role_title)
    target_tags = role_primary_tags(" ".join(student.target_roles))

    bonus = 0
    if normalized_role and normalized_role in normalized_targets and shared_count >= 2:
        bonus += 3
        if primary_target and normalized_role == primary_target:
            bonus += 2
    elif shared_count >= 2 and candidate_tags and target_tags and candidate_tags & target_tags:
        bonus += 1

    scenario_match = False
    if int(match.score) >= 55 and shared_count >= 2 and _industry_overlap(student, template):
        scenario_match = True
    if int(match.score) >= 60 and shared_count >= 2 and _city_preference_matches(student, template):
        scenario_match = True
    if scenario_match:
        bonus += 1

    return min(bonus, 6)


def _strategy_lane_score(
    student: StudentProfile,
    primary_match: dict[str, Any],
    candidate: dict[str, Any],
    lane: str,
    selected_families: set[str],
) -> int:
    score = int(candidate.get("score", 0))
    candidate_title = str(candidate.get("role_title", ""))
    candidate_family = str(candidate.get("role_family", "综合"))
    primary_family = str(primary_match.get("role_family", "综合"))
    candidate_missing = len(candidate.get("missing_skills", []))
    candidate_shared = len(candidate.get("shared_skills", []))

    normalized_candidate = _normalize_role_label(candidate_title)
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))

    explicit_target = normalized_candidate in normalized_targets
    in_transition_path = normalized_candidate in normalized_transitions
    same_family = candidate_family == primary_family
    score_gap = max(0, int(primary_match.get("score", 0)) - score)

    adjusted = score
    if lane == "cross":
        if explicit_target:
            adjusted += 12
        if in_transition_path:
            adjusted += 10
        if not same_family:
            adjusted += 5
        if candidate_family not in selected_families:
            adjusted += 2
        if candidate_shared >= 2:
            adjusted += 2
        if candidate_missing <= 2:
            adjusted += 2
        if same_family and not explicit_target and not in_transition_path:
            adjusted -= 6
        if score_gap > 28:
            adjusted -= 4
    else:
        if explicit_target:
            adjusted += 12
        if in_transition_path:
            adjusted += 15
        if same_family:
            adjusted += 4
        if candidate_family not in selected_families:
            adjusted += 2
        if candidate_missing <= 2:
            adjusted += 3
        if candidate_shared >= 2:
            adjusted += 2
        if score_gap > 22:
            adjusted -= 2
    return adjusted


def _select_application_matches(
    student: StudentProfile,
    ranked_matches: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    if not ranked_matches:
        return []

    primary_match = ranked_matches[0]
    remaining = list(ranked_matches[1: max(limit + 6, 8)])
    selected = [primary_match]
    selected_titles = {str(primary_match.get("role_title", ""))}
    selected_families = {str(primary_match.get("role_family", "综合"))}

    lane_order = ["cross", "safety"]
    for lane in lane_order[: max(0, limit - 1)]:
        available = [item for item in remaining if str(item.get("role_title", "")) not in selected_titles]
        if not available:
            break
        chosen = max(
            available,
            key=lambda item: _strategy_lane_score(student, primary_match, item, lane, selected_families),
        )
        selected.append(chosen)
        selected_titles.add(str(chosen.get("role_title", "")))
        selected_families.add(str(chosen.get("role_family", "综合")))

    if len(selected) < limit:
        for item in ranked_matches[1:]:
            title = str(item.get("role_title", ""))
            if title in selected_titles:
                continue
            selected.append(item)
            selected_titles.add(title)
            if len(selected) >= limit:
                break

    return selected[:limit]


def _application_positioning(
    student: StudentProfile,
    primary_match: dict[str, Any],
    match: dict[str, Any],
    lane_label: str,
) -> str:
    role_title = str(match.get("role_title", "目标岗位"))
    normalized_role = _normalize_role_label(role_title)
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))

    if lane_label == "主攻":
        return "当前最值得集中资源冲刺的岗位，优先匹配简历、项目讲稿和面试准备。"
    if normalized_role in normalized_targets:
        return "这是学生明确表达过的意向方向，适合作为保留并持续验证的第二赛道。"
    if normalized_role in normalized_transitions:
        return "这是主岗位的相邻迁移路径，共享较多底层能力，适合横向扩展投递。"
    if str(match.get("role_family", "")) != str(primary_match.get("role_family", "")):
        return "这是用于分散求职风险的跨族岗位，适合在不脱离能力底座的前提下提高面邀概率。"
    return "这是与主岗位能力栈接近的备选方向，可作为阶段性兜底选择。"


def _application_selection_reason(
    student: StudentProfile,
    primary_match: dict[str, Any],
    match: dict[str, Any],
) -> str:
    normalized_role = _normalize_role_label(str(match.get("role_title", "")))
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))
    reasons: list[str] = []

    if normalized_role in normalized_targets:
        reasons.append("命中学生明确写下的目标岗位")
    if normalized_role in normalized_transitions:
        reasons.append("位于主岗位模板的横向迁移路径中")
    if match.get("shared_skills"):
        reasons.append("已验证共享技能：" + _join_or_default(list(match.get("shared_skills", [])), "基础技能", limit=2))
    if match.get("missing_skills"):
        reasons.append("主要缺口集中在：" + _join_or_default(list(match.get("missing_skills", [])), "项目表达", limit=2))
    return "；".join(reasons[:3]) if reasons else "当前分数和证据链较稳定，适合纳入投递矩阵。"


def _application_risk_note(primary_match: dict[str, Any], match: dict[str, Any], lane_label: str) -> str:
    missing_skills = list(match.get("missing_skills", []))
    if lane_label == "主攻":
        return (
            "主风险在于" + _join_or_default(missing_skills, "项目举证", limit=2) + "仍需补成可面试的案例。"
            if missing_skills
            else "当前短板主要转为表达和面试稳定性，建议尽快进入模拟面试。"
        )
    score_gap = max(0, int(primary_match.get("score", 0)) - int(match.get("score", 0)))
    if score_gap >= 15:
        return f"与主岗位相比仍有 {score_gap} 分差，需要控制投递比例，避免过早分散精力。"
    if missing_skills:
        return "该方向的短板主要在 " + _join_or_default(missing_skills, "项目表达", limit=2) + "，投递前最好先补 1 个最小案例。"
    return "该方向可直接保留在投递池中，但建议沿用主项目证据，避免重新起一套故事线。"


def _comparison_lane_label(strategy_matches: list[dict[str, Any]], role_title: str) -> str:
    lane_labels = ["主攻", "跨投", "保底"]
    for index, match in enumerate(strategy_matches[:3]):
        if str(match.get("role_title", "")) == role_title:
            return lane_labels[index]
    return "候选"


def _comparison_candidates(
    student: StudentProfile,
    ranked_matches: list[dict[str, Any]],
    strategy_matches: list[dict[str, Any]],
    limit: int = 4,
) -> list[tuple[int, dict[str, Any]]]:
    if not ranked_matches:
        return []

    strategy_titles = {str(item.get("role_title", "")) for item in strategy_matches[1:]}
    normalized_targets = _normalized_role_labels(student.target_roles)
    candidates: list[tuple[int, dict[str, Any]]] = []
    selected_titles: set[str] = set()

    for index, match in enumerate(ranked_matches[1:7], start=2):
        role_title = str(match.get("role_title", ""))
        normalized_title = _normalize_role_label(role_title)
        if not role_title or role_title in selected_titles:
            continue
        if (
            index <= 3
            or role_title in strategy_titles
            or normalized_title in normalized_targets
        ):
            candidates.append((index, match))
            selected_titles.add(role_title)
        if len(candidates) >= limit:
            return candidates[:limit]

    for match in strategy_matches[1:]:
        role_title = str(match.get("role_title", ""))
        if not role_title or role_title in selected_titles:
            continue
        rank_position = next(
            (idx for idx, item in enumerate(ranked_matches, start=1) if str(item.get("role_title", "")) == role_title),
            99,
        )
        candidates.append((rank_position, match))
        selected_titles.add(role_title)
        if len(candidates) >= limit:
            break
    return candidates[:limit]


def _comparison_primary_advantage(primary_match: dict[str, Any], candidate: dict[str, Any]) -> str:
    primary_shared = list(primary_match.get("shared_skills", []))
    primary_missing = list(primary_match.get("missing_skills", []))
    candidate_missing = list(candidate.get("missing_skills", []))
    parts: list[str] = []

    if primary_shared:
        parts.append("主岗位已稳定命中 " + _join_or_default(primary_shared, "核心技能", limit=2))
    if len(primary_missing) < len(candidate_missing):
        parts.append("关键缺口更少")
    elif not primary_missing:
        parts.append("当前几乎没有硬缺口，更适合直接进入投递和面试")
    return "；".join(parts[:3]) if parts else "主岗位的现有证据链更完整，执行成本更低。"


def _comparison_candidate_value(
    student: StudentProfile,
    primary_match: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    role_title = str(candidate.get("role_title", "目标岗位"))
    normalized_role = _normalize_role_label(role_title)
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))
    shared_skills = list(candidate.get("shared_skills", []))
    parts: list[str] = []

    if normalized_role in normalized_targets:
        parts.append("它仍是学生明确表达过的意向方向")
    if normalized_role in normalized_transitions:
        parts.append("它位于主岗位的迁移路径中")
    if shared_skills:
        parts.append("已有 " + _join_or_default(shared_skills, "基础能力", limit=2) + " 可直接复用")
    return "；".join(parts[:3]) if parts else "它仍可作为备选方向保留在投递池中。"


def _comparison_why_not_first(
    student: StudentProfile,
    primary_match: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    primary_score = int(primary_match.get("score", 0))
    candidate_score = int(candidate.get("score", 0))
    score_gap = max(0, primary_score - candidate_score)
    primary_shared = len(primary_match.get("shared_skills", []))
    candidate_shared = len(candidate.get("shared_skills", []))
    primary_missing = list(primary_match.get("missing_skills", []))
    candidate_missing = list(candidate.get("missing_skills", []))
    normalized_role = _normalize_role_label(str(candidate.get("role_title", "")))
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))

    reasons: list[str] = []
    if score_gap > 0:
        reasons.append(f"当前综合匹配分比主岗位低 {score_gap} 分")
    if len(candidate_missing) > len(primary_missing):
        reasons.append("关键缺口更多，主要还差 " + _join_or_default(candidate_missing, "岗位证据", limit=2))
    elif candidate_missing and not primary_missing:
        reasons.append("仍缺 " + _join_or_default(candidate_missing, "岗位证据", limit=2) + " 的直接案例")
    if candidate_shared < primary_shared:
        reasons.append(f"已验证共享技能少于主岗位（{candidate_shared} vs {primary_shared}）")
    if (
        str(candidate.get("role_family", "")) != str(primary_match.get("role_family", ""))
        and normalized_role not in normalized_targets
        and normalized_role not in normalized_transitions
    ):
        reasons.append("与当前主叙事不在同一岗位族，切过去需要重新组织简历和项目故事")
    if not reasons:
        reasons.append("虽然也具备投递价值，但当前稳定性和证据密度还不如主岗位")
    return "；".join(reasons[:4]) + "。"


def _comparison_upgrade_path(
    student: StudentProfile,
    primary_match: dict[str, Any],
    candidate: dict[str, Any],
) -> str:
    role_title = str(candidate.get("role_title", "该岗位"))
    missing_skills = list(candidate.get("missing_skills", []))
    normalized_role = _normalize_role_label(role_title)
    normalized_targets = _normalized_role_labels(student.target_roles)
    normalized_transitions = _normalized_role_labels(list(primary_match.get("transition_paths", [])))
    upgrade_focus = _join_or_default(missing_skills, "项目表达", limit=2)

    if normalized_role in normalized_targets:
        return f"如果补齐 {upgrade_focus}，并把现有项目改写成更贴近 {role_title} 的案例，它有机会在下一轮上升到主推位。"
    if normalized_role in normalized_transitions:
        return f"如果未来想把 {role_title} 升成第一优先，需要先补齐 {upgrade_focus}，再补 1 段更贴近该岗位职责的项目或实习证据。"
    return f"若想把 {role_title} 提升到第一，需要补齐 {upgrade_focus}，并准备一套独立于主岗位的求职叙事与作品证据。"


def _build_recommendation_comparisons(
    student: StudentProfile,
    primary_match: dict[str, Any],
    ranked_matches: list[dict[str, Any]],
    strategy_matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comparison_items: list[dict[str, Any]] = []
    for raw_rank, candidate in _comparison_candidates(student, ranked_matches, strategy_matches):
        role_title = str(candidate.get("role_title", "候选岗位"))
        comparison_items.append(
            {
                "role_title": role_title,
                "role_family": str(candidate.get("role_family", "综合")),
                "fit_score": int(candidate.get("score", 0)),
                "raw_rank": raw_rank,
                "lane": _comparison_lane_label(strategy_matches, role_title),
                "score_gap": max(0, int(primary_match.get("score", 0)) - int(candidate.get("score", 0))),
                "why_not_first": _comparison_why_not_first(student, primary_match, candidate),
                "primary_advantage": _comparison_primary_advantage(primary_match, candidate),
                "candidate_value": _comparison_candidate_value(student, primary_match, candidate),
                "upgrade_path": _comparison_upgrade_path(student, primary_match, candidate),
            }
        )
    return comparison_items[:4]


def _extract_gap_keywords(gaps: list[str]) -> list[str]:
    keywords: list[str] = []
    for gap in gaps:
        if "：" not in gap:
            continue
        _, raw_items = gap.split("：", 1)
        for item in raw_items.split("、"):
            cleaned = item.strip()
            if cleaned and cleaned not in keywords:
                keywords.append(cleaned)
    return keywords


def _split_answer_items(raw_value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[、,，/；;]", raw_value) if item.strip()]


def apply_agent_answers(student: StudentProfile, answers: dict[str, str] | None) -> StudentProfile:
    if not answers:
        return student

    cleaned_answers = {
        key: str(value).strip()
        for key, value in answers.items()
        if str(key).strip() and str(value).strip()
    }
    if not cleaned_answers:
        return student

    if cleaned_answers.get("target_role"):
        student.target_roles = _split_answer_items(cleaned_answers["target_role"])
    if cleaned_answers.get("preferred_city"):
        student.city_preference = cleaned_answers["preferred_city"]
    if cleaned_answers.get("target_industry"):
        student.target_industries = _split_answer_items(cleaned_answers["target_industry"])

    student.agent_answers.update(cleaned_answers)
    return refresh_student_profile_metrics(student)


def _generate_ai_match_commentary(
    role_title: str,
    score: int,
    strengths: list[str],
    missing_skills: list[str],
) -> str:
    """调用大模型为 Top1 匹配岗位生成 2-3 句 AI 评审意见，增强 LLM 存在感"""
    system_prompt = (
        "你是一位专业的职业规划评审专家。请根据学生与目标岗位的匹配情况，"
        "用 2-3 句话写出简洁、专业的 AI 评审意见。语气肯定而务实，"
        "要指出当前优势并点明最关键的提升方向，不要说废话，不要重复数字。"
    )
    strengths_str = "、".join(strengths[:2]) if strengths else "有一定基础能力"
    gaps_str = "、".join(missing_skills[:2]) if missing_skills else "综合能力有待打磨"
    user_prompt = (
        f"目标岗位：{role_title}，当前匹配分：{score} 分。\n"
        f"已验证优势：{strengths_str}。\n"
        f"关键差距：{gaps_str}。\n"
        f"请给出你的 AI 评审意见（2-3 句话）。"
    )
    try:
        client = OpenAIResponsesClient()
        result = client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
        return str(result).strip() if result else ""
    except Exception as e:
        print(f"AI 评审意见生成失败，将跳过显示: {e}")
        return ""


# 🌟 新增：动态大模型规划引擎，用于消灭硬编码
def _generate_dynamic_role_guidance(role_title: str, missing_skills: list[str]) -> dict[str, Any]:
    """利用大模型动态生成个性化的项目建议和自测题，消灭硬编码"""
    schema = {
        "type": "object",
        "properties": {
            "recommended_projects": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2条具体的项目实战建议，必须结合目标岗位和学生的技能缺口来写。"
            },
            "assessment_tasks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2条岗前复测考核任务。"
            },
            "self_assessment_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "prompt": {"type": "string", "description": "具体的自测提问语句"},
                        "focus": {"type": "string", "description": "考察的维度名称"}
                    },
                    "required": ["id", "prompt", "focus"],
                    "additionalProperties": False
                },
                "description": "3道岗位自测题，需针对学生薄弱项。"
            }
        },
        "required": ["recommended_projects", "assessment_tasks", "self_assessment_questions"],
        "additionalProperties": False
    }

    system_prompt = "你是一个资深的职业规划导师和技术面试官。请根据学生意向的目标岗位和当前缺失的核心技能，动态生成高价值、可执行的项目实战建议、复测考核任务和自测问卷。拒绝假大空的套话，要给出具体的业务场景或技术栈要求。"
    skills_str = "、".join(missing_skills[:3]) if missing_skills else "通用实战经验"
    user_prompt = f"目标岗位：{role_title}\n该学生当前急需补强的关键技能缺口：{skills_str}\n请为他量身定制冲刺方案。"

    try:
        client = OpenAIResponsesClient()
        return client.create_structured_output(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema_name="dynamic_guidance",
            schema=schema
        )
    except Exception as e:
        print(f"动态生成指导方案失败, 将使用规则兜底: {e}")
        return {}


def _project_suggestions_for_role(role_title: str) -> list[str]:
    # 保留原有的规则映射，作为大模型调用失败时的安全兜底 (Fallback)
    role_map = {
        "Java开发工程师": [
            "做一个带登录、权限和数据库的管理系统后端项目",
            "补一个接口文档和部署说明，体现工程化能力",
        ],
        "前端开发工程师": [
            "做一个可交互的职业规划前端页面，展示匹配分和路径图谱",
            "补一个响应式页面项目，并加上接口联调截图",
        ],
        "测试工程师": [
            "做一套接口测试用例和缺陷跟踪表",
            "补一个自动化测试脚本项目，体现质量保障能力",
        ],
        "软件测试工程师": [
            "基于接口文档写自动化测试脚本",
            "整理一份完整的测试计划、测试用例和缺陷报告",
        ],
        "测试开发工程师": [
            "搭建一套 Python + Selenium/Pytest 的自动化测试框架，并接入 Jenkins CI",
            "输出完整的测试报告和接口自动化覆盖率数据",
        ],
        "实施工程师": [
            "做一份系统部署与用户培训手册",
            "补一份上线问题排查清单和交付演示文档",
        ],
        "技术支持工程师": [
            "做一份常见问题知识库和工单处理流程图",
            "准备 2 个典型故障排查案例",
        ],
        "C/C++开发工程师": [
            "做一个底层模块或小型系统工具项目",
            "补一份性能优化或调试记录，体现工程能力",
        ],
        "硬件测试工程师": [
            "做一份硬件测试方案和测试记录表",
            "准备一个设备调试或故障定位案例",
        ],
        "质量工程师": [
            "整理一份质量评审清单和改进闭环表",
            "补一份从问题发现到整改验证的完整案例",
        ],
        "产品助理": [
            "做一套 PRD、原型图和需求优先级说明",
            "补一份用户访谈或问卷分析摘要",
        ],
        "售前工程师": [
            "做一份面向客户的技术解决方案 PPT 和演示材料",
            "整理一个客户需求调研报告和对应的方案建议书",
        ],
        "项目专员": [
            "做一份完整的项目计划表（含里程碑、风险和资源分配）",
            "整理一份跨部门协调会议纪要和行动项跟踪表",
        ],
        "项目经理": [
            "完成一个包含需求分析、进度管理和风险控制的完整项目复盘报告",
            "准备一份用于答辩或交付的项目总结 PPT，突出成果和经验沉淀",
        ],
        "运营专员": [
            "策划并模拟执行一次用户活动，输出活动方案、执行记录和数据复盘",
            "做一份基于真实数据的用户行为分析报告，给出运营建议",
        ],
    }
    return role_map.get(
        role_title,
        ["补一个和目标岗位直接相关的小项目", "准备项目说明、截图和复盘文档"],
    )


def _build_learning_sprints(
    student: StudentProfile,
    primary_match: dict[str, Any],
    gap_keywords: list[str],
) -> list[dict[str, str]]:
    role_title = str(primary_match["role_title"])
    focus_gap = student.agent_answers.get("improvement_focus")
    short_goal = student.agent_answers.get("thirty_day_goal")

    prioritized_gaps = []
    if focus_gap:
        prioritized_gaps.append(focus_gap)
    prioritized_gaps.extend(keyword for keyword in gap_keywords if keyword not in prioritized_gaps)
    prioritized_gaps = prioritized_gaps[:3]

    sprints: list[dict[str, str]] = []
    for keyword in prioritized_gaps:
        sprints.append(
            {
                "title": f"补齐 {keyword} 能力证据",
                "type": "技能补强",
                "reason": f"{keyword} 是 {role_title} 的关键差距之一，补齐后能直接改善匹配解释。",
                "deliverable": f"完成一个包含 {keyword} 的小案例，并沉淀 README、截图或演示视频。",
            }
        )

    sprints.append(
        {
            "title": "把推荐补强项目做成可展示作品",
            "type": "项目举证",
            "reason": "获奖风格的作品不仅给建议，还要把建议转成可展示的成果物。",
            "deliverable": "完成 1 个与目标岗位强相关的项目，并准备 3 分钟口头讲解稿。",
        }
    )
    sprints.append(
        {
            "title": "完成一次复测并生成成长对比",
            "type": "闭环复盘",
            "reason": "让系统形成“诊断-训练-复测-成长曲线”的闭环，而不是一次性推荐。",
            "deliverable": short_goal or "补充智能体追问后再次分析，对比前后得分变化与短板收敛情况。",
        }
    )
    return sprints[:4]


def _build_next_review_targets(
    student: StudentProfile,
    primary_match: dict[str, Any],
    gap_keywords: list[str],
) -> list[str]:
    current_score = int(primary_match["score"])
    if current_score >= 92:
        score_target = f"下次复测时，保持 {primary_match['role_title']} 匹配分稳定在 {current_score} 分以上，并验证解释链是否仍然完整。"
    else:
        score_target = f"下次复测时，将 {primary_match['role_title']} 匹配分从 {current_score} 分提升到 {min(current_score + 8, 92)} 分以上。"
    targets = [score_target]
    if gap_keywords:
        targets.append("至少补齐 2 项核心短板：" + "、".join(gap_keywords[:2]))
    if student.missing_sections:
        targets.append("补全简历缺失项：" + "、".join(student.missing_sections[:2]))
    targets.append("新增 1 个可讲清业务背景、技术方案和结果指标的项目案例。")
    return targets


def _build_growth_comparison(
    student: StudentProfile,
    primary_match: dict[str, Any],
    previous_analysis: dict[str, Any] | None,
) -> dict[str, Any]:
    if not previous_analysis:
        return {
            "has_baseline": False,
            "summary": "当前还没有可对比的上一轮分析。完成一次补充问答并再次生成后，这里会自动展示成长轨迹。",
            "progress_items": [
                "建议先回答左侧智能体追问，再做一次复测。",
                "第二次分析会自动对比画像完整度、竞争力和主岗位匹配分的变化。",
            ],
        }

    previous_student = previous_analysis.get("student_profile", {})
    previous_plan = previous_analysis.get("career_plan", {})
    previous_score = int(previous_plan.get("primary_score") or 0)
    previous_role = previous_plan.get("primary_role") or "未生成"
    score_delta = int(primary_match["score"]) - previous_score
    completeness_delta = student.profile_completeness - int(previous_student.get("profile_completeness") or 0)
    competitiveness_delta = student.competitiveness_score - int(previous_student.get("competitiveness_score") or 0)

    if score_delta > 0:
        trend = "上升"
    elif score_delta < 0:
        trend = "回落"
    else:
        trend = "持平"

    progress_items = [
        f"主推荐岗位：{previous_role} -> {primary_match['role_title']}",
        f"匹配分变化：{previous_score} -> {primary_match['score']}（{score_delta:+d}）",
        f"画像完整度变化：{int(previous_student.get('profile_completeness') or 0)} -> {student.profile_completeness}（{completeness_delta:+d}）",
        f"就业竞争力变化：{int(previous_student.get('competitiveness_score') or 0)} -> {student.competitiveness_score}（{competitiveness_delta:+d}）",
    ]

    return {
        "has_baseline": True,
        "previous_analysis_id": previous_analysis.get("id"),
        "summary": f"与上一轮相比，当前结果整体{trend}。这能向评委证明系统不是一次性推荐，而是支持持续成长的职业规划闭环。",
        "progress_items": progress_items,
        "score_delta": score_delta,
        "completeness_delta": completeness_delta,
        "competitiveness_delta": competitiveness_delta,
    }


def _build_stakeholder_views(
    student: StudentProfile,
    primary_match: dict[str, Any],
    backups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    backup_titles = [match["role_title"] for match in backups]
    counselor_focus = "先补项目经历和目标岗位" if student.missing_sections else "优先补齐核心技能和面试举证"
    follow_up_level = "重点跟踪" if primary_match["score"] < 70 or student.profile_completeness < 75 else "常规跟踪"
    return [
        {
            "role": "学生端",
            "headline": f"当前最建议优先冲刺 {primary_match['role_title']}。",
            "items": [
                "先做主岗位，再把 " + "、".join(backup_titles or ["相近岗位"]) + " 作为备选方向。",
                "优先把共享技能转成可讲清楚的项目证据，避免只有关键词没有成果物。",
            ],
        },
        {
            "role": "辅导员端",
            "headline": f"这位学生当前属于 {follow_up_level} 类对象。",
            "items": [
                counselor_focus,
                "建议用同一份报告跟踪 30 天、90 天和 180 天行动执行情况。",
            ],
        },
        {
            "role": "就业中心端",
            "headline": "可纳入‘一生一策’的个性化就业辅导清单。",
            "items": [
                f"主推荐岗位为 {primary_match['role_title']}，可对应推送相关企业招聘与训练营资源。",
                f"意向城市为 {student.city_preference or '待补充'}，可作为岗位推送和区域帮扶依据。",
            ],
        },
    ]


def _build_evaluation_metrics(
    student: StudentProfile,
    primary_match: dict[str, Any],
    parser_metadata: dict[str, Any] | None,
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    shared_count = len(primary_match.get("shared_skills", []))
    required_count = max(1, len(primary_match.get("core_skills", [])))
    retrieved_count = len(evidence_bundle.get("items", []))
    evidence_hit_rate = int(evidence_bundle.get("evidence_hit_rate", 0))
    evidence_coverage = min(100, int(shared_count / required_count * 100) + min(retrieved_count * 6, 18))
    explanation_coverage = 100
    if not primary_match.get("gaps"):
        explanation_coverage -= 10
    if not primary_match.get("suggestions"):
        explanation_coverage -= 20

    loop_completion = 65
    if student.agent_answers:
        loop_completion += 15
    if student.projects:
        loop_completion += 10
    if student.internships:
        loop_completion += 10
    if self_assessment.get("score", 0) > 0:
        loop_completion += 10
    loop_completion = min(loop_completion, 100)

    parser_score = 84
    if parser_metadata and parser_metadata.get("fallback_used"):
        parser_score -= 8
    if parser_metadata and parser_metadata.get("used_mode") == "llm":
        parser_score += 4
    parser_score = max(0, min(parser_score, 100))
    taxonomy_skills = normalize_skill_list(student.skills)
    taxonomy_score = min(100, 55 + len(taxonomy_skills) * 6)

    return [
        {
            "name": "匹配证据覆盖",
            "score": evidence_coverage,
            "detail": f"Top1 岗位命中了 {shared_count}/{required_count} 个核心技能证据，并自动检索到 {retrieved_count} 条官方证据片段。",
        },
        {
            "name": "证据命中率",
            "score": evidence_hit_rate,
            "detail": f"检索证据覆盖了 {len(evidence_bundle.get('hit_terms', []))}/{max(1, len(evidence_bundle.get('target_terms', [])))} 个目标术语。",
        },
        {
            "name": "解释完整度",
            "score": explanation_coverage,
            "detail": "已同时输出优势、差距、建议和主推荐岗位解释。",
        },
        {
            "name": "闭环完成度",
            "score": loop_completion,
            "detail": "已具备行动计划、训练冲刺、复测目标和成长对比入口。",
        },
        {
            "name": "服务就绪度",
            "score": parser_score,
            "detail": "综合考虑解析稳定性、历史留存、导出交付和现场兜底能力。",
        },
        {
            "name": "能力归一覆盖",
            "score": taxonomy_score,
            "detail": f"学生技能中有 {len(taxonomy_skills)}/{max(1, len(student.skills))} 项已归一到能力词表，便于匹配与复核。",
        },
        {
            "name": "岗位自测完成度",
            "score": int(self_assessment.get("score", 0)),
            "detail": self_assessment.get("summary", "尚未完成岗位自测。"),
        },
    ]


def _build_competency_dimensions(student: StudentProfile, primary_match: dict[str, Any]) -> list[dict[str, Any]]:
    breakdown = primary_match.get("breakdown", {})
    knowledge = int(breakdown.get("professional_skills", 0))
    literacy = int(breakdown.get("professional_literacy", 0))
    growth = int(breakdown.get("growth_potential", 0))
    basic = int(breakdown.get("basic_requirements", 0))

    self_management = min(100, 40 + len(student.awards) * 8 + len(student.certificates) * 10)
    teamwork = min(100, 35 + len(student.internships) * 18 + (10 if "团队协作" in " ".join(student.soft_skills) else 0))

    return [
        {"name": "知识技能", "weight": "25%", "score": knowledge, "note": "对应岗位核心技能、技术栈和工具链覆盖。"},
        {"name": "岗位胜任", "weight": "25%", "score": basic, "note": "对应学历、目标岗位对齐度与基础申请条件。"},
        {"name": "自我管理", "weight": "15%", "score": self_management, "note": "结合获奖、证书与稳定输出能力估计执行自驱水平。"},
        {"name": "团队协作", "weight": "15%", "score": max(literacy, teamwork), "note": "参考软技能、实习协同经历与表达型证据。"},
        {"name": "发展潜力", "weight": "20%", "score": growth, "note": "参考项目、实习、证书和可持续成长空间。"},
    ]


def _role_radar_axes() -> list[dict[str, Any]]:
    return [
        {"name": "综合适配", "max": 100, "detail": "主排序得分，反映当前岗位优先级。"},
        {"name": "核心技能", "max": 100, "detail": "岗位核心技能与工具链命中情况。"},
        {"name": "岗位胜任", "max": 100, "detail": "学历、证书、方向对齐和基础入场条件。"},
        {"name": "软技能协同", "max": 100, "detail": "沟通表达、协作和岗位软要求的匹配度。"},
        {"name": "证据举证", "max": 100, "detail": "项目/实习是否足以支撑真实面试追问。"},
        {"name": "成长潜力", "max": 100, "detail": "补强空间与持续成长的可迁移性。"},
    ]


def _role_evidence_readiness(student: StudentProfile, match: dict[str, Any]) -> int:
    shared_count = len(match.get("shared_skills", []))
    missing_count = len(match.get("missing_skills", []))
    project_bonus = min(len(student.projects) * 8, 16)
    internship_bonus = min(len(student.internships) * 10, 20)
    score = 36 + shared_count * 12 + project_bonus + internship_bonus - missing_count * 7
    return max(0, min(score, 100))


def _role_radar_values(student: StudentProfile, match: dict[str, Any]) -> list[int]:
    breakdown = match.get("breakdown", {})
    teamwork = min(100, 35 + len(student.internships) * 18 + (10 if "团队协作" in " ".join(student.soft_skills) else 0))
    literacy = int(breakdown.get("professional_literacy", 0))
    return [
        int(match.get("score", 0)),
        int(breakdown.get("professional_skills", 0)),
        int(breakdown.get("basic_requirements", 0)),
        max(literacy, teamwork),
        _role_evidence_readiness(student, match),
        int(breakdown.get("growth_potential", 0)),
    ]


def _build_role_comparison_summary(role_comparison_radar: dict[str, Any]) -> list[str]:
    roles = list(role_comparison_radar.get("roles", []))
    axes = list(role_comparison_radar.get("axes", []))
    if len(roles) <= 1 or not axes:
        return []

    primary = roles[0]
    primary_values = list(primary.get("values", []))
    summaries: list[str] = []
    for role in roles[1:]:
        role_values = list(role.get("values", []))
        if len(role_values) != len(primary_values):
            continue

        diffs = [role_values[index] - primary_values[index] for index in range(len(primary_values))]
        best_index = max(range(len(diffs)), key=lambda index: diffs[index])
        worst_index = min(range(len(diffs)), key=lambda index: diffs[index])

        best_axis = str(axes[best_index].get("name", "关键维度"))
        worst_axis = str(axes[worst_index].get("name", "关键维度"))
        best_diff = diffs[best_index]
        worst_diff = diffs[worst_index]

        if best_diff >= 0:
            best_text = f"在“{best_axis}”上不弱于主岗（{role_values[best_index]} vs {primary_values[best_index]}）"
        else:
            best_text = f"与主岗最接近的是“{best_axis}”（仅差 {abs(best_diff)} 分）"

        if worst_diff < 0:
            worst_text = f"差距最大的是“{worst_axis}”（落后 {abs(worst_diff)} 分）"
        else:
            worst_text = f"整体差距已较小，当前没有明显短板维度"

        summaries.append(
            f"{role.get('lane', '备选')} {role.get('role_title', '候选岗位')}：{best_text}；{worst_text}。"
        )
    return summaries


def _build_role_comparison_radar(
    student: StudentProfile,
    strategy_matches: list[dict[str, Any]],
) -> dict[str, Any]:
    if not strategy_matches:
        return {}

    axes = _role_radar_axes()
    lane_labels = ["主攻", "跨投", "保底"]
    roles: list[dict[str, Any]] = []
    for index, match in enumerate(strategy_matches[:3]):
        roles.append(
            {
                "role_title": str(match.get("role_title", "目标岗位")),
                "lane": lane_labels[index],
                "score": int(match.get("score", 0)),
                "values": _role_radar_values(student, match),
            }
        )

    radar = {"axes": axes, "roles": roles}
    radar["summary"] = _build_role_comparison_summary(radar)
    return radar


def _build_service_loop(
    student: StudentProfile,
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
) -> list[dict[str, str]]:
    current_stage = "职业诊断"
    if student.agent_answers:
        current_stage = "复测反馈"
    elif student.projects or student.internships:
        current_stage = "项目补强"

    return [
        {
            "stage": "职业诊断",
            "status": "已完成" if student.profile_completeness >= 70 else "进行中",
            "detail": f"基于官方 JD 和学生画像完成 {primary_match['role_title']} 初步定位。",
        },
        {
            "stage": "岗位自测",
            "status": "已完成" if self_assessment.get("score", 0) > 0 else "建议补充",
            "detail": "围绕主推荐岗位做知识点自测和岗位化问答，验证能力证据是否真实可讲。",
        },
        {
            "stage": "项目补强",
            "status": "进行中" if student.projects or student.internships else "待开始",
            "detail": "把差距项转成项目、证书、作品集和实习经历，形成可展示成果。",
        },
        {
            "stage": "复测反馈",
            "status": "已开启" if student.agent_answers else "待开启",
            "detail": "补充追问信息后再次分析，对比匹配分、完整度和竞争力变化。",
        },
    ]


def _resolve_gap_dimension(keyword: str, primary_match: dict[str, Any]) -> tuple[str, int]:
    lowered = str(keyword).lower()
    breakdown = primary_match.get("breakdown", {})
    if any(term in lowered for term in ["项目表达", "项目讲解", "项目复盘", "star", "项目案例"]):
        return "发展潜力", int(breakdown.get("growth_potential", 0))
    if any(term in lowered for term in ["岗位知识", "工具链", "岗位自测"]):
        return "知识技能", int(breakdown.get("professional_skills", 0))
    if any(term in lowered for term in ["沟通", "表达", "协作", "责任", "培训"]):
        return "团队协作", int(breakdown.get("professional_literacy", 0))
    if any(term in lowered for term in ["项目", "实习", "举证", "star"]):
        return "发展潜力", int(breakdown.get("growth_potential", 0))
    if any(term in lowered for term in ["证书", "学历", "意向", "简历", "完整", "目标岗位"]):
        return "岗位胜任", int(breakdown.get("basic_requirements", 0))
    return "知识技能", int(breakdown.get("professional_skills", 0))


def _append_gap_candidate(candidates: list[str], keyword: str) -> None:
    cleaned = normalize_skill_alias(keyword)
    if not cleaned:
        return
    if any(str(item).lower() == cleaned.lower() for item in candidates):
        return
    candidates.append(cleaned)


def _fallback_gap_candidates(
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> list[str]:
    candidates: list[str] = []
    weak_focuses = normalize_skill_list(self_assessment.get("weak_focuses", []))

    for keyword in list(primary_match.get("missing_skills", []))[:3]:
        _append_gap_candidate(candidates, str(keyword))

    for focus in weak_focuses[:2]:
        _append_gap_candidate(candidates, focus)

    for keyword in _extract_gap_keywords(list(primary_match.get("gaps", [])))[:4]:
        _append_gap_candidate(candidates, keyword)

    evidence_hit_rate = int(evidence_bundle.get("evidence_hit_rate", 0))
    if evidence_hit_rate < 65:
        _append_gap_candidate(candidates, "项目表达")

    if int(self_assessment.get("score", 0)) == 0:
        _append_gap_candidate(candidates, "岗位自测")

    breakdown = primary_match.get("breakdown", {})
    dimension_fallbacks = [
        ("growth_potential", "项目表达"),
        ("professional_skills", "岗位知识"),
        ("basic_requirements", "简历完整度"),
        ("professional_literacy", "沟通表达"),
    ]
    for _, fallback_keyword in sorted(
        dimension_fallbacks,
        key=lambda item: int(breakdown.get(item[0], 0)),
    ):
        if len(candidates) >= 4:
            break
        _append_gap_candidate(candidates, fallback_keyword)

    if not candidates:
        candidates.extend(["项目表达", "岗位知识"])
    return candidates[:4]


def _gap_item_copy(keyword: str, dimension: str) -> tuple[str, str, str]:
    lowered = str(keyword).lower()
    if any(term in lowered for term in ["项目", "举证", "star"]):
        return (
            f"{keyword} 目前更像“写在简历里”，还没有稳定沉淀成能讲清楚的项目证据，这会直接压低“{dimension}”维度。",
            f"围绕 {keyword} 补 1 个最小案例，并整理成 STAR 讲稿、项目截图和结果指标。",
            f"补充 {keyword} 的项目截图、流程图、成果数据或可复述的项目讲解稿。",
        )
    if any(term in lowered for term in ["沟通", "表达", "协作", "培训"]):
        return (
            f"{keyword} 还缺少可被面试官追问的真实场景，容易让“{dimension}”维度停留在泛化表述。",
            f"补 1 次汇报、培训或跨部门协作复盘，把职责、冲突和结果讲具体。",
            f"沉淀协作案例、沟通纪要、培训反馈或可量化结果描述。",
        )
    if any(term in lowered for term in ["证书", "英语", "四级", "六级", "软考", "计算机"]):
        return (
            f"{keyword} 属于岗位筛选时的基础门槛，缺口会先压低“{dimension}”维度，再影响简历通过率。",
            f"明确考试或补证时间表，并把已通过证书和备考进度同步写进简历。",
            f"补充证书编号、成绩单、考试计划或已报名记录。",
        )
    if "自测" in lowered:
        return (
            f"{keyword} 还没有完成，当前很难判断知识点是否真的能讲出来，这会压低“{dimension}”维度。",
            f"先完成一轮岗位自测，记录不会讲的点，再回填到项目讲稿和面试题板。",
            f"形成错题清单、知识点复盘和下一次复测分数对比。",
        )
    if any(term in lowered for term in ["知识", "工具链"]):
        return (
            f"{keyword} 仍偏弱时，面试容易停留在概念层，难以支撑“{dimension}”维度继续上升。",
            f"围绕 {keyword} 做 1 次岗位自测、1 个最小练习和 1 版简历改写。",
            f"补充练习记录、代码片段、工具使用截图或题目复盘说明。",
        )
    if any(term in lowered for term in ["简历", "完整", "目标岗位", "意向"]):
        return (
            f"{keyword} 还不够完整，会让系统和招聘方都难以准确判断你的岗位定位，从而拖累“{dimension}”维度。",
            f"补齐目标岗位、项目职责、实习职责和结果描述，再做一轮岗位化改写。",
            f"补充清晰的目标岗位、职责边界、成果数字和投递版本记录。",
        )
    return (
        f"{keyword} 主要压低“{dimension}”维度，补齐后更容易把匹配解释从‘会写简历’变成‘能举证’。",
        f"围绕 {keyword} 完成 1 个最小案例、1 次岗位自测和 1 版项目表达稿。",
        f"补充 {keyword} 的项目截图、代码片段、STAR 表达或上线记录。",
    )


def _build_gap_benefit_analysis(
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = _fallback_gap_candidates(primary_match, self_assessment, evidence_bundle)
    term_map = build_term_citation_map(evidence_bundle)
    weak_focuses = {str(item).lower() for item in normalize_skill_list(self_assessment.get("weak_focuses", []))}
    fallback_citations = [
        str(item.get("citation_id", "")).strip()
        for item in evidence_bundle.get("items", [])
        if str(item.get("citation_id", "")).strip()
    ]
    items: list[dict[str, Any]] = []
    for index, keyword in enumerate(candidates[:4], start=1):
        dimension, current_score = _resolve_gap_dimension(keyword, primary_match)
        expected_gain = min(16, 6 + index * 2 + (3 if str(keyword).lower() in weak_focuses else 0))
        projected_score = min(100, current_score + expected_gain)
        citation_ids = term_map.get(str(keyword).lower(), [])
        if not citation_ids:
            citation_ids = fallback_citations[:1]
        detail, action, expected_evidence = _gap_item_copy(str(keyword), dimension)
        items.append(
            {
                "gap": keyword,
                "dimension": dimension,
                "current_score": current_score,
                "expected_gain": expected_gain,
                "projected_score": projected_score,
                "citations": citation_ids[:2],
                "detail": detail,
                "action": action,
                "expected_evidence": expected_evidence,
            }
        )
    return items


def _build_plan_self_checks(
    student: StudentProfile,
    primary_match: dict[str, Any],
    parser_metadata: dict[str, Any] | None,
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
    resource_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_hit_rate = int(evidence_bundle.get("evidence_hit_rate", 0))
    target_role = student.agent_answers.get("target_role") or (student.target_roles[0] if student.target_roles else "")
    target_aligned = not target_role or target_role == primary_match["role_title"] or target_role in primary_match["role_title"]
    checks = [
        {
            "name": "证据对齐检查",
            "status": "通过" if evidence_hit_rate >= 70 else "关注",
            "score": evidence_hit_rate,
            "detail": f"当前证据命中率 {evidence_hit_rate}%，主推荐解释已绑定官方 JD / 模板片段。",
            "action": "若命中率偏低，优先补充岗位关键词、项目术语和城市/岗位意向。",
        },
        {
            "name": "目标一致性检查",
            "status": "通过" if target_aligned else "待补",
            "score": 92 if target_aligned else 64,
            "detail": f"当前主岗位为 {primary_match['role_title']}，学生目标偏好为 {target_role or '未补充'}。",
            "action": "若目标不一致，先用智能体追问收敛主岗位，再进行二次复测。",
        },
        {
            "name": "交付可执行性检查",
            "status": "通过" if len(resource_map) >= 3 else "关注",
            "score": min(100, 60 + len(resource_map) * 10),
            "detail": f"当前已生成 {len(resource_map)} 条资源映射与交付物建议，可直接转成训练任务。",
            "action": "确保每项建议都能落成项目、证书、自测记录或投递材料。",
        },
        {
            "name": "闭环完整性检查",
            "status": "通过" if len(self_assessment.get('items', [])) >= 3 and student.profile_completeness >= 70 else "关注",
            "score": min(100, 58 + len(self_assessment.get("items", [])) * 10 + student.profile_completeness // 4),
            "detail": "已同时检查追问、自测、补强、复测四个节点是否齐备。",
            "action": "至少完成一次岗位自测并回填追问，才能形成完整成长曲线。",
        },
        {
            "name": "稳定性兜底检查",
            "status": "通过" if not (parser_metadata or {}).get("fallback_used") else "关注",
            "score": 90 if not (parser_metadata or {}).get("fallback_used") else 76,
            "detail": f"当前解析模式：{(parser_metadata or {}).get('used_mode', 'unknown')}，支持现场自动回退。",
            "action": "若发生回退，建议老师优先抽检关键字段与主推荐岗位解释。",
        },
    ]
    return checks


def _build_similar_cases(student: StudentProfile, primary_match: dict[str, Any]) -> list[dict[str, Any]]:
    return find_similar_analyses(
        student_name=student.name,
        major=student.major,
        current_skills=student.skills,
        target_roles=student.target_roles,
        city_preference=student.city_preference,
        primary_role=str(primary_match.get("role_title", "")),
        limit=3,
    )


def _assessment_tasks_for_role(role_title: str) -> list[str]:
    role_map = {
        "Java开发工程师": [
            "完成 10 道 Java / Spring / MySQL 岗位核心题自测，并记录错误点。",
            "针对一个项目准备 STAR 法回答，重点说明性能优化、接口设计和部署过程。",
        ],
        "前端开发工程师": [
            "完成 10 道 HTML / CSS / JavaScript / Vue 或 React 题目自测。",
            "准备一个页面性能优化或组件设计的项目复盘讲稿。",
        ],
        "测试工程师": [
            "完成 8 道测试用例设计、接口测试和缺陷定位题自测。",
            "针对一个项目准备测试计划、缺陷闭环和自动化脚本说明。",
        ],
        "实施工程师": [
            "完成 8 道系统部署、排障、培训交付场景题自测。",
            "准备一份上线部署流程和问题处理清单口述版。",
        ],
        "售前工程师": [
            "完成 8 道客户需求调研、方案设计和商务沟通场景题自测。",
            "准备一份完整的解决方案 PPT 讲解稿，含需求分析、方案亮点和落地建议。",
        ],
        "项目专员": [
            "完成 8 道项目计划制定、风险跟踪和跨部门沟通场景题自测。",
            "准备一份项目计划表和会议纪要模板，并练习 3 分钟口头汇报。",
        ],
        "项目经理": [
            "完成 10 道项目立项、进度管理、风险控制和干系人沟通场景题自测。",
            "针对一个完整项目准备 STAR 法复盘讲稿，说清楚范围、计划、执行和结果。",
        ],
        "测试开发工程师": [
            "完成 10 道 Python / Pytest / Selenium / CI 流水线场景题自测。",
            "准备一个自动化测试框架搭建或 CI/CD 接入案例的讲解稿。",
        ],
        "运营专员": [
            "完成 8 道用户增长、活动策划、数据分析和内容运营场景题自测。",
            "准备一份活动方案或数据复盘报告，并练习向评委讲清楚运营目标和结果。",
        ],
    }
    return role_map.get(
        role_title,
        [
            f"围绕 {role_title} 做 8 到 10 道岗位核心题自测，记录不会的问题。",
            "准备一个项目或经历的 STAR 法讲解版本，用于下一轮复测。",
        ],
    )


def _self_assessment_questions_for_role(role_title: str) -> list[dict[str, str]]:
    role_map = {
        "Java开发工程师": [
            {"id": "java_core", "prompt": "你现在独立完成 Java + Spring Boot 接口开发的把握程度如何？", "focus": "后端开发"},
            {"id": "db_design", "prompt": "面对一个业务需求，你能否独立完成数据库设计与 SQL 编写？", "focus": "数据库"},
            {"id": "project_pitch", "prompt": "你能否在 3 分钟内讲清一个后端项目的业务背景、技术方案和结果？", "focus": "项目表达"},
        ],
        "前端开发工程师": [
            {"id": "frontend_core", "prompt": "你现在独立完成组件开发、状态管理和接口联调的把握程度如何？", "focus": "前端开发"},
            {"id": "performance", "prompt": "你能否说清一个页面性能优化或交互优化案例？", "focus": "性能优化"},
            {"id": "project_pitch", "prompt": "你能否在 3 分钟内讲清一个前端项目的设计思路和效果？", "focus": "项目表达"},
        ],
        "测试工程师": [
            {"id": "test_case", "prompt": "你现在独立完成测试用例设计和缺陷定位的把握程度如何？", "focus": "测试设计"},
            {"id": "automation", "prompt": "你能否使用至少一种自动化测试工具完成基础脚本编写？", "focus": "自动化测试"},
            {"id": "project_pitch", "prompt": "你能否清楚讲述一个测试闭环案例？", "focus": "项目表达"},
        ],
        "实施工程师": [
            {"id": "deployment", "prompt": "你现在独立完成系统部署、配置和基础排障的把握程度如何？", "focus": "部署实施"},
            {"id": "delivery", "prompt": "面对客户培训或交付场景，你的把握程度如何？", "focus": "交付表达"},
            {"id": "project_pitch", "prompt": "你能否讲清一个实施/交付案例中的问题与解决过程？", "focus": "项目表达"},
        ],
        "售前工程师": [
            {"id": "solution_design", "prompt": "你现在独立完成客户需求调研和技术方案设计的把握程度如何？", "focus": "方案设计"},
            {"id": "presentation", "prompt": "你能否在 10 分钟内用 PPT 向客户清晰介绍一套解决方案？", "focus": "演示表达"},
            {"id": "project_pitch", "prompt": "你能否讲清一个客户沟通或方案交付案例中的挑战与结果？", "focus": "项目表达"},
        ],
        "项目专员": [
            {"id": "plan_management", "prompt": "你现在独立制定项目计划表（含里程碑和风险）的把握程度如何？", "focus": "计划管理"},
            {"id": "coordination", "prompt": "你能否组织一次跨部门协调会议并输出行动项跟踪表？", "focus": "跨部门协调"},
            {"id": "project_pitch", "prompt": "你能否清楚描述一次你参与过的项目协调经历和最终成果？", "focus": "项目表达"},
        ],
        "项目经理": [
            {"id": "scope_management", "prompt": "你现在独立完成需求范围定义、WBS 拆解和进度基线制定的把握程度如何？", "focus": "范围管理"},
            {"id": "risk_control", "prompt": "你能否识别项目中的关键风险并给出应对措施？", "focus": "风险控制"},
            {"id": "project_pitch", "prompt": "你能否在 5 分钟内讲清一个完整项目的目标、执行过程和最终交付成果？", "focus": "项目表达"},
        ],
        "测试开发工程师": [
            {"id": "framework_design", "prompt": "你现在独立搭建 Python + Pytest 自动化测试框架的把握程度如何？", "focus": "框架搭建"},
            {"id": "ci_integration", "prompt": "你能否将自动化测试脚本接入 Jenkins 并实现定时触发？", "focus": "CI 集成"},
            {"id": "project_pitch", "prompt": "你能否讲清一个自动化测试项目的覆盖率、执行效率和发现的缺陷？", "focus": "项目表达"},
        ],
        "运营专员": [
            {"id": "campaign_planning", "prompt": "你现在独立策划一次用户活动（含目标、方案、节奏和预算）的把握程度如何？", "focus": "活动策划"},
            {"id": "data_analysis", "prompt": "你能否根据运营数据撰写一份用户行为分析报告并给出建议？", "focus": "数据分析"},
            {"id": "project_pitch", "prompt": "你能否清楚讲述一次运营活动的目标、执行过程和复盘结论？", "focus": "项目表达"},
        ],
    }
    return role_map.get(
        role_title,
        [
            {"id": "role_knowledge", "prompt": f"你现在对 {role_title} 核心知识点的把握程度如何？", "focus": "岗位知识"},
            {"id": "tool_chain", "prompt": f"你现在对 {role_title} 常用工具链的掌握程度如何？", "focus": "工具链"},
            {"id": "project_pitch", "prompt": "你能否清楚讲述一个与目标岗位相关的项目案例？", "focus": "项目表达"},
        ],
    )


# 🌟 核心修改：支持接收大模型动态生成的题目
def _build_self_assessment_summary(
    role_title: str,
    answers: dict[str, int] | None,
    dynamic_questions: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    # 优先使用大模型生成的针对性问题，如果没有则降级使用规则库兜底
    questions = dynamic_questions if dynamic_questions else _self_assessment_questions_for_role(role_title)
    
    answers = answers or {}
    items: list[dict[str, Any]] = []
    total_score = 0
    max_score = max(1, len(questions) * 2)
    answered_count = 0

    for question in questions:
        raw_score = answers.get(question["id"])
        score = int(raw_score) if raw_score is not None else None
        if score is not None:
            total_score += score
            answered_count += 1
        if score is None:
            level = "未作答"
        elif score >= 2:
            level = "熟练"
        elif score == 1:
            level = "基础"
        else:
            level = "待补强"
        items.append(
            {
                "id": question["id"],
                "prompt": question["prompt"],
                "focus": question["focus"],
                "score": score,
                "level": level,
            }
        )

    overall = int(total_score / max_score * 100) if answered_count else 0
    weak_focuses = [item["focus"] for item in items if item["score"] == 0]
    summary = "建议先完成岗位自测，验证推荐结果和能力证据。"
    if overall >= 75:
        summary = "当前自测表现较稳，适合把更多时间投入项目举证和投递准备。"
    elif overall >= 45:
        summary = "当前自测处于过渡区，建议围绕待补强维度做一轮集中训练。"

    return {
        "title": f"{role_title} 岗位自测",
        "score": overall,
        "items": items,
        "weak_focuses": weak_focuses,
        "summary": summary,
    }


def _build_resource_map(
    role_title: str,
    gap_keywords: list[str],
    self_assessment: dict[str, Any],
) -> list[dict[str, Any]]:
    resources = [
        {
            "category": "项目模板",
            "priority": "高",
            "title": f"{role_title} 代表性项目模板",
            "description": "优先做一个和主推荐岗位最贴近的项目，把技能点、业务场景和结果指标讲清楚。",
            "deliverable": "README、核心截图、项目讲解稿、部署说明。",
        },
        {
            "category": "简历与表达",
            "priority": "高",
            "title": "STAR 法项目表达模板",
            "description": "把项目经历改写成场景、任务、行动、结果四段式，便于复测和面试使用。",
            "deliverable": "1 分钟精简版 + 3 分钟完整版项目讲稿。",
        },
    ]

    for keyword in gap_keywords[:2]:
        resources.append(
            {
                "category": "技能补强",
                "priority": "高",
                "title": f"{keyword} 补强清单",
                "description": f"围绕 {keyword} 制定 7 天到 14 天的补强任务，把缺口转成可证明能力。",
                "deliverable": f"完成 {keyword} 笔记、自测结果和一个最小案例。",
            }
        )

    weak_focuses = self_assessment.get("weak_focuses", [])
    if weak_focuses:
        resources.append(
            {
                "category": "岗位自测",
                "priority": "中",
                "title": "薄弱环节专项自测",
                "description": "围绕岗位自测里分数最低的维度做一次专项复盘。",
                "deliverable": "记录错题、不会讲的点和下一次复测目标：" + "、".join(weak_focuses[:2]),
            }
        )

    resources.append(
        {
            "category": "证书与资源",
            "priority": "中",
            "title": "基础证书与投递资源包",
            "description": "如果当前证书或基础项偏弱，优先补齐能快速提升简历可信度的基础证明。",
            "deliverable": "明确是否补英语、计算机基础证书，并完成对应投递材料整理。",
        }
    )
    return resources


def _build_agent_questions(
    student: StudentProfile,
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
) -> list[dict[str, str]]:
    top_role = primary_match["role_title"]
    missing_skills = primary_match.get("missing_skills", [])
    weak_focuses = self_assessment.get("weak_focuses", [])
    questions: list[dict[str, str]] = []

    if "target_role" not in student.agent_answers:
        questions.append(
            {
                "id": "target_role",
                "question": "如果这周只能优先冲刺一个方向，你最想先拿下哪个岗位？",
                "placeholder": "例如：Java开发工程师",
                "suggested_answer": student.target_roles[0] if student.target_roles else top_role,
                "rationale": "目标岗位越明确，系统越能把推荐结果收敛成可执行方案。",
            }
        )

    if "preferred_city" not in student.agent_answers:
        questions.append(
            {
                "id": "preferred_city",
                "question": "你接下来更希望优先在哪个城市或区域找机会？",
                "placeholder": "例如：上海 / 深圳 / 杭州",
                "suggested_answer": student.city_preference or "杭州",
                "rationale": "城市偏好会影响就业中心推岗和老师的一生一策帮扶方案。",
            }
        )

    if "improvement_focus" not in student.agent_answers:
        questions.append(
            {
                "id": "improvement_focus",
                "question": "接下来 30 天，你最想先补哪类短板？",
                "placeholder": "例如：Spring Boot / 自动化测试 / 项目表达",
                "suggested_answer": weak_focuses[0] if weak_focuses else (missing_skills[0] if missing_skills else "项目表达"),
                "rationale": "系统会把这个答案直接转成训练闭环和复测目标。",
            }
        )

    if "project_focus" not in student.agent_answers:
        questions.append(
            {
                "id": "project_focus",
                "question": "你最想拿哪个项目或经历，作为主岗位的核心证明材料？",
                "placeholder": "例如：校园二手交易平台 / 接口自动化项目",
                "suggested_answer": student.projects[0] if student.projects else "主岗位相关项目",
                "rationale": "项目证据是拉高匹配可信度和面试说服力的关键。",
            }
        )

    if "thirty_day_goal" not in student.agent_answers:
        questions.append(
            {
                "id": "thirty_day_goal",
                "question": "你希望 30 天后拿到什么可见成果？",
                "placeholder": "例如：完整项目作品 / 一段实习 / 证书准备完成",
                "suggested_answer": "完整项目作品",
                "rationale": "短期目标会决定系统给出的行动节奏和交付件形式。",
            }
        )

    if "certificate_plan" not in student.agent_answers and student.missing_sections:
        questions.append(
            {
                "id": "certificate_plan",
                "question": "如果需要补一项基础证明，你更倾向先补证书、项目还是实习？",
                "placeholder": "例如：证书 / 项目 / 实习",
                "suggested_answer": "项目",
                "rationale": "这会影响资源映射和下一阶段的优先级安排。",
            }
        )

    return questions[:3]


def _build_innovation_highlights(student: StudentProfile) -> list[dict[str, str]]:
    return [
        {
            "title": "证据驱动生成",
            "tag": "Evidence-bound",
            "detail": "建议生成前先绑定官方 JD 与岗位模板证据，无法回看证据时会降级为规则化提示。",
        },
        {
            "title": "可解释匹配引擎",
            "tag": "Explainable Matching",
            "detail": "总分拆解为基础要求、专业技能、职业素养与发展潜力四个维度，并给出共享技能与差距项。",
        },
        {
            "title": "多阶段工作流编排",
            "tag": "Agentic Workflow",
            "detail": "系统把解析、匹配、规划、追问、自测、复测与学校看板串成可校验、可降级的任务链。",
        },
        {
            "title": "人机协同闭环",
            "tag": "Human-in-the-loop",
            "detail": "老师可抽检模板与建议结果，学生可补充偏好与证据，系统负责批量执行、留痕与复盘。",
        },
    ]


def _build_technical_keywords() -> list[str]:
    return [
        "Evidence-bound Generation",
        "Explainable Matching",
        "Competency Taxonomy",
        "Agentic Workflow",
        "Human-in-the-loop Review",
        "Sample Verification Center",
    ]


def _build_technical_modules() -> list[dict[str, str]]:
    return [
        {
            "name": "证据驱动生成",
            "tag": "Grounded Generation",
            "detail": "把官方 JD、岗位模板与学生画像作为知识底座，系统先分块检索证据，再以引用片段约束建议生成。",
        },
        {
            "name": "可解释匹配引擎",
            "tag": "Explainable Recommendation",
            "detail": "使用分维度评分和差距映射，而不是黑箱端到端推荐，便于评委追问时直接回看依据。",
        },
        {
            "name": "胜任力维度模型",
            "tag": "Competency Taxonomy",
            "detail": "用可维护的能力维度词表与别名归一机制统一描述岗位要求和学生能力，不宣称图学习训练。",
        },
        {
            "name": "多阶段工作流智能体",
            "tag": "Workflow Orchestration",
            "detail": "把解析、检索、重排、匹配、规划、追问、自测、复测和运营看板编排成可校验节点，任何一步置信不足都可以触发追问或规则降级。",
        },
        {
            "name": "人机协同治理",
            "tag": "Human-in-the-loop",
            "detail": "将老师抽检、样例验证和学生补证据纳入闭环，确保系统可控、可复盘、可持续优化。",
        },
    ]


def _load_role_template(role_title: str) -> dict[str, Any] | None:
    return next((item for item in load_role_templates() if item.get("canonical_title") == role_title), None)


def _service_segment(primary_score: int, profile_completeness: int) -> tuple[str, str]:
    if primary_score >= 80 and profile_completeness >= 80:
        return (
            "强匹配直推",
            "已经具备较强岗位贴合度，优先做定向投递、模拟面试和企业直连。",
        )
    if primary_score >= 65:
        return (
            "潜力转化",
            "具备转化空间，关键是把短板转成项目证据和可讲清的求职材料。",
        )
    return (
        "重点帮扶",
        "当前不适合盲投，建议先补齐画像、主项目和岗位自测，再进入投递阶段。",
    )


def _job_search_stage(
    student: StudentProfile,
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
) -> tuple[str, str]:
    if student.profile_completeness < 70:
        return "画像补全期", "先把学校、专业、目标岗位、项目和实习职责补齐，再做精准推荐。"
    if not student.projects and not student.internships:
        return "作品补强期", "当前最大短板不是投递量，而是缺少能支撑岗位胜任力的作品与经历。"
    if int(self_assessment.get("score", 0)) < 50 or len(primary_match.get("missing_skills", [])) >= 3:
        return "能力冲刺期", "先围绕 1 到 2 个关键技能做专项补强，再准备主项目讲稿。"
    if int(primary_match.get("score", 0)) >= 80:
        return "集中投递期", "画像和能力证据已较稳定，适合开始集中投递和模拟面试。"
    return "定向打磨期", "当前适合一边补强，一边用目标 JD 校准简历与项目表达。"


def _join_or_default(items: list[str] | None, default: str, limit: int = 3) -> str:
    cleaned = [str(item).strip() for item in items or [] if str(item).strip()]
    if not cleaned:
        return default
    return "、".join(cleaned[:limit])


def _build_job_search_snapshot(
    student: StudentProfile,
    primary_match: dict[str, Any],
    strategy_matches: list[dict[str, Any]],
    role_template: dict[str, Any] | None,
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    primary_score = int(primary_match.get("score", 0))
    segment_label, segment_detail = _service_segment(primary_score, student.profile_completeness)
    stage_label, stage_detail = _job_search_stage(student, primary_match, self_assessment)
    preferred_cities = student.city_preference or _join_or_default(
        list(role_template.get("typical_cities", [])) if role_template else [],
        "待补充目标城市",
        limit=2,
    )
    preferred_industries = _join_or_default(
        student.target_industries or (list(role_template.get("typical_industries", [])) if role_template else []),
        "待补充目标行业",
        limit=3,
    )
    salary_hint = _join_or_default(
        list(role_template.get("sample_salary_ranges", [])) if role_template else [],
        "官方样本未给出稳定薪资带",
        limit=2,
    )
    recommendation_matrix = []
    lane_labels = ["主攻", "跨投", "保底"]
    for index, match in enumerate(strategy_matches[:3]):
        recommendation_matrix.append(f"{lane_labels[index]} {str(match.get('role_title', '未生成岗位'))}")
    evidence_hit_rate = int(evidence_bundle.get("evidence_hit_rate", 0))
    readiness_score = round((student.profile_completeness + primary_score + evidence_hit_rate) / 3)

    return [
        {
            "label": "当前阶段",
            "value": stage_label,
            "detail": stage_detail,
        },
        {
            "label": "服务分层",
            "value": segment_label,
            "detail": segment_detail,
        },
        {
            "label": "主攻岗位",
            "value": str(primary_match.get("role_title", "未生成")),
            "detail": "主推荐岗位来自官方 JD 聚类模板，可直接追溯到原始样本。",
        },
        {
            "label": "优先城市",
            "value": preferred_cities,
            "detail": "优先围绕这些城市做岗位检索、简历定制和宣讲会关注。",
        },
        {
            "label": "目标行业",
            "value": preferred_industries,
            "detail": "优先关注岗位聚类中高频出现的行业，减少无效跨投。",
        },
        {
            "label": "薪资参考",
            "value": salary_hint,
            "detail": "基于官方样本中的代表性薪资区间，用于建立合理预期。",
        },
        {
            "label": "推荐编排",
            "value": " / ".join(recommendation_matrix) or "待生成",
            "detail": "主攻位看当前最佳匹配，跨投位优先保留学生第二意向或主岗迁移路径，保底位兼顾稳定性与面邀率。",
        },
        {
            "label": "求职就绪度",
            "value": f"{readiness_score} 分",
            "detail": f"综合画像完整度 {student.profile_completeness}、主岗分 {primary_score}、证据命中率 {evidence_hit_rate} 计算。",
        },
    ]


def _build_application_strategy(
    student: StudentProfile,
    primary_match: dict[str, Any],
    strategy_matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lane_labels = ["主攻", "跨投", "保底"]
    candidates = strategy_matches[:3] if strategy_matches else [primary_match]
    strategies: list[dict[str, Any]] = []

    for index, match in enumerate(candidates):
        role_title = str(match.get("role_title", "未生成岗位"))
        role_template = _load_role_template(role_title)
        city_focus = student.city_preference or _join_or_default(
            list(role_template.get("typical_cities", [])) if role_template else [],
            "优先锁定 1 到 2 个目标城市",
            limit=2,
        )
        industry_focus = _join_or_default(
            student.target_industries or (list(role_template.get("typical_industries", [])) if role_template else []),
            "软件/互联网/企业服务",
            limit=2,
        )
        salary_hint = _join_or_default(
            list(role_template.get("sample_salary_ranges", [])) if role_template else [],
            "样本薪资需结合现场岗位补充",
            limit=1,
        )
        keywords = [
            role_title,
            *[str(item) for item in match.get("shared_skills", [])[:2]],
            *[str(item) for item in match.get("missing_skills", [])[:1]],
        ]
        deliverables = []
        deliverables.append("定制化简历 3 版")
        deliverables.append("主项目讲稿 1 套")
        if match.get("missing_skills"):
            deliverables.append(f"补齐 {str(match['missing_skills'][0])} 的最小案例")
        else:
            deliverables.append("补一轮面试题复盘")

        strategies.append(
            {
                "lane": lane_labels[index],
                "role_title": role_title,
                "fit_score": int(match.get("score", 0)),
                "positioning": _application_positioning(student, primary_match, match, lane_labels[index]),
                "selection_reason": _application_selection_reason(student, primary_match, match),
                "risk_note": _application_risk_note(primary_match, match, lane_labels[index]),
                "city_focus": city_focus,
                "industry_focus": industry_focus,
                "salary_hint": salary_hint,
                "keywords": [item for item in keywords if item],
                "rationale": (
                    f"该方向已命中 {_join_or_default(list(match.get('shared_skills', [])), '基础技能', limit=2)}，"
                    f"同时需要继续补齐 {_join_or_default(list(match.get('missing_skills', [])), '项目表达', limit=1)}。"
                ),
                "action": (
                    "先用 3 份真实 JD 校准简历关键词，再围绕主项目准备一版可直接投递与面试的材料。"
                    if index == 0
                    else "保留相近技能词和项目证据，避免完全跨方向造成解释断层。"
                ),
                "deliverables": deliverables,
            }
        )

    return strategies


def _build_resume_surgery(
    student: StudentProfile,
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
) -> list[dict[str, Any]]:
    section_map = {
        "目标岗位": {
            "section": "求职意向",
            "issue": "简历没有明确主攻岗位，容易让投递和老师指导都失焦。",
            "action": f"在简历抬头或自我评价区明确写出“目标岗位：{primary_match['role_title']} / 备选岗位：{'、'.join(student.target_roles[:2]) or '相近岗位'}”。",
            "deliverable": "1 行岗位意向 + 1 行城市偏好。",
        },
        "意向城市": {
            "section": "城市偏好",
            "issue": "缺少城市偏好会降低推岗与投递筛选效率。",
            "action": "补充 1 到 2 个优先城市，并在投递时做城市版本区分。",
            "deliverable": "在简历或求职表单中写清优先城市和可接受范围。",
        },
        "项目经历": {
            "section": "项目经历",
            "issue": "缺少项目会让岗位匹配只能停留在关键词层面，无法真正举证。",
            "action": f"补 1 个与 {primary_match['role_title']} 强相关的项目，写清场景、职责、方案和结果。",
            "deliverable": "每个项目至少 3 个 STAR 要点 + 1 个量化结果。",
        },
        "实习经历": {
            "section": "实习/实训",
            "issue": "没有实习或实训经历时，岗位适应性证据偏弱。",
            "action": "用校内项目、竞赛实训或模拟交付案例替代真实实习经历的展示空白。",
            "deliverable": "补一段“角色-任务-结果”式经历描述。",
        },
        "证书信息": {
            "section": "基础证明",
            "issue": "基础证书或能力证明偏弱，简历可信度受影响。",
            "action": "补充英语、计算机或岗位相关基础证书，并写明时间节点。",
            "deliverable": "在简历证书栏增加已获证书或备考计划。",
        },
    }

    items: list[dict[str, Any]] = []
    for label in student.missing_sections:
        if label in section_map:
            items.append(section_map[label])

    for gap in list(primary_match.get("missing_skills", []))[:2]:
        items.append(
            {
                "section": f"{gap} 证据",
                "issue": f"{gap} 当前主要停留在缺口状态，简历里缺少能说服面试官的真实证据。",
                "action": f"把 {gap} 写进项目职责、技术栈、解决问题过程和最终结果，避免只堆在技能列表。",
                "deliverable": f"补 1 个 {gap} 最小案例，至少准备截图、代码/流程说明和结果指标各 1 项。",
            }
        )

    weak_focuses = list(self_assessment.get("weak_focuses", []))
    if weak_focuses:
        items.append(
            {
                "section": "面试薄弱项",
                "issue": f"岗位自测显示 {_join_or_default(weak_focuses, '核心技能', limit=2)} 仍偏弱，面试容易被追问击穿。",
                "action": "围绕最低分维度补一页复盘笔记，并准备一个能证明进步的训练案例。",
                "deliverable": "错题清单 1 份 + 二次复测目标 1 份。",
            }
        )

    if not items:
        items.append(
            {
                "section": "项目表达",
                "issue": "当前主要风险不在于信息缺失，而在于表达不够岗位化。",
                "action": "把最强项目改写成 STAR 结构，并突出业务结果与岗位能力对应关系。",
                "deliverable": "1 分钟版项目讲稿 + 3 分钟版项目讲稿。",
            }
        )

    return items[:5]


def _build_interview_focus(
    student: StudentProfile,
    primary_match: dict[str, Any],
    self_assessment: dict[str, Any],
) -> list[dict[str, Any]]:
    role_title = str(primary_match.get("role_title", "目标岗位"))
    project_focus = student.agent_answers.get("project_focus") or (student.projects[0] if student.projects else "最相关项目")
    shared_skills = list(primary_match.get("shared_skills", []))
    missing_skills = list(primary_match.get("missing_skills", []))
    weak_focuses = list(self_assessment.get("weak_focuses", []))

    items = [
        {
            "theme": "项目总述",
            "question": f"请用 3 分钟讲清 {project_focus} 为什么能证明你适合 {role_title}。",
            "signal": "能完整说出业务场景、个人职责、关键动作和量化结果。",
            "prep": "准备 1 分钟版与 3 分钟版两套话术，避免只讲技术名词。",
        }
    ]

    for skill in shared_skills[:2]:
        items.append(
            {
                "theme": f"{skill} 实战追问",
                "question": f"如果面试官追问你在项目里如何使用 {skill}，你能否给出具体场景和结果？",
                "signal": "回答里要出现真实场景、具体动作和结果指标，而不是泛泛描述。",
                "prep": f"准备 1 个围绕 {skill} 的项目片段，最好附带截图、代码或测试结果。",
            }
        )

    for skill in missing_skills[:2]:
        items.append(
            {
                "theme": f"{skill} 补强计划",
                "question": f"如果岗位要求 {skill}，你准备如何在 2 周内把它补到可面试水平？",
                "signal": "不要空谈学习态度，要给出最小案例、学习路径和复测安排。",
                "prep": f"准备 {skill} 的 7 到 14 天补强路线，以及 1 个可展示的最小练习案例。",
            }
        )

    if weak_focuses:
        focus = weak_focuses[0]
        items.append(
            {
                "theme": "低分维度复盘",
                "question": f"岗位自测里 {focus} 得分偏低，你下一轮怎么补，怎么证明自己真的补上了？",
                "signal": "面试官更看重补短板的方法论和证据，而不是一句‘我会努力学习’。",
                "prep": "准备错题复盘、训练动作和二次复测目标三件套。",
            }
        )

    return items[:5]


def _build_role_action_plan_bundle(
    student: StudentProfile,
    role_match: dict[str, Any],
    lane_label: str,
) -> dict[str, list[str]]:
    role_title = str(role_match.get("role_title", "目标岗位"))
    focus_gap = student.agent_answers.get("improvement_focus")
    gap_keywords: list[str] = []
    if focus_gap:
        gap_keywords.append(focus_gap)
    for keyword in list(role_match.get("missing_skills", [])):
        if keyword not in gap_keywords:
            gap_keywords.append(keyword)
    if not gap_keywords:
        gap_keywords = ["项目表达", "岗位举证"]

    short_goal = student.agent_answers.get("thirty_day_goal") or f"完成 1 版可用于 {role_title} 投递的简历与项目讲稿"
    lane_opening = {
        "主攻": f"把简历求职意向、自我评价和项目标题统一改成 {role_title} 叙事，直接进入集中投递准备。",
        "跨投": f"保留当前能力底座，但把项目职责、结果指标和关键词改写成更贴近 {role_title} 的版本。",
        "保底": f"优先用最小改写成本把现有经历映射到 {role_title}，先提升面邀稳定性，再决定是否深切换。",
    }.get(lane_label, f"围绕 {role_title} 重排简历和项目叙事，建立独立的投递版本。")

    action_plan_30 = [
        lane_opening,
        "优先补齐该岗位的核心差距：" + "、".join(gap_keywords[:2]),
        f"30 天内至少完成 1 个能证明 {role_title} 胜任力的最小案例或讲稿：{short_goal}",
    ]
    if student.missing_sections:
        action_plan_30.append("同步补全简历缺失项：" + "、".join(student.missing_sections[:2]))

    action_plan_90 = [
        f"完成 1 个与 {role_title} 直接相关的项目或专题，并沉淀 README、截图或演示材料。",
        "用 3 份真实 JD 校准关键词、项目要点和投递话术，形成该岗位专属版本。",
        "准备 8 到 10 道该岗位高频面试题，并完成 1 次岗位化模拟面试。",
    ]

    action_plan_180 = [
        f"争取 1 段与 {role_title} 相关的实习、实训或真实项目经历，补足长期证据链。",
        f"持续维护 {role_title} 的项目案例库、面试题库和投递复盘记录。",
        "把最有效的简历版本、项目讲稿和面试答案固化成可复用求职材料。",
    ]

    return {
        "action_plan_30_days": action_plan_30[:4],
        "action_plan_90_days": action_plan_90[:3],
        "action_plan_180_days": action_plan_180[:3],
        "gap_keywords": gap_keywords[:3],
    }


def _build_role_plan_panel_bundle(
    student: StudentProfile,
    role_match: dict[str, Any],
    self_assessment: dict[str, Any],
    evidence_bundle: dict[str, Any],
    *,
    parser_metadata: dict[str, Any] | None = None,
    gap_keywords: list[str] | None = None,
) -> dict[str, Any]:
    role_title = str(role_match.get("role_title", "目标岗位"))
    resolved_gap_keywords = [str(item).strip() for item in gap_keywords or [] if str(item).strip()]
    if not resolved_gap_keywords:
        focus_gap = student.agent_answers.get("improvement_focus")
        if focus_gap:
            resolved_gap_keywords.append(focus_gap)
        for keyword in list(role_match.get("missing_skills", [])):
            if keyword not in resolved_gap_keywords:
                resolved_gap_keywords.append(keyword)
    if not resolved_gap_keywords:
        resolved_gap_keywords = ["项目表达", "岗位举证"]

    resource_map = _build_resource_map(role_title, resolved_gap_keywords, self_assessment)
    return {
        "recommended_projects": _project_suggestions_for_role(role_title),
        "learning_sprints": _build_learning_sprints(student, role_match, resolved_gap_keywords),
        "gap_benefit_analysis": _build_gap_benefit_analysis(role_match, self_assessment, evidence_bundle),
        "plan_self_checks": _build_plan_self_checks(
            student,
            role_match,
            parser_metadata,
            self_assessment,
            evidence_bundle,
            resource_map,
        ),
        "resource_map": resource_map,
        "growth_path": list(role_match.get("growth_path", [])),
        "transition_paths": list(role_match.get("transition_paths", [])),
        "assessment_tasks": _assessment_tasks_for_role(role_title),
    }


def _build_role_switch_simulations(
    student: StudentProfile,
    strategy_matches: list[dict[str, Any]],
    application_strategy: list[dict[str, Any]],
    self_assessment: dict[str, Any],
    parser_metadata: dict[str, Any] | None = None,
    primary_role_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    strategy_lookup = {str(item.get("role_title", "")): item for item in application_strategy}
    simulations: list[dict[str, Any]] = []
    primary_role_title = str(strategy_matches[0].get("role_title", "")) if strategy_matches else ""

    for match in strategy_matches[:3]:
        role_title = str(match.get("role_title", "目标岗位"))
        strategy_item = strategy_lookup.get(role_title, {})
        lane_label = str(strategy_item.get("lane", _comparison_lane_label(strategy_matches, role_title)))
        plan_bundle = _build_role_action_plan_bundle(student, match, lane_label)
        evidence_bundle = build_grounded_evidence_bundle(student, match)
        simulation_assessment = dict(self_assessment or {})
        if match.get("missing_skills"):
            simulation_assessment["weak_focuses"] = list(match.get("missing_skills", []))[:2]
        panel_bundle = _build_role_plan_panel_bundle(
            student,
            match,
            simulation_assessment,
            evidence_bundle,
            parser_metadata=parser_metadata,
            gap_keywords=list(plan_bundle.get("gap_keywords", [])),
        )
        if role_title == primary_role_title and primary_role_bundle:
            panel_bundle.update(primary_role_bundle)

        simulations.append(
            {
                "role_title": role_title,
                "lane": lane_label,
                "fit_score": int(match.get("score", 0)),
                "summary": (
                    f"当前切到 {lane_label} 岗位 {role_title} 后，方案会优先围绕 "
                    f"{_join_or_default(plan_bundle.get('gap_keywords', []), '项目表达', limit=2)} 做岗位化重写和补强。"
                ),
                "positioning": str(strategy_item.get("positioning", "")),
                "selection_reason": str(strategy_item.get("selection_reason", "")),
                "risk_note": str(strategy_item.get("risk_note", "")),
                "action_plan_30_days": list(plan_bundle.get("action_plan_30_days", [])),
                "action_plan_90_days": list(plan_bundle.get("action_plan_90_days", [])),
                "action_plan_180_days": list(plan_bundle.get("action_plan_180_days", [])),
                "evidence_bundle": evidence_bundle,
                "resume_surgery": _build_resume_surgery(student, match, simulation_assessment),
                "interview_focus": _build_interview_focus(student, match, simulation_assessment),
                "next_review_targets": _build_next_review_targets(student, match, list(plan_bundle.get("gap_keywords", []))),
                "recommended_projects": list(panel_bundle.get("recommended_projects", [])),
                "learning_sprints": list(panel_bundle.get("learning_sprints", [])),
                "gap_benefit_analysis": list(panel_bundle.get("gap_benefit_analysis", [])),
                "plan_self_checks": list(panel_bundle.get("plan_self_checks", [])),
                "resource_map": list(panel_bundle.get("resource_map", [])),
                "growth_path": list(panel_bundle.get("growth_path", [])),
                "transition_paths": list(panel_bundle.get("transition_paths", [])),
                "assessment_tasks": list(panel_bundle.get("assessment_tasks", [])),
            }
        )

    return simulations


def build_career_plan(
    student: StudentProfile,
    ranked_matches: list[dict[str, object]],
    *,
    previous_analysis: dict[str, Any] | None = None,
    parser_metadata: dict[str, Any] | None = None,
    self_assessment_answers: dict[str, int] | None = None,
) -> CareerPlan:
    strategy_matches = _select_application_matches(student, ranked_matches)
    primary = strategy_matches[0] if strategy_matches else ranked_matches[0]
    backups = strategy_matches[1:3]
    focus_gap = student.agent_answers.get("improvement_focus")
    top_gap_keywords = list(primary.get("missing_skills") or [])
    if focus_gap and focus_gap not in top_gap_keywords:
        top_gap_keywords.insert(0, focus_gap)
    if not top_gap_keywords:
        top_gap_keywords = ["项目表达", "岗位举证"]
    role_title = primary["role_title"]
    
    # 🌟 核心接入点：触发大模型动态生成专属项目与考核计划
    dynamic_guidance = _generate_dynamic_role_guidance(role_title, top_gap_keywords)

    # 🌟 P5：生成 AI 匹配评审意见（有 LLM key 时调用，失败则静默跳过）
    ai_match_commentary = _generate_ai_match_commentary(
        role_title=role_title,
        score=int(primary["score"]),
        strengths=list(primary.get("strengths", [])),
        missing_skills=list(primary.get("missing_skills", [])),
    )

    focus_role = student.agent_answers.get("target_role") or role_title
    overview = (
        f"{student.name} 当前最适合优先冲刺 {role_title}，"
        f"同时可把 {'、'.join(match['role_title'] for match in backups) or '相近岗位'} 作为备选方向。"
    )
    if focus_role != role_title:
        overview += f" 结合智能体补充问答，系统会继续用 {focus_role} 作为下一轮对齐目标。"

    risks = list(primary["gaps"])

    # 🌟 核心替换：传入大模型生成的动态自测题
    self_assessment = _build_self_assessment_summary(
        role_title, 
        self_assessment_answers,
        dynamic_questions=dynamic_guidance.get("self_assessment_questions")
    )
    
    evidence_bundle = build_grounded_evidence_bundle(student, primary)
    role_template = _load_role_template(role_title)
    primary_panel_bundle = _build_role_plan_panel_bundle(
        student,
        primary,
        self_assessment,
        evidence_bundle,
        parser_metadata=parser_metadata,
        gap_keywords=top_gap_keywords,
    )
    primary_panel_bundle["recommended_projects"] = dynamic_guidance.get("recommended_projects") or list(
        primary_panel_bundle.get("recommended_projects", [])
    )
    primary_panel_bundle["assessment_tasks"] = dynamic_guidance.get("assessment_tasks") or list(
        primary_panel_bundle.get("assessment_tasks", [])
    )
    resource_map = list(primary_panel_bundle.get("resource_map", []))
    application_strategy = _build_application_strategy(student, primary, strategy_matches)
    recommendation_comparisons = _build_recommendation_comparisons(student, primary, ranked_matches, strategy_matches)
    role_switch_simulations = _build_role_switch_simulations(
        student,
        strategy_matches,
        application_strategy,
        self_assessment,
        parser_metadata,
        primary_panel_bundle,
    )
    role_comparison_radar = _build_role_comparison_radar(student, strategy_matches)
    job_search_snapshot = _build_job_search_snapshot(student, primary, strategy_matches, role_template, self_assessment, evidence_bundle)
    resume_surgery = _build_resume_surgery(student, primary, self_assessment)
    interview_focus = _build_interview_focus(student, primary, self_assessment)
    primary_plan_bundle = _build_role_action_plan_bundle(student, primary, "主攻")
    overview = annotate_text_with_citations(
        overview,
        evidence_bundle,
        preferred_terms=[role_title, *top_gap_keywords, *(primary.get("shared_skills") or [])],
        max_annotations=3,
    )

    return CareerPlan(
        primary_role=role_title,
        backup_roles=[match["role_title"] for match in backups],
        primary_score=primary["score"],
        overview=overview,
        job_search_snapshot=job_search_snapshot,
        strengths=list(primary["strengths"]),
        risks=risks,
        primary_growth_path=list(primary["growth_path"]),
        transition_paths=list(primary["transition_paths"]),
        action_plan_30_days=list(primary_plan_bundle.get("action_plan_30_days", [])),
        action_plan_90_days=list(primary_plan_bundle.get("action_plan_90_days", [])),
        action_plan_180_days=list(primary_plan_bundle.get("action_plan_180_days", [])),
        application_strategy=application_strategy,
        recommendation_comparisons=recommendation_comparisons,
        role_switch_simulations=role_switch_simulations,
        # 🌟 核心替换：优先使用动态生成的项目，失败则使用规则字典兜底
        recommended_projects=list(primary_panel_bundle.get("recommended_projects", [])),
        learning_sprints=list(primary_panel_bundle.get("learning_sprints", [])),
        resume_surgery=resume_surgery,
        next_review_targets=_build_next_review_targets(student, primary, top_gap_keywords),
        growth_comparison=_build_growth_comparison(student, primary, previous_analysis),
        stakeholder_views=_build_stakeholder_views(student, primary, backups),
        evaluation_metrics=_build_evaluation_metrics(student, primary, parser_metadata, self_assessment, evidence_bundle),
        competency_dimensions=_build_competency_dimensions(student, primary),
        role_comparison_radar=role_comparison_radar,
        service_loop=_build_service_loop(student, primary, self_assessment),
        gap_benefit_analysis=list(primary_panel_bundle.get("gap_benefit_analysis", [])),
        plan_self_checks=list(primary_panel_bundle.get("plan_self_checks", [])),
        similar_cases=_build_similar_cases(student, primary),
        # 🌟 核心替换：优先使用动态生成的任务，失败则使用规则字典兜底
        assessment_tasks=list(primary_panel_bundle.get("assessment_tasks", [])),
        interview_focus=interview_focus,
        self_assessment=self_assessment,
        resource_map=resource_map,
        agent_questions=_build_agent_questions(student, primary, self_assessment),
        innovation_highlights=_build_innovation_highlights(student),
        technical_keywords=_build_technical_keywords(),
        technical_modules=_build_technical_modules(),
        evidence_bundle=evidence_bundle,
        service_scenarios=["学生自助诊断", "辅导员一生一策", "就业中心精准推岗"],
        # 🌟 亮点：更新了产品底层的技术签名
        product_signature="分块检索 + 证据重排 + 可解释匹配 + 复核留痕闭环",
        ai_match_commentary=ai_match_commentary,
    )
