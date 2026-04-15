from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from a13_starter.src.dataset import build_job_text_from_row, load_cleaned_job_rows
from a13_starter.src.extractors import build_job_profile
from a13_starter.src.paths import resolve_project_root
from a13_starter.src.role_normalizer import clean_text, normalize_job_title
from a13_starter.src.role_template_specs import ensure_role_templates
from a13_starter.src.template_evidence_regenerator import build_template_evidence_payload


PROJECT_ROOT = resolve_project_root(__file__, 2)
JD_XLS_PATH = PROJECT_ROOT / "A13_官方资料" / "A13-JD采样数据.xls"
ROLE_TEMPLATES_PATH = PROJECT_ROOT / "a13_starter" / "generated" / "role_profile_templates.json"

_SECTION_TITLE_MARKERS = (
    "工程师",
    "开发",
    "测试",
    "分析师",
    "实施",
    "支持",
    "售前",
    "运营",
    "产品",
    "经理",
    "算法",
    "大模型",
    "前端",
    "后端",
    "java",
    "python",
    "c/c++",
    "c++",
    "cpp",
    "web",
    "嵌入式",
)

_GENERIC_SECTION_LABELS = {
    "岗位职责",
    "任职要求",
    "职位描述",
    "职位要求",
    "岗位要求",
    "职责",
    "要求",
    "公司福利",
    "福利",
    "工作职责",
    "任职资格",
    "任职条件",
}


@lru_cache(maxsize=1)
def load_all_job_rows() -> list[dict[str, str]]:
    try:
        return load_cleaned_job_rows(JD_XLS_PATH)
    except Exception:
        return []


@lru_cache(maxsize=1)
def load_role_templates() -> list[dict[str, Any]]:
    if not ROLE_TEMPLATES_PATH.exists():
        return ensure_role_templates([])
    return ensure_role_templates(json.loads(ROLE_TEMPLATES_PATH.read_text(encoding="utf-8")))


def _clean_search_text(value: Any) -> str:
    return clean_text(value).lower()


def _extract_inline_heading(line: str) -> tuple[str, str] | None:
    cleaned = clean_text(line)
    if not cleaned:
        return None
    if re.match(r"^[0-9一二三四五六七八九十]+[、.．)）]", cleaned):
        return None

    head = cleaned
    tail = ""
    if "：" in cleaned:
        head, tail = cleaned.split("：", 1)
    elif ":" in cleaned:
        head, tail = cleaned.split(":", 1)

    heading = head.strip(" -").strip()
    body = tail.strip()
    lowered_heading = heading.lower()
    if not heading or len(heading) > 28:
        return None
    if heading in _GENERIC_SECTION_LABELS or lowered_heading in {label.lower() for label in _GENERIC_SECTION_LABELS}:
        return None
    if any(marker in lowered_heading for marker in _SECTION_TITLE_MARKERS):
        return heading, body
    return None


def _extract_job_search_sections(row: dict[str, Any]) -> list[dict[str, str]]:
    source_title = clean_text(row.get("岗位名称", ""))
    detail = clean_text(row.get("岗位详情", ""))
    if not detail:
        return [{"section_title": source_title or "未命名岗位", "section_detail": ""}]

    sections: list[dict[str, str]] = []
    current_title = ""
    current_lines: list[str] = []
    saw_explicit_section = False

    for raw_line in detail.splitlines():
        line = clean_text(raw_line)
        if not line:
            continue
        heading = _extract_inline_heading(line)
        if heading:
            saw_explicit_section = True
            if current_title:
                sections.append(
                    {
                        "section_title": current_title,
                        "section_detail": "\n".join(current_lines).strip(),
                    }
                )
            current_title = heading[0]
            current_lines = [heading[1]] if heading[1] else []
            continue
        if current_title:
            current_lines.append(line)

    if saw_explicit_section and current_title:
        sections.append(
            {
                "section_title": current_title,
                "section_detail": "\n".join(current_lines).strip(),
            }
        )

    if sections:
        return sections
    return [{"section_title": source_title or "未命名岗位", "section_detail": detail}]


def _score_search_section(
    query: str,
    query_normalized: str,
    row: dict[str, Any],
    section_title: str,
    section_detail: str,
    profile: dict[str, Any],
) -> int:
    source_title = clean_text(row.get("岗位名称", ""))
    industry = clean_text(row.get("所属行业", ""))
    company = clean_text(row.get("公司名称", ""))
    section_title_lower = section_title.lower()
    section_detail_lower = section_detail.lower()
    source_title_lower = source_title.lower()
    row_normalized = clean_text(row.get("_normalized_title", ""))
    section_normalized = normalize_job_title(section_title, detail=section_detail, industry=industry)
    section_normalized_lower = section_normalized.lower()

    score = 0
    if query_normalized and section_normalized_lower == query_normalized:
        score += 120
    if query and query in section_title_lower:
        score += 95
    if query_normalized and query_normalized in section_title_lower:
        score += 80
    if query and query in source_title_lower:
        score += 45
    if query_normalized and row_normalized.lower() == query_normalized:
        score += 42
    if query and query in section_detail_lower:
        score += 18
    if query and query in company.lower():
        score += 20
    if query and query in industry.lower():
        score += 10

    skill_text = " ".join(profile.get("required_skills", []))
    if query and query in skill_text.lower():
        score += 12
    if section_title_lower != source_title_lower and source_title_lower and query not in source_title_lower:
        score += 10
    return score


def search_job_profiles(query: str, limit: int = 12) -> list[dict[str, Any]]:
    keyword = _clean_search_text(query)
    if not keyword:
        return []
    normalized_query = normalize_job_title(str(query or "").strip()).lower()

    scored: list[tuple[int, dict[str, Any], dict[str, Any], dict[str, str]]] = []
    for row in load_all_job_rows():
        for section in _extract_job_search_sections(row):
            section_title = clean_text(section.get("section_title", ""))
            section_detail = clean_text(section.get("section_detail", ""))
            haystack_parts = [
                section_title,
                section_detail,
                row.get("岗位名称", ""),
                row.get("公司名称", ""),
                row.get("所属行业", ""),
                row.get("地址", ""),
            ]
            haystack = " ".join(part for part in haystack_parts if part).lower()
            if keyword not in haystack and (not normalized_query or normalized_query not in haystack):
                continue

            profile = build_job_profile(f"{section_title}\n{section_detail}".strip())
            score = _score_search_section(
                keyword,
                normalized_query,
                row,
                section_title,
                section_detail,
                profile.to_dict(),
            )
            if score <= 0:
                continue
            scored.append((score, row, profile.to_dict(), {"section_title": section_title, "section_detail": section_detail}))

    scored.sort(key=lambda item: item[0], reverse=True)
    results: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for score, row, profile, section in scored:
        if len(results) >= max(1, limit):
            break
        dedupe_key = f"{row.get('岗位编码') or row.get('岗位名称')}|{section.get('section_title', '')}"
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        results.append(
            {
                "score": score,
                "job_title": section.get("section_title") or row.get("岗位名称"),
                "source_title": row.get("岗位名称"),
                "company_name": row.get("公司名称"),
                "city": row.get("地址"),
                "salary_range": row.get("薪资范围"),
                "industry": row.get("所属行业"),
                "job_code": row.get("岗位编码"),
                "job_url": row.get("岗位来源地址"),
                "job_detail": section.get("section_detail") or row.get("岗位详情"),
                "required_skills": profile.get("required_skills", []),
                "soft_skills": profile.get("soft_skills", []),
            }
        )
    return results


def get_template_evidence(role_title: str, limit: int = 6) -> dict[str, Any] | None:
    template = next((item for item in load_role_templates() if item.get("canonical_title") == role_title), None)
    if template is None:
        return None
    return build_template_evidence_payload(template, load_all_job_rows(), limit=limit)
