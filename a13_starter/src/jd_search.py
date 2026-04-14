from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from a13_starter.src.dataset import build_job_text_from_row, load_job_rows
from a13_starter.src.extractors import build_job_profile
from a13_starter.src.paths import resolve_project_root
from a13_starter.src.role_template_specs import ensure_role_templates


PROJECT_ROOT = resolve_project_root(__file__, 2)
JD_XLS_PATH = PROJECT_ROOT / "A13_官方资料" / "A13-JD采样数据.xls"
ROLE_TEMPLATES_PATH = PROJECT_ROOT / "a13_starter" / "generated" / "role_profile_templates.json"


@lru_cache(maxsize=1)
def load_all_job_rows() -> list[dict[str, str]]:
    try:
        return load_job_rows(JD_XLS_PATH)
    except Exception:
        return []


@lru_cache(maxsize=1)
def load_role_templates() -> list[dict[str, Any]]:
    if not ROLE_TEMPLATES_PATH.exists():
        return ensure_role_templates([])
    return ensure_role_templates(json.loads(ROLE_TEMPLATES_PATH.read_text(encoding="utf-8")))


def search_job_profiles(query: str, limit: int = 12) -> list[dict[str, Any]]:
    keyword = (query or "").strip().lower()
    if not keyword:
        return []

    scored: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    for row in load_all_job_rows():
        haystack_parts = [
            row.get("岗位名称", ""),
            row.get("公司名称", ""),
            row.get("所属行业", ""),
            row.get("地址", ""),
            row.get("岗位详情", ""),
            row.get("公司详情", ""),
        ]
        haystack = " ".join(part for part in haystack_parts if part).lower()
        if keyword not in haystack:
            continue

        profile = build_job_profile(build_job_text_from_row(row))
        score = 20
        if keyword in row.get("岗位名称", "").lower():
            score += 60
        if keyword in row.get("公司名称", "").lower():
            score += 25
        if keyword in row.get("所属行业", "").lower():
            score += 10
        if keyword in " ".join(profile.required_skills).lower():
            score += 18

        scored.append((score, row, profile.to_dict()))

    scored.sort(key=lambda item: item[0], reverse=True)
    results: list[dict[str, Any]] = []
    for score, row, profile in scored[: max(1, limit)]:
        results.append(
            {
                "score": score,
                "job_title": row.get("岗位名称"),
                "company_name": row.get("公司名称"),
                "city": row.get("地址"),
                "salary_range": row.get("薪资范围"),
                "industry": row.get("所属行业"),
                "job_code": row.get("岗位编码"),
                "job_url": row.get("岗位来源地址"),
                "job_detail": row.get("岗位详情"),
                "required_skills": profile.get("required_skills", []),
                "soft_skills": profile.get("soft_skills", []),
            }
        )
    return results


def get_template_evidence(role_title: str, limit: int = 6) -> dict[str, Any] | None:
    template = next((item for item in load_role_templates() if item.get("canonical_title") == role_title), None)
    if template is None:
        return None

    source_title = str(template.get("source_title", ""))
    matches: list[dict[str, Any]] = []
    for row in load_all_job_rows():
        if str(row.get("岗位名称", "")).strip() != source_title:
            continue
        profile = build_job_profile(build_job_text_from_row(row))
        matches.append(
            {
                "job_title": row.get("岗位名称"),
                "company_name": row.get("公司名称"),
                "city": row.get("地址"),
                "salary_range": row.get("薪资范围"),
                "industry": row.get("所属行业"),
                "job_code": row.get("岗位编码"),
                "job_url": row.get("岗位来源地址"),
                "job_detail": row.get("岗位详情"),
                "required_skills": profile.required_skills,
            }
        )
        if len(matches) >= max(1, limit):
            break

    return {
        "role_title": role_title,
        "source_title": source_title,
        "dataset_job_count": template.get("dataset_job_count", 0),
        "dataset_evidence": template.get("dataset_evidence", {}),
        "representative_jobs": matches,
    }
