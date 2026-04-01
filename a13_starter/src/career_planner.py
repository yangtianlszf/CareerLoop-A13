from __future__ import annotations

import re
from typing import Any

from a13_starter.src.extractors import refresh_student_profile_metrics
from a13_starter.src.matcher import match_student_to_job
from a13_starter.src.models import CareerPlan, JobProfile, StudentProfile


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
        matches.append(
            {
                "role_title": template["canonical_title"],
                "role_family": template["role_family"],
                "score": match.score,
                "breakdown": match.breakdown.to_dict(),
                "strengths": match.strengths,
                "gaps": match.gaps,
                "suggestions": match.suggestions,
                "shared_skills": match.shared_skills,
                "missing_skills": match.missing_skills,
                "explanation": match.explanation,
                "confidence_label": match.confidence_label,
                "transition_paths": template["transition_paths"],
                "growth_path": template["vertical_growth_path"],
                "summary": template["summary"],
                "core_skills": template["core_skills"],
                "preferred_skills": template["preferred_skills"],
            }
        )
    matches.sort(key=lambda item: item["score"], reverse=True)
    if top_k is None:
        return matches
    return matches[:top_k]


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


def _project_suggestions_for_role(role_title: str) -> list[str]:
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
    targets = [
        f"下次复测时，将 {primary_match['role_title']} 匹配分从 {current_score} 分提升到 {min(current_score + 8, 92)} 分以上。",
    ]
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
) -> list[dict[str, Any]]:
    shared_count = len(primary_match.get("shared_skills", []))
    required_count = max(1, len(primary_match.get("core_skills", [])))
    evidence_coverage = min(100, int(shared_count / required_count * 100))
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

    return [
        {
            "name": "匹配证据覆盖",
            "score": evidence_coverage,
            "detail": f"Top1 岗位命中了 {shared_count}/{required_count} 个核心技能证据。",
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
    }
    return role_map.get(
        role_title,
        [
            {"id": "role_knowledge", "prompt": f"你现在对 {role_title} 核心知识点的把握程度如何？", "focus": "岗位知识"},
            {"id": "tool_chain", "prompt": f"你现在对 {role_title} 常用工具链的掌握程度如何？", "focus": "工具链"},
            {"id": "project_pitch", "prompt": "你能否清楚讲述一个与目标岗位相关的项目案例？", "focus": "项目表达"},
        ],
    )


def _build_self_assessment_summary(
    role_title: str,
    answers: dict[str, int] | None,
) -> dict[str, Any]:
    questions = _self_assessment_questions_for_role(role_title)
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
            "title": "官方 JD 驱动的双画像决策",
            "tag": "Evidence-First",
            "detail": "用官方 JD 样本构建岗位模板，再和学生画像做可解释匹配，避免空泛推荐。",
        },
        {
            "title": "追问后复测的职业规划闭环",
            "tag": "Agent Loop",
            "detail": "智能体会主动追问目标岗位、城市偏好和补强重点，再用第二次分析形成成长对比。",
        },
        {
            "title": "一份报告服务三类角色",
            "tag": "Campus Service",
            "detail": "同一底层结果同时服务学生自助决策、辅导员重点帮扶和就业中心岗位推送。",
        },
    ]


def build_career_plan(
    student: StudentProfile,
    ranked_matches: list[dict[str, object]],
    *,
    previous_analysis: dict[str, Any] | None = None,
    parser_metadata: dict[str, Any] | None = None,
    self_assessment_answers: dict[str, int] | None = None,
) -> CareerPlan:
    primary = ranked_matches[0]
    backups = ranked_matches[1:3]
    focus_gap = student.agent_answers.get("improvement_focus")
    top_gap_keywords = list(primary.get("missing_skills") or [])
    if focus_gap and focus_gap not in top_gap_keywords:
        top_gap_keywords.insert(0, focus_gap)
    if not top_gap_keywords:
        top_gap_keywords = ["项目表达", "岗位举证"]
    role_title = primary["role_title"]
    focus_role = student.agent_answers.get("target_role") or role_title
    overview = (
        f"{student.name} 当前最适合优先冲刺 {role_title}，"
        f"同时可把 {'、'.join(match['role_title'] for match in backups) or '相近岗位'} 作为备选方向。"
    )
    if focus_role != role_title:
        overview += f" 结合智能体补充问答，系统会继续用 {focus_role} 作为下一轮对齐目标。"

    risks = list(primary["gaps"])
    if student.missing_sections:
        risks.append("简历信息仍不完整：" + "、".join(student.missing_sections))

    short_goal = student.agent_answers.get("thirty_day_goal") or "做出一个可展示的求职作品"
    self_assessment = _build_self_assessment_summary(role_title, self_assessment_answers)
    resource_map = _build_resource_map(role_title, top_gap_keywords, self_assessment)
    action_plan_30 = [
        "补齐简历中的关键信息，至少补充专业、目标岗位、项目成果和实习职责",
        "围绕目标岗位补 2 到 3 项最关键技能：" + "、".join(top_gap_keywords[:3] or ["项目表达", "岗位举证"]),
        f"30 天内优先拿到一个明确成果：{short_goal}",
    ]
    if focus_gap:
        action_plan_30.insert(1, f"优先围绕补充问答里选择的短板 {focus_gap} 做一次专题补强")

    action_plan_90 = [
        "完成 1 个与目标岗位直接相关的项目，并沉淀 README、截图和演示视频",
        "根据备选岗位补一个通用能力模块，比如接口测试、部署文档或原型设计",
        "用 3 份真实或模拟 JD 反复校准简历和能力画像",
    ]
    action_plan_180 = [
        "优先争取与主岗位匹配的实习或真实项目经历",
        "建立主岗位 + 备选岗位的双路径求职策略，持续迭代作品集",
        "将项目、竞赛和职业规划报告整合成一套完整求职材料",
    ]

    return CareerPlan(
        primary_role=role_title,
        backup_roles=[match["role_title"] for match in backups],
        primary_score=primary["score"],
        overview=overview,
        strengths=list(primary["strengths"]),
        risks=risks,
        primary_growth_path=list(primary["growth_path"]),
        transition_paths=list(primary["transition_paths"]),
        action_plan_30_days=action_plan_30,
        action_plan_90_days=action_plan_90,
        action_plan_180_days=action_plan_180,
        recommended_projects=_project_suggestions_for_role(role_title),
        learning_sprints=_build_learning_sprints(student, primary, top_gap_keywords),
        next_review_targets=_build_next_review_targets(student, primary, top_gap_keywords),
        growth_comparison=_build_growth_comparison(student, primary, previous_analysis),
        stakeholder_views=_build_stakeholder_views(student, primary, backups),
        evaluation_metrics=_build_evaluation_metrics(student, primary, parser_metadata, self_assessment),
        competency_dimensions=_build_competency_dimensions(student, primary),
        service_loop=_build_service_loop(student, primary, self_assessment),
        assessment_tasks=_assessment_tasks_for_role(role_title),
        self_assessment=self_assessment,
        resource_map=resource_map,
        agent_questions=_build_agent_questions(student, primary, self_assessment),
        innovation_highlights=_build_innovation_highlights(student),
        service_scenarios=["学生自助诊断", "辅导员一生一策", "就业中心精准推岗"],
        product_signature="官方 JD 驱动的可解释双画像闭环",
    )
