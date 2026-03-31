from __future__ import annotations

from a13_starter.src.models import CareerPlan, JobProfile, MatchResult, StudentProfile


def _render_list(items: list[str]) -> str:
    if not items:
        return "- 无\n"
    return "".join(f"- {item}\n" for item in items)


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

## 3. 岗位匹配结果
{chr(10).join(top_match_lines)}

### 主推荐岗位解释
{top_matches[0].get('explanation', '暂无解释') if top_matches else '暂无解释'}

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
"""
