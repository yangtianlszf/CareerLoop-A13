from __future__ import annotations

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


def build_career_plan(student: StudentProfile, ranked_matches: list[dict[str, object]]) -> CareerPlan:
    primary = ranked_matches[0]
    backups = ranked_matches[1:3]
    top_gap_keywords = _extract_gap_keywords(primary["gaps"])
    role_title = primary["role_title"]
    overview = (
        f"{student.name} 当前最适合优先冲刺 {role_title}，"
        f"同时可把 {'、'.join(match['role_title'] for match in backups) or '相近岗位'} 作为备选方向。"
    )

    risks = list(primary["gaps"])
    if student.missing_sections:
        risks.append("简历信息仍不完整：" + "、".join(student.missing_sections))

    action_plan_30 = [
        "补齐简历中的关键信息，至少补充专业、目标岗位、项目成果和实习职责",
        "围绕目标岗位补 2 到 3 项最关键技能：" + "、".join(top_gap_keywords[:3] or ["核心技能"]),
        "整理一份可口头讲清楚的项目经历，准备答辩时的能力举证",
    ]
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
    )
