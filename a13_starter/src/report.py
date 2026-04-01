from __future__ import annotations

from a13_starter.src.models import CareerPlan, JobProfile, MatchResult, StudentProfile


def _render_list(items: list[str]) -> str:
    if not items:
        return "- 无\n"
    return "".join(f"- {item}\n" for item in items)


def _render_dict_items(items: list[dict[str, object]], formatter) -> str:
    if not items:
        return "- 无\n"
    return "".join(f"- {formatter(item)}\n" for item in items)


def build_report_markdown(
    student: StudentProfile,
    job: JobProfile,
    match_result: MatchResult,
) -> str:
    return f"""# 职业规划报告（原型）

## 1. 学生概况
- 姓名：{student.name}
- 学历：{student.education_level or "未识别"}
- 目标岗位：{' / '.join(student.target_roles) if student.target_roles else "未填写"}
- 意向城市：{student.city_preference or "未填写"}

## 2. 学生能力画像
### 技能
{_render_list(student.skills)}
### 证书
{_render_list(student.certificates)}
### 项目经历
{_render_list(student.projects)}
### 实习经历
{_render_list(student.internships)}

## 3. 目标岗位画像
- 岗位名称：{job.title}
- 学历要求：{job.education_requirement or "未识别"}
- 经验要求：{job.experience_requirement or "未识别"}
- 工作地点：{job.city or "未识别"}
- 薪资范围：{job.salary_range or "未识别"}

### 岗位核心技能
{_render_list(job.required_skills)}

### 岗位软技能
{_render_list(job.soft_skills)}

### 岗位成长路径
{_render_list(job.growth_path)}

## 4. 人岗匹配结果
- 综合得分：{match_result.score}
- 基础要求得分：{match_result.breakdown.basic_requirements}
- 专业技能得分：{match_result.breakdown.professional_skills}
- 职业素养得分：{match_result.breakdown.professional_literacy}
- 发展潜力得分：{match_result.breakdown.growth_potential}

### 优势
{_render_list(match_result.strengths)}

### 差距
{_render_list(match_result.gaps)}

### 行动建议
{_render_list(match_result.suggestions)}
"""


def build_career_report_markdown(
    student: StudentProfile,
    ranked_matches: list[dict[str, object]],
    career_plan: CareerPlan,
) -> str:
    top_matches = ranked_matches[:3]
    top_match_lines = []
    for item in top_matches:
        top_match_lines.append(
            f"- {item['role_title']}：{item['score']} 分（置信度：{item.get('confidence_label', '中')}）"
        )

    stakeholder_lines = _render_dict_items(
        career_plan.stakeholder_views,
        lambda item: f"{item.get('role', '角色')}：{item.get('headline', '')}；重点：{'、'.join(item.get('items', []))}",
    )
    metric_lines = _render_dict_items(
        career_plan.evaluation_metrics,
        lambda item: f"{item.get('name', '指标')}：{item.get('score', 0)} 分，{item.get('detail', '')}",
    )
    sprint_lines = _render_dict_items(
        career_plan.learning_sprints,
        lambda item: (
            f"{item.get('title', '训练任务')}（{item.get('type', '训练')}）"
            f"｜原因：{item.get('reason', '')}"
            f"｜交付物：{item.get('deliverable', '')}"
        ),
    )
    question_lines = _render_dict_items(
        career_plan.agent_questions,
        lambda item: (
            f"{item.get('question', '')}"
            f"｜建议回答：{item.get('suggested_answer', '')}"
            f"｜用途：{item.get('rationale', '')}"
        ),
    )
    innovation_lines = _render_dict_items(
        career_plan.innovation_highlights,
        lambda item: f"{item.get('title', '')}（{item.get('tag', '')}）：{item.get('detail', '')}",
    )
    evidence_lines = _render_dict_items(
        career_plan.evidence_bundle.get("items", []),
        lambda item: (
            f"{item.get('citation_id', '')} {item.get('source_type', '')}"
            f"｜{item.get('job_title', '')}"
            f"｜{item.get('company_name', '')}"
            f"｜命中词：{'、'.join(item.get('matched_terms', []))}"
            f"｜片段：{item.get('snippet', '')}"
        ),
    )
    technical_module_lines = _render_dict_items(
        career_plan.technical_modules,
        lambda item: f"{item.get('name', '')}（{item.get('tag', '')}）：{item.get('detail', '')}",
    )
    competency_lines = _render_dict_items(
        career_plan.competency_dimensions,
        lambda item: f"{item.get('name', '')}：{item.get('score', 0)} 分（权重 {item.get('weight', '')}），{item.get('note', '')}",
    )
    loop_lines = _render_dict_items(
        career_plan.service_loop,
        lambda item: f"{item.get('stage', '')}：{item.get('status', '')}，{item.get('detail', '')}",
    )
    resource_lines = _render_dict_items(
        career_plan.resource_map,
        lambda item: (
            f"{item.get('category', '')}｜{item.get('priority', '')}｜{item.get('title', '')}"
            f"：{item.get('description', '')}｜交付物：{item.get('deliverable', '')}"
        ),
    )
    comparison = career_plan.growth_comparison or {}

    return f"""# 大学生职业规划报告

## 1. 学生基本画像
- 姓名：{student.name}
- 学校：{student.school_name or "未填写"}
- 专业：{student.major or "未填写"}
- 学历：{student.education_level or "未识别"}
- 意向岗位：{'、'.join(student.target_roles) if student.target_roles else "未填写"}
- 意向行业：{'、'.join(student.target_industries) if student.target_industries else "未填写"}
- 意向城市：{student.city_preference or "未填写"}
- 画像完整度：{student.profile_completeness}
- 就业竞争力：{student.competitiveness_score}

## 2. 能力画像摘要
### 技术技能
{_render_list(student.skills)}
### 软技能
{_render_list(student.soft_skills)}
### 证书
{_render_list(student.certificates)}
### 项目经历
{_render_list(student.projects)}
### 实习经历
{_render_list(student.internships)}
### 获奖与竞赛
{_render_list(student.awards)}
### 当前缺失项
{_render_list(student.missing_sections)}
### 智能体补充信息
{_render_list([f"{key}：{value}" for key, value in student.agent_answers.items()])}

## 3. 岗位匹配结果
{chr(10).join(top_match_lines)}

### 主推荐岗位解释
{top_matches[0].get('explanation', '暂无解释') if top_matches else '暂无解释'}

### 证据驱动检索链
- 检索模式：{career_plan.evidence_bundle.get('retrieval_mode', '未生成')}
- 检索关键词：{'、'.join(career_plan.evidence_bundle.get('query_terms', [])) or '未生成'}
- 证据命中率：{career_plan.evidence_bundle.get('evidence_hit_rate', 0)}%（命中 {'、'.join(career_plan.evidence_bundle.get('hit_terms', [])) or '无'}）
- 检索摘要：{career_plan.evidence_bundle.get('summary', '暂无')}
{evidence_lines}

## 4. 主推荐岗位
- 主岗位：{career_plan.primary_role}
- 主岗位匹配分：{career_plan.primary_score}
- 备选岗位：{'、'.join(career_plan.backup_roles) if career_plan.backup_roles else "无"}
- 综合判断：{career_plan.overview}

### 主岗位优势
{_render_list(career_plan.strengths)}

### 当前风险与短板
{_render_list(career_plan.risks)}

## 5. 职业发展路径
### 主路径
{_render_list(career_plan.primary_growth_path)}

### 转岗路径
{_render_list(career_plan.transition_paths)}

## 6. 行动计划
### 30 天行动计划
{_render_list(career_plan.action_plan_30_days)}

### 90 天行动计划
{_render_list(career_plan.action_plan_90_days)}

### 180 天行动计划
{_render_list(career_plan.action_plan_180_days)}

## 7. 推荐补充项目
{_render_list(career_plan.recommended_projects)}

## 8. 训练闭环
### 学习冲刺任务
{sprint_lines}

### 下一次复测目标
{_render_list(career_plan.next_review_targets)}

## 9. 成长对比
- 对比结论：{comparison.get('summary', '暂无对比结果')}
### 变化明细
{_render_list(comparison.get('progress_items', []))}

## 10. 多角色服务视角
{stakeholder_lines}

## 11. 技术方案概述
- 技术定位：证据驱动生成 + 可解释匹配 + 人机协同闭环
- 方案概述：系统先把学生简历解析为结构化画像，再将官方 JD 与岗位模板转为可计算的岗位能力维度；匹配阶段输出总分与分维度解释，并对每条结论保留证据回看入口；规划阶段将能力差距映射为补强动作，通过智能体追问、岗位自测与复测形成成长闭环；学校侧再用运营看板承接个体结果与群体趋势，实现从推荐到运营的一体化服务。

### 技术关键词
{_render_list(career_plan.technical_keywords)}

### 核心技术模块
{technical_module_lines}

## 12. 评测快照
{metric_lines}

## 13. 胜任力模型
{competency_lines}

## 14. 服务闭环
{loop_lines}

### 岗位自测任务
{_render_list(career_plan.assessment_tasks)}

### 岗位自测结果
- 自测标题：{career_plan.self_assessment.get('title', '未生成')}
- 自测得分：{career_plan.self_assessment.get('score', 0)}
- 自测结论：{career_plan.self_assessment.get('summary', '暂无')}
{_render_list([f"{item.get('focus', '')}：{item.get('level', '')}" for item in career_plan.self_assessment.get('items', [])])}

## 15. 资源映射
{resource_lines}

## 16. 智能体追问
{question_lines}

## 17. 创新锚点
- 产品标签：{career_plan.product_signature or "未设置"}
{innovation_lines}
"""
