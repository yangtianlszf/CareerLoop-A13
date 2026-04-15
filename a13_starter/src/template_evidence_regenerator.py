from __future__ import annotations

from collections import Counter
from typing import Any

from a13_starter.src.dataset import build_job_text_from_row
from a13_starter.src.extractors import build_job_profile


def _top_pairs(counter: Counter[str], limit: int) -> list[list[object]]:
    return [[name, count] for name, count in counter.most_common(limit) if name]


def _row_identity(row: dict[str, Any]) -> str:
    return str(
        row.get("岗位编码")
        or f"{row.get('岗位名称', '')}|{row.get('公司名称', '')}|{row.get('地址', '')}|{row.get('薪资范围', '')}"
    )


def _clean_lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _raw_title(row: dict[str, Any]) -> str:
    return str(row.get("岗位名称", "")).strip()


def _normalized_title(row: dict[str, Any]) -> str:
    return str(row.get("_normalized_title", "")).strip()


def _is_exact_title_match(template: dict[str, Any], row: dict[str, Any]) -> bool:
    raw_title = _raw_title(row)
    canonical_title = str(template.get("canonical_title", "")).strip()
    source_title = str(template.get("source_title", "")).strip()
    if not raw_title:
        return False
    return bool((canonical_title and raw_title == canonical_title) or (source_title and raw_title == source_title))


def _is_normalized_cluster_match(template: dict[str, Any], row: dict[str, Any]) -> bool:
    canonical_title = str(template.get("canonical_title", "")).strip()
    if not canonical_title:
        return False
    return _normalized_title(row) == canonical_title and not _is_exact_title_match(template, row)


def _classify_template_rows(
    template: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    exact_title_rows: list[dict[str, Any]] = []
    normalized_cluster_rows: list[dict[str, Any]] = []
    fallback_inferred_rows: list[dict[str, Any]] = []

    for row in rows:
        if _is_exact_title_match(template, row):
            exact_title_rows.append(row)
        elif _is_normalized_cluster_match(template, row):
            normalized_cluster_rows.append(row)
        else:
            fallback_inferred_rows.append(row)

    return {
        "exact_title_rows": exact_title_rows,
        "normalized_cluster_rows": normalized_cluster_rows,
        "fallback_inferred_rows": fallback_inferred_rows,
    }


def _build_sample_scopes(classified_rows: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    scope_defs = [
        (
            "exact_title",
            "原始同名岗位样本",
            "岗位标题与模板岗位名高度一致，可直接展示为同名示例",
        ),
        (
            "normalized_cluster",
            "推断聚类样本",
            "岗位标题不完全一致，但归一化后属于同一岗位族，用于统计共性要求",
        ),
        (
            "fallback_inferred",
            "关键词补充样本",
            "官方样本缺少稳定同名岗位时，用关键词和岗位族补充统计，不直接等同原始同名岗位",
        ),
    ]
    scopes: list[dict[str, Any]] = []
    for key, label, description in scope_defs:
        scopes.append(
            {
                "key": key,
                "label": label,
                "count": len(classified_rows[f"{key}_rows"]),
                "description": description,
            }
        )
    return scopes


def _resolve_evidence_mode(classified_rows: dict[str, list[dict[str, Any]]]) -> str:
    exact_count = len(classified_rows["exact_title_rows"])
    cluster_count = len(classified_rows["normalized_cluster_rows"])
    fallback_count = len(classified_rows["fallback_inferred_rows"])

    if exact_count and not cluster_count and not fallback_count:
        return "exact_title"
    if cluster_count and not exact_count and not fallback_count:
        return "normalized_cluster"
    if fallback_count and not exact_count and not cluster_count:
        return "fallback_inferred"
    if exact_count and (cluster_count or fallback_count):
        return "mixed"
    if cluster_count and fallback_count:
        return "cluster_plus_fallback"
    return "empty"


def _fallback_keyword_rows(template: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    canonical_title = str(template.get("canonical_title", "")).strip()
    source_title = str(template.get("source_title", "")).strip()

    if "python" in canonical_title.lower() or "python" in source_title.lower():
        direct_title_matches = [
            row for row in rows if "python" in _clean_lower(row.get("岗位名称", ""))
        ]
        if direct_title_matches:
            return direct_title_matches
        return [
            row
            for row in rows
            if "python" in _clean_lower(row.get("岗位详情", ""))
            and "开发" in str(row.get("_role_family", ""))
        ]

    if "数据分析" in canonical_title or "数据分析" in source_title:
        return [
            row
            for row in rows
            if "数据分析" in str(row.get("岗位名称", ""))
            or "数据分析" in str(row.get("岗位详情", ""))
        ]

    return []


def select_template_rows(template: dict[str, Any] | None, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not template:
        return []

    canonical_title = str(template.get("canonical_title", "")).strip()
    source_title = str(template.get("source_title", "")).strip()

    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        normalized_title = _normalized_title(row)
        raw_title = _raw_title(row)
        if (canonical_title and normalized_title == canonical_title) or (source_title and raw_title == source_title):
            selected[_row_identity(row)] = row

    if selected:
        return list(selected.values())

    fallback_rows = _fallback_keyword_rows(template, rows)
    for row in fallback_rows:
        selected[_row_identity(row)] = row
    return list(selected.values())


def _profiled_template_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profiled: list[dict[str, Any]] = []
    for row in rows:
        profile = build_job_profile(build_job_text_from_row({str(key): str(value) for key, value in row.items()}))
        profiled.append({"row": row, "profile": profile})
    return profiled


def _template_focus_keywords(template: dict[str, Any]) -> list[str]:
    title = str(template.get("canonical_title", "")).strip().lower()
    source_title = str(template.get("source_title", "")).strip().lower()
    merged = f"{title} {source_title}"

    keyword_map = [
        ("python", ["python"]),
        ("数据分析", ["数据分析"]),
        ("技术支持", ["技术支持"]),
        ("实施", ["实施"]),
        ("硬件测试", ["硬件测试"]),
        ("软件测试", ["软件测试"]),
        ("测试开发", ["测试开发"]),
        ("测试", ["测试"]),
        ("前端", ["前端"]),
        ("java", ["java"]),
        ("c/c++", ["c/c++", "c++"]),
        ("产品", ["产品"]),
        ("运营", ["运营"]),
        ("项目", ["项目"]),
        ("售前", ["售前"]),
    ]
    for marker, keywords in keyword_map:
        if marker in merged:
            return keywords
    return [token for token in [source_title, title] if token]


def _title_signal_score(template: dict[str, Any], row: dict[str, Any]) -> int:
    raw_title = str(row.get("岗位名称", "")).strip().lower()
    detail = str(row.get("岗位详情", "")).strip().lower()
    canonical_title = str(template.get("canonical_title", "")).strip().lower()
    source_title = str(template.get("source_title", "")).strip().lower()

    score = 0
    if raw_title and raw_title == canonical_title:
        score += 12
    if source_title and raw_title == source_title:
        score += 12
    for keyword in _template_focus_keywords(template):
        if not keyword:
            continue
        if keyword in raw_title:
            score += 8
        elif keyword in detail:
            score += 1
    return score


def _representative_jobs(
    template: dict[str, Any],
    profiled_rows: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    ranked = sorted(
        profiled_rows,
        key=lambda item: (
            _title_signal_score(template, item["row"]),
            len(item["profile"].required_skills),
            len(item["profile"].soft_skills),
            bool(item["row"].get("_normalized_salary_range") or item["row"].get("薪资范围")),
            len(str(item["row"].get("岗位详情", ""))),
        ),
        reverse=True,
    )
    if ranked and _title_signal_score(template, ranked[0]["row"]) <= 1:
        return []

    jobs: list[dict[str, Any]] = []
    for item in ranked[: max(1, limit)]:
        row = item["row"]
        profile = item["profile"]
        jobs.append(
            {
                "job_title": row.get("岗位名称"),
                "company_name": row.get("公司名称"),
                "city": row.get("_normalized_address") or row.get("地址"),
                "salary_range": row.get("_normalized_salary_range") or row.get("薪资范围"),
                "industry": row.get("所属行业"),
                "job_code": row.get("岗位编码"),
                "job_url": row.get("岗位来源地址"),
                "job_detail": row.get("岗位详情"),
                "required_skills": list(profile.required_skills),
            }
        )
    return jobs


def build_template_evidence_payload(
    template: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    limit: int = 6,
) -> dict[str, Any]:
    matched_rows = select_template_rows(template, rows)
    classified_rows = _classify_template_rows(template, matched_rows)
    profiled_rows = _profiled_template_rows(matched_rows)
    exact_profiled_rows = _profiled_template_rows(classified_rows["exact_title_rows"])
    normalized_cluster_profiled_rows = _profiled_template_rows(classified_rows["normalized_cluster_rows"])
    fallback_profiled_rows = _profiled_template_rows(classified_rows["fallback_inferred_rows"])

    skill_counter: Counter[str] = Counter()
    soft_skill_counter: Counter[str] = Counter()
    industry_counter: Counter[str] = Counter()
    city_counter: Counter[str] = Counter()
    salary_counter: Counter[str] = Counter()

    for item in profiled_rows:
        row = item["row"]
        profile = item["profile"]
        skill_counter.update(profile.required_skills)
        soft_skill_counter.update(profile.soft_skills)
        for industry in str(row.get("所属行业", "")).split(","):
            cleaned = industry.strip()
            if cleaned:
                industry_counter.update([cleaned])
        city = str(row.get("_normalized_address") or row.get("地址", "")).strip()
        salary = str(row.get("_normalized_salary_range") or row.get("薪资范围", "")).strip()
        if city:
            city_counter.update([city])
        if salary:
            salary_counter.update([salary])

    dataset_evidence = {
        "top_skills": _top_pairs(skill_counter, 10) or list(template.get("dataset_evidence", {}).get("top_skills", [])),
        "top_soft_skills": _top_pairs(soft_skill_counter, 8) or list(template.get("dataset_evidence", {}).get("top_soft_skills", [])),
        "top_industries": _top_pairs(industry_counter, 8) or list(template.get("dataset_evidence", {}).get("top_industries", [])),
        "top_cities": _top_pairs(city_counter, 8) or list(template.get("dataset_evidence", {}).get("top_cities", [])),
    }

    exact_representative_jobs = _representative_jobs(template, exact_profiled_rows, limit)
    cluster_representative_jobs = _representative_jobs(template, normalized_cluster_profiled_rows, limit)
    fallback_representative_jobs = _representative_jobs(template, fallback_profiled_rows, limit)

    representative_jobs = exact_representative_jobs
    representative_jobs_source = "exact_title"
    if not representative_jobs:
        representative_jobs = cluster_representative_jobs
        representative_jobs_source = "normalized_cluster"
    if not representative_jobs:
        representative_jobs = fallback_representative_jobs
        representative_jobs_source = "fallback_inferred"
    if not representative_jobs:
        representative_jobs_source = "none"

    return {
        "role_title": str(template.get("canonical_title", "")),
        "source_title": str(template.get("source_title", "")),
        "evidence_mode": _resolve_evidence_mode(classified_rows),
        "sample_scopes": _build_sample_scopes(classified_rows),
        "dataset_job_count": len(matched_rows),
        "exact_title_job_count": len(classified_rows["exact_title_rows"]),
        "normalized_cluster_job_count": len(classified_rows["normalized_cluster_rows"]),
        "fallback_inferred_job_count": len(classified_rows["fallback_inferred_rows"]),
        "typical_industries": [item[0] for item in dataset_evidence["top_industries"][:5]] or list(template.get("typical_industries", [])),
        "typical_cities": [item[0] for item in dataset_evidence["top_cities"][:5]] or list(template.get("typical_cities", [])),
        "sample_salary_ranges": [item[0] for item in _top_pairs(salary_counter, 5)] or list(template.get("sample_salary_ranges", [])),
        "dataset_evidence": dataset_evidence,
        "representative_jobs_source": representative_jobs_source,
        "representative_jobs": representative_jobs,
        "exact_title_representative_jobs": exact_representative_jobs,
        "normalized_cluster_representative_jobs": cluster_representative_jobs,
        "fallback_inferred_representative_jobs": fallback_representative_jobs,
    }


def refresh_templates_with_evidence(
    templates: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    refreshed: list[dict[str, Any]] = []
    for template in templates:
        payload = build_template_evidence_payload(template, rows)
        refreshed.append(
            {
                **dict(template),
                "dataset_job_count": payload["dataset_job_count"],
                "typical_industries": payload["typical_industries"],
                "typical_cities": payload["typical_cities"],
                "sample_salary_ranges": payload["sample_salary_ranges"],
                "dataset_evidence": payload["dataset_evidence"],
            }
        )
    return refreshed


def render_role_profile_templates_markdown(templates: list[dict[str, Any]]) -> str:
    lines = ["# 首批岗位画像模板", ""]
    for template in templates:
        lines.extend(
            [
                f"## {template.get('canonical_title', '未命名岗位')}",
                f"- 原始岗位名：{template.get('source_title', '')}",
                f"- 岗位族：{template.get('role_family', '综合')}",
                f"- 数据样本量：{template.get('dataset_job_count', 0)}",
                f"- 岗位说明：{template.get('summary', '')}",
                f"- 核心技能：{'、'.join(template.get('core_skills', [])) or '暂无'}",
                f"- 加分技能：{'、'.join(template.get('preferred_skills', [])) or '暂无'}",
                f"- 软技能：{'、'.join(template.get('soft_skills', [])) or '暂无'}",
                f"- 证书要求：{'、'.join(template.get('certificates', [])) or '暂无'}",
                f"- 学历要求：{template.get('education_requirement', '未说明')}",
                f"- 经验要求：{template.get('experience_requirement', '未说明')}",
                f"- 典型行业：{'、'.join(template.get('typical_industries', [])) or '暂无'}",
                f"- 典型城市：{'、'.join(template.get('typical_cities', [])) or '暂无'}",
                f"- 常见薪资：{'、'.join(template.get('sample_salary_ranges', [])) or '暂无'}",
                f"- 纵向成长路径：{' -> '.join(template.get('vertical_growth_path', [])) or '暂无'}",
                f"- 横向转岗路径：{'、'.join(template.get('transition_paths', [])) or '暂无'}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"
