ROLE_TEMPLATE_SPECS = {
    "Java": {
        "canonical_title": "Java开发工程师",
        "role_family": "开发",
        "summary": "负责业务系统后端开发、接口设计、数据库建模与服务稳定性优化，适合作为后端方向的核心岗位画像。",
        "must_have_skills": ["Java", "Spring", "Spring Boot", "SQL", "MySQL", "Linux", "Git"],
        "preferred_skills": ["Redis", "Docker", "Postman", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "学习能力", "责任心", "分析能力"],
        "certificates": ["英语四级", "计算机二级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，可接受实习经历替代部分经验",
        "vertical_growth_path": ["初级Java开发工程师", "中级Java开发工程师", "高级Java开发工程师", "技术负责人"],
        "transition_paths": ["测试开发工程师", "实施工程师", "技术支持工程师"],
    },
    "C/C++": {
        "canonical_title": "C/C++开发工程师",
        "role_family": "开发",
        "summary": "负责底层模块、系统组件、嵌入式或高性能程序开发，是偏底层和系统方向的重要岗位画像。",
        "must_have_skills": ["C", "C++", "Linux", "Git"],
        "preferred_skills": ["Python", "SQL", "单片机", "嵌入式", "硬件调试"],
        "soft_skills": ["沟通", "学习能力", "团队协作", "责任心", "分析能力"],
        "certificates": ["英语四级", "计算机二级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有竞赛或项目经历更佳",
        "vertical_growth_path": ["初级C/C++开发工程师", "中级C/C++开发工程师", "高级系统工程师", "架构师"],
        "transition_paths": ["硬件测试工程师", "测试工程师", "技术支持工程师"],
    },
    "前端开发": {
        "canonical_title": "前端开发工程师",
        "role_family": "开发",
        "summary": "负责 Web 前端页面开发、交互实现和体验优化，是职业规划系统展示层的代表岗位。",
        "must_have_skills": ["HTML", "CSS", "JavaScript", "Vue", "Git"],
        "preferred_skills": ["TypeScript", "React", "Node.js", "需求分析", "原型设计"],
        "soft_skills": ["沟通", "学习能力", "团队协作", "责任心", "执行力"],
        "certificates": ["英语四级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有页面项目或实习经历更佳",
        "vertical_growth_path": ["前端开发工程师", "资深前端开发工程师", "前端架构师", "技术负责人"],
        "transition_paths": ["产品专员/助理", "测试工程师", "Java开发工程师"],
    },
    "实施工程师": {
        "canonical_title": "实施工程师",
        "role_family": "交付",
        "summary": "负责软件系统部署、上线实施、培训和交付支持，强调沟通能力、项目协同与现场问题处理能力。",
        "must_have_skills": ["Linux", "SQL", "MySQL", "项目管理"],
        "preferred_skills": ["Python", "Java", "数据分析", "需求分析", "Postman"],
        "soft_skills": ["沟通", "责任心", "学习能力", "团队协作", "表达能力", "抗压"],
        "certificates": ["英语四级"],
        "education_requirement": "本科",
        "experience_requirement": "可接受应届，要求较强执行力和现场适应能力",
        "vertical_growth_path": ["实施工程师", "高级实施工程师", "实施顾问", "交付负责人"],
        "transition_paths": ["技术支持工程师", "项目经理", "产品专员/助理"],
    },
    "技术支持工程师": {
        "canonical_title": "技术支持工程师",
        "role_family": "服务",
        "summary": "负责客户现场或远程技术支持、问题定位和解决方案跟进，适合作为服务与技术结合型岗位画像。",
        "must_have_skills": ["Linux", "SQL", "需求分析"],
        "preferred_skills": ["Python", "Java", "数据分析", "MySQL", "项目管理"],
        "soft_skills": ["沟通", "责任心", "学习能力", "表达能力", "抗压", "团队协作"],
        "certificates": ["英语四级"],
        "education_requirement": "本科",
        "experience_requirement": "应届可投，强调服务意识和问题定位能力",
        "vertical_growth_path": ["技术支持工程师", "高级技术支持工程师", "解决方案工程师", "服务负责人"],
        "transition_paths": ["实施工程师", "售前工程师", "测试工程师"],
    },
    "测试工程师": {
        "canonical_title": "测试工程师",
        "role_family": "测试",
        "summary": "负责测试设计、缺陷跟踪、回归验证和质量保障，是系统稳定性和交付质量的重要岗位。",
        "must_have_skills": ["测试用例", "功能测试", "SQL", "Linux"],
        "preferred_skills": ["Python", "Java", "自动化测试", "Postman", "JMeter", "缺陷管理"],
        "soft_skills": ["沟通", "责任心", "团队协作", "学习能力", "分析能力"],
        "certificates": ["英语四级", "软件测试相关认证"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有测试项目经验更佳",
        "vertical_growth_path": ["测试工程师", "高级测试工程师", "测试开发工程师", "测试经理"],
        "transition_paths": ["软件测试工程师", "质量管理/测试", "Java开发工程师"],
    },
    "软件测试": {
        "canonical_title": "软件测试工程师",
        "role_family": "测试",
        "summary": "聚焦软件功能、接口与自动化测试，是比赛中最容易落地的质量保障岗位之一。",
        "must_have_skills": ["测试用例", "功能测试", "接口测试", "SQL", "Linux"],
        "preferred_skills": ["Python", "Java", "自动化测试", "Selenium", "Postman", "Jenkins"],
        "soft_skills": ["沟通", "责任心", "学习能力", "团队协作", "分析能力"],
        "certificates": ["英语四级", "软件测试相关认证"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有自动化测试经历更佳",
        "vertical_growth_path": ["软件测试工程师", "自动化测试工程师", "测试开发工程师", "质量平台主管"],
        "transition_paths": ["测试工程师", "质量管理/测试", "技术支持工程师"],
    },
    "硬件测试": {
        "canonical_title": "硬件测试工程师",
        "role_family": "测试",
        "summary": "负责硬件设备测试、稳定性验证和故障定位，适合体现电气与计算机交叉方向的岗位画像。",
        "must_have_skills": ["硬件调试", "Linux", "C++", "单片机"],
        "preferred_skills": ["Python", "嵌入式", "电路设计", "数据分析", "测试用例"],
        "soft_skills": ["沟通", "责任心", "学习能力", "团队协作", "分析能力"],
        "certificates": ["英语四级", "电子类相关证书"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有实验室或硬件项目经历更佳",
        "vertical_growth_path": ["硬件测试工程师", "可靠性测试工程师", "高级测试工程师", "硬件质量经理"],
        "transition_paths": ["C/C++开发工程师", "质量管理/测试", "测试工程师"],
    },
    "质量管理/测试": {
        "canonical_title": "质量工程师",
        "role_family": "质量",
        "summary": "负责质量标准制定、测试流程管理和质量改进，偏向质量保障和流程化管理能力。",
        "must_have_skills": ["测试用例", "缺陷管理", "项目管理"],
        "preferred_skills": ["数据分析", "功能测试", "自动化测试", "需求分析"],
        "soft_skills": ["沟通", "责任心", "抗压", "执行力", "分析能力"],
        "certificates": ["质量管理相关证书"],
        "education_requirement": "本科",
        "experience_requirement": "有测试或质量相关经验更佳",
        "vertical_growth_path": ["质量工程师", "高级质量工程师", "QA负责人", "质量经理"],
        "transition_paths": ["测试工程师", "软件测试工程师", "项目经理"],
    },
    "产品专员/助理": {
        "canonical_title": "产品助理",
        "role_family": "产品",
        "summary": "负责需求收集、原型整理、文档撰写与跨团队沟通，适合作为职业规划系统业务分析方向岗位画像。",
        "must_have_skills": ["需求分析", "原型设计", "Axure", "PRD"],
        "preferred_skills": ["用户研究", "数据分析", "项目管理", "沟通表达"],
        "soft_skills": ["沟通", "责任心", "分析能力", "学习能力", "团队协作", "表达能力"],
        "certificates": ["英语四级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有产品或运营项目经历更佳",
        "vertical_growth_path": ["产品助理", "产品专员", "产品经理", "高级产品经理"],
        "transition_paths": ["前端开发工程师", "实施工程师", "项目经理"],
    },
}


SUPPLEMENTAL_ROLE_TEMPLATES = [
    {
        "source_title": "Python开发工程师",
        "canonical_title": "Python开发工程师",
        "role_family": "开发",
        "dataset_job_count": 0,
        "summary": "围绕 Python 后端服务、AI 应用工程或自动化平台开发开展工作，强调 Python 工程实现、部署联调和框架落地能力，不作为通用后端的默认兜底岗位。",
        "core_skills": ["Python", "SQL", "Linux", "Git"],
        "preferred_skills": ["MySQL", "Docker", "Redis", "FastAPI", "Flask", "Django", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "学习能力", "责任心", "分析能力"],
        "certificates": ["英语四级", "计算机二级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，但更适合具备 Python 后端、AI 应用落地、自动化平台或脚本工程化经历的学生",
        "typical_industries": ["企业服务", "计算机软件", "人工智能", "互联网", "IT服务"],
        "typical_cities": ["上海-浦东新区", "杭州-余杭区", "深圳-南山区", "北京-海淀区", "南京-雨花台区"],
        "sample_salary_ranges": ["9000-15000元", "1-1.8万", "8000-12000元", "1.2-1.8万"],
        "vertical_growth_path": ["Python开发工程师", "Python后端工程师", "高级后端开发工程师", "技术负责人"],
        "transition_paths": ["数据分析师", "测试开发工程师", "Java开发工程师"],
        "match_weights": {
            "basic_requirements": 0.2,
            "professional_skills": 0.4,
            "professional_literacy": 0.2,
            "growth_potential": 0.2,
        },
        "dataset_evidence": {
            "top_skills": [["Python", 0], ["SQL", 0], ["MySQL", 0], ["Linux", 0], ["Git", 0]],
            "top_soft_skills": [["沟通", 0], ["团队协作", 0], ["学习能力", 0], ["责任心", 0]],
            "top_industries": [["计算机软件", 0], ["互联网", 0], ["企业服务", 0]],
            "top_cities": [["上海-浦东新区", 0], ["杭州-余杭区", 0], ["深圳-南山区", 0]],
        },
        "innovation_ability": "能把业务需求快速转成 Python 服务、AI 应用能力或自动化脚本，提升开发和交付效率",
        "learning_ability": "能快速学习新框架、模型接入方式和接口规范，在短周期内完成模块搭建与联调",
        "stress_tolerance": "能在联调、上线和排障场景中保持稳定推进和问题闭环",
        "communication_ability": "能和前端、测试及业务方有效同步接口、数据结构和迭代进度",
        "internship_ability": "具备参与 Python 服务开发、AI 应用落地、数据库设计和系统联调的实践基础",
    },
    {
        "source_title": "数据分析师",
        "canonical_title": "数据分析师",
        "role_family": "数据",
        "dataset_job_count": 0,
        "summary": "围绕业务指标拆解、数据清洗、报表分析和结论输出开展工作，适合具备 Python/SQL 和分析表达能力的学生。",
        "core_skills": ["Python", "SQL", "Excel", "数据分析", "PPT"],
        "preferred_skills": ["MySQL", "需求分析", "机器学习", "项目管理", "沟通"],
        "soft_skills": ["分析能力", "沟通", "表达能力", "学习能力", "执行力", "团队协作"],
        "certificates": ["英语四级", "计算机二级"],
        "education_requirement": "本科",
        "experience_requirement": "应届优先，有数据分析项目、商业分析竞赛或可视化报告经历更佳",
        "typical_industries": ["互联网", "电子商务", "企业服务", "金融科技", "零售"],
        "typical_cities": ["上海-浦东新区", "杭州-余杭区", "深圳-南山区", "北京-海淀区", "成都-高新区"],
        "sample_salary_ranges": ["7000-10000元", "8000-12000元", "1-1.5万", "9000-14000元"],
        "vertical_growth_path": ["初级数据分析师", "数据分析师", "高级数据分析师", "数据产品经理"],
        "transition_paths": ["Python开发工程师", "运营专员", "产品助理"],
        "match_weights": {
            "basic_requirements": 0.2,
            "professional_skills": 0.4,
            "professional_literacy": 0.2,
            "growth_potential": 0.2,
        },
        "dataset_evidence": {
            "top_skills": [["Python", 0], ["SQL", 0], ["Excel", 0], ["数据分析", 0], ["PPT", 0]],
            "top_soft_skills": [["分析能力", 0], ["沟通", 0], ["表达能力", 0], ["学习能力", 0]],
            "top_industries": [["互联网", 0], ["电子商务", 0], ["企业服务", 0]],
            "top_cities": [["上海-浦东新区", 0], ["杭州-余杭区", 0], ["深圳-南山区", 0]],
        },
        "innovation_ability": "能从数据波动中主动提出假设，并设计分析框架验证业务问题",
        "learning_ability": "能快速学习新业务指标口径和分析工具，在短周期内形成分析结论",
        "stress_tolerance": "能在业务方高频追数和紧急汇报场景下保持分析口径一致和输出质量",
        "communication_ability": "能把复杂数据结果转译为业务同学能理解的结论和行动建议",
        "internship_ability": "具备完成数据清洗、指标分析、可视化汇报和复盘建议的基础实践能力",
    }
]


TEMPLATE_CALIBRATIONS: dict[str, dict[str, object]] = {
    "Java开发工程师": {
        "core_skills": ["Java", "Spring", "SQL", "MySQL"],
        "preferred_skills": ["Spring Boot", "Linux", "Git", "Redis", "Docker", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "学习能力", "责任心", "执行力", "分析能力"],
    },
    "C/C++开发工程师": {
        "core_skills": ["C", "C++", "Linux"],
        "preferred_skills": ["嵌入式", "单片机", "TCP/IP", "Python", "Git", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "学习能力", "责任心", "创新", "分析能力"],
    },
    "前端开发工程师": {
        "core_skills": ["HTML", "CSS", "JavaScript"],
        "preferred_skills": ["Vue", "React", "TypeScript", "Git", "原型设计", "需求分析"],
        "soft_skills": ["团队协作", "沟通", "学习能力", "创新", "执行力"],
    },
    "实施工程师": {
        "core_skills": ["Linux", "SQL", "项目管理"],
        "preferred_skills": ["MySQL", "Oracle", "HTTP", "需求分析", "数据分析", "ERP"],
        "soft_skills": ["执行力", "沟通", "服务意识", "团队协作", "责任心", "表达能力"],
    },
    "技术支持工程师": {
        "core_skills": ["Linux", "需求分析"],
        "preferred_skills": ["项目管理", "SQL", "PPT", "Excel", "HTTP", "Oracle", "PLC", "数据分析"],
        "soft_skills": ["沟通", "服务意识", "团队协作", "表达能力", "责任心", "执行力"],
    },
    "测试工程师": {
        "core_skills": ["测试用例", "功能测试"],
        "preferred_skills": ["自动化测试", "性能测试", "SQL", "Linux", "Python", "MySQL", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "责任心", "分析能力", "学习能力"],
    },
    "软件测试工程师": {
        "core_skills": ["测试用例", "功能测试", "自动化测试"],
        "preferred_skills": ["接口测试", "Selenium", "Python", "Linux", "需求分析", "性能测试", "SQL"],
        "soft_skills": ["沟通", "团队协作", "责任心", "分析能力", "学习能力"],
    },
    "测试开发工程师": {
        "core_skills": ["自动化测试", "Selenium", "测试用例"],
        "preferred_skills": ["Python", "Java", "Linux", "SQL", "Jenkins", "性能测试", "Git"],
        "soft_skills": ["沟通", "团队协作", "责任心", "分析能力", "学习能力"],
    },
    "硬件测试工程师": {
        "core_skills": ["测试用例", "功能测试", "性能测试"],
        "preferred_skills": ["硬件调试", "嵌入式", "C++", "Linux", "单片机", "电路设计"],
        "soft_skills": ["沟通", "团队协作", "责任心", "学习能力", "分析能力"],
    },
    "质量工程师": {
        "core_skills": ["测试用例", "项目管理"],
        "preferred_skills": ["数据分析", "功能测试", "Excel", "Word", "需求分析"],
        "soft_skills": ["沟通", "责任心", "执行力", "分析能力", "抗压"],
    },
    "产品助理": {
        "core_skills": ["需求分析", "原型设计"],
        "preferred_skills": ["PRD", "Axure", "PPT", "数据分析", "项目管理", "用户研究"],
        "soft_skills": ["沟通", "团队协作", "分析能力", "学习能力", "表达能力"],
    },
    "售前工程师": {
        "core_skills": ["商务谈判", "PPT", "Excel"],
        "preferred_skills": ["方案设计", "项目管理", "Word", "数据分析", "CRM", "ERP", "Visio"],
        "soft_skills": ["沟通", "表达能力", "客户关系", "团队协作", "责任心"],
    },
    "项目专员": {
        "core_skills": ["项目管理", "Excel", "PPT"],
        "preferred_skills": ["Word", "数据库", "ERP", "Visio", "需求分析"],
        "soft_skills": ["沟通", "执行力", "团队协作", "责任心", "表达能力"],
    },
    "项目经理": {
        "core_skills": ["项目管理", "需求分析"],
        "preferred_skills": ["PMP", "方案设计", "Excel", "Word", "商务谈判", "数据分析"],
        "soft_skills": ["沟通", "执行力", "团队协作", "责任心", "抗压", "表达能力"],
    },
    "运营专员": {
        "core_skills": ["社区运营", "用户运营", "数据分析"],
        "preferred_skills": ["内容运营", "Excel", "PPT", "Word", "SEO", "项目管理"],
        "soft_skills": ["沟通", "团队协作", "执行力", "学习能力", "责任心"],
    },
    "Python开发工程师": {
        "summary": "围绕 Python 后端服务、AI 应用工程或自动化平台开发开展工作，强调 Python 工程实现、部署联调和框架落地能力，不作为通用后端的默认兜底岗位。",
        "core_skills": ["Python", "SQL", "Linux", "Git"],
        "preferred_skills": ["MySQL", "Docker", "Redis", "FastAPI", "Flask", "Django", "需求分析"],
        "soft_skills": ["沟通", "团队协作", "学习能力", "责任心", "分析能力"],
        "experience_requirement": "应届优先，但更适合具备 Python 后端、AI 应用落地、自动化平台或脚本工程化经历的学生",
        "vertical_growth_path": ["Python开发工程师", "Python后端工程师", "高级后端开发工程师", "技术负责人"],
        "typical_industries": ["企业服务", "计算机软件", "人工智能", "互联网", "IT服务"],
    },
    "数据分析师": {
        "core_skills": ["数据分析", "Excel", "SQL"],
        "preferred_skills": ["Python", "PPT", "MySQL", "项目管理", "需求分析", "Word"],
        "soft_skills": ["分析能力", "沟通", "表达能力", "学习能力", "执行力", "团队协作"],
    },
}


def _dedupe_list(items: list[str] | None) -> list[str]:
    deduped: list[str] = []
    for item in items or []:
        text = str(item or "").strip()
        if text and text not in deduped:
            deduped.append(text)
    return deduped


def _apply_template_calibrations(template: dict[str, object]) -> dict[str, object]:
    normalized = dict(template)
    title = str(normalized.get("canonical_title", "")).strip()
    override = TEMPLATE_CALIBRATIONS.get(title)
    if not override:
        return normalized

    for key, value in override.items():
        if isinstance(value, list):
            normalized[key] = _dedupe_list(list(value))
        else:
            normalized[key] = value
    return normalized


def ensure_role_templates(templates: list[dict[str, object]]) -> list[dict[str, object]]:
    normalized = [_apply_template_calibrations(dict(item)) for item in templates if isinstance(item, dict)]
    existing_titles = {str(item.get("canonical_title", "")).strip() for item in normalized}
    for template in SUPPLEMENTAL_ROLE_TEMPLATES:
        title = str(template.get("canonical_title", "")).strip()
        if title and title not in existing_titles:
            normalized.append(_apply_template_calibrations(dict(template)))
            existing_titles.add(title)
    return normalized
