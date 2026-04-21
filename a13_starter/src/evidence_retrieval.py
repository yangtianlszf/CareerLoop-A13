from __future__ import annotations

import re
from typing import Any

from a13_starter.src.jd_search import load_all_job_rows, load_role_templates
from a13_starter.src.models import StudentProfile
from a13_starter.src.skill_taxonomy import expand_skill_list, normalize_skill_alias
from a13_starter.src.template_evidence_regenerator import select_template_rows


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(cleaned)
    return result


def _lowered_set(items: list[str]) -> set[str]:
    return {str(item).strip().lower() for item in items if str(item).strip()}


def _split_sentences(text: str, max_len: int = 110) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", str(text or "").replace("\r", "\n")).strip()
    if not normalized:
        return []

    raw_parts = [
        part.strip()
        for part in re.split(r"[\n。！？；;]", normalized)
        if part and part.strip()
    ]
    chunks: list[str] = []
    current = ""
    for part in raw_parts:
        if len(current) + len(part) + 1 <= max_len:
            current = f"{current}；{part}".strip("；") if current else part
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks


def _build_query_terms(student: StudentProfile, primary_match: dict[str, Any], template: dict[str, Any] | None) -> list[str]:
    terms: list[str] = []
    terms.append(str(primary_match.get("role_title", "")))
    if template:
        terms.append(str(template.get("source_title", "")))
        terms.extend(expand_skill_list(template.get("core_skills", [])[:5], max_per_skill=2))
        terms.extend(expand_skill_list(template.get("preferred_skills", [])[:3], max_per_skill=2))
    terms.extend(student.target_roles[:2])
    terms.extend(expand_skill_list(student.skills[:6], max_per_skill=2))
    terms.extend(expand_skill_list(primary_match.get("shared_skills", [])[:4], max_per_skill=2))
    terms.extend(expand_skill_list(primary_match.get("missing_skills", [])[:3], max_per_skill=2))
    if student.city_preference:
        terms.append(student.city_preference)
    return _dedupe_keep_order(terms)


def _template_chunk(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_type": "template",
        "source_title": str(template.get("canonical_title", "")),
        "job_title": str(template.get("source_title", "")),
        "company_name": "岗位模板",
        "city": "模板汇总",
        "industry": "、".join(str(item) for item in template.get("typical_industries", [])[:3]),
        "text": (
            f"{template.get('summary', '')} 核心技能：{'、'.join(template.get('core_skills', [])[:6])}"
            f"。软技能：{'、'.join(template.get('soft_skills', [])[:4])}"
            f"。成长路径：{'、'.join(template.get('vertical_growth_path', [])[:3])}"
        ).strip(),
        "job_code": "template",
        "job_url": "",
    }


def _jd_chunks(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for row in rows:
        header = (
            f"{row.get('岗位名称', '')}｜{row.get('公司名称', '')}｜{row.get('地址', '')}"
            f"｜{row.get('薪资范围', '')}"
        ).strip("｜")
        for sentence in _split_sentences(row.get("岗位详情", "")):
            chunks.append(
                {
                    "source_type": "jd_detail",
                    "source_title": row.get("岗位名称", ""),
                    "job_title": row.get("岗位名称", ""),
                    "company_name": row.get("公司名称", ""),
                    "city": row.get("地址", ""),
                    "industry": row.get("所属行业", ""),
                    "text": f"{header}：{sentence}",
                    "job_code": row.get("岗位编码", ""),
                    "job_url": row.get("岗位来源地址", ""),
                }
            )
        for sentence in _split_sentences(row.get("公司详情", ""), max_len=90)[:2]:
            chunks.append(
                {
                    "source_type": "company_context",
                    "source_title": row.get("岗位名称", ""),
                    "job_title": row.get("岗位名称", ""),
                    "company_name": row.get("公司名称", ""),
                    "city": row.get("地址", ""),
                    "industry": row.get("所属行业", ""),
                    "text": f"{row.get('公司名称', '')} 背景：{sentence}",
                    "job_code": row.get("岗位编码", ""),
                    "job_url": row.get("岗位来源地址", ""),
                }
            )
    return chunks


def _score_chunk(
    chunk: dict[str, Any],
    query_terms: list[str],
    primary_match: dict[str, Any],
    template: dict[str, Any] | None,
) -> tuple[int, list[str]]:
    text = " ".join(
        [
            str(chunk.get("source_title", "")),
            str(chunk.get("job_title", "")),
            str(chunk.get("company_name", "")),
            str(chunk.get("city", "")),
            str(chunk.get("industry", "")),
            str(chunk.get("text", "")),
        ]
    ).lower()
    source_title = str(chunk.get("source_title", "")).strip()
    role_title = str(primary_match.get("role_title", "")).strip()
    template_source = str(template.get("source_title", "")).strip() if template else ""
    core_skills = {str(item).lower() for item in primary_match.get("core_skills", [])}
    shared_skills = {str(item).lower() for item in primary_match.get("shared_skills", [])}
    missing_skills = {str(item).lower() for item in primary_match.get("missing_skills", [])}

    score = 0
    matched_terms: list[str] = []
    for term in query_terms:
        lowered = term.lower()
        if lowered and lowered in text:
            matched_terms.append(term)
            if term == role_title:
                score += 60
            elif term == template_source:
                score += 45
            elif lowered in core_skills:
                score += 24
            elif lowered in shared_skills:
                score += 18
            elif lowered in missing_skills:
                score += 14
            else:
                score += 8

    if template_source and source_title == template_source:
        score += 28
    if role_title and role_title in source_title:
        score += 24
    if chunk.get("source_type") == "template":
        score += 26
    if chunk.get("source_type") == "jd_detail":
        score += 12
    if len(matched_terms) >= 3:
        score += 12
    return score, _dedupe_keep_order(matched_terms)


def build_grounded_evidence_bundle(
    student: StudentProfile,
    primary_match: dict[str, Any],
    *,
    limit: int = 5,
) -> dict[str, Any]:
    role_title = str(primary_match.get("role_title", "")).strip()
    templates = load_role_templates()
    template = next((item for item in templates if item.get("canonical_title") == role_title), None)
    query_terms = _build_query_terms(student, primary_match, template)

    source_title = str(template.get("source_title", "")).strip() if template else ""
    all_rows = load_all_job_rows()
    matching_rows = select_template_rows(template, all_rows) if template else []
    if not matching_rows:
        matching_rows = all_rows

    jd_candidates = _jd_chunks(matching_rows)
    jd_scored: list[tuple[int, dict[str, Any], list[str]]] = []
    for chunk in jd_candidates:
        score, matched_terms = _score_chunk(chunk, query_terms, primary_match, template)
        if score <= 0:
            continue
        jd_scored.append((score, chunk, matched_terms))
    jd_scored.sort(key=lambda item: item[0], reverse=True)

    template_scored: list[tuple[int, dict[str, Any], list[str]]] = []
    if template:
        template_chunk = _template_chunk(template)
        score, matched_terms = _score_chunk(template_chunk, query_terms, primary_match, template)
        if score > 0:
            template_scored.append((score, template_chunk, matched_terms))

    # 证据卡片优先展示真实官方 JD 片段；只有没有可用 JD 证据时，才回退到岗位模板摘要。
    scored = jd_scored if jd_scored else template_scored

    evidence_items: list[dict[str, Any]] = []
    for index, (score, chunk, matched_terms) in enumerate(scored[: max(1, limit)], start=1):
        evidence_items.append(
            {
                "citation_id": f"[E{index}]",
                "score": score,
                "source_type": chunk.get("source_type"),
                "source_title": chunk.get("source_title"),
                "job_title": chunk.get("job_title"),
                "company_name": chunk.get("company_name"),
                "city": chunk.get("city"),
                "industry": chunk.get("industry"),
                "snippet": chunk.get("text"),
                "matched_terms": matched_terms,
                "job_code": chunk.get("job_code"),
                "job_url": chunk.get("job_url"),
            }
        )

    unique_terms = _dedupe_keep_order(
        [term for item in evidence_items for term in item.get("matched_terms", [])]
    )
    requirement_terms = _dedupe_keep_order(
        [normalize_skill_alias(str(item)) for item in primary_match.get("core_skills", [])[:6]]
    )
    if not requirement_terms:
        requirement_terms = _dedupe_keep_order(
            [
                *[normalize_skill_alias(str(item)) for item in primary_match.get("shared_skills", [])[:6]],
                *[normalize_skill_alias(str(item)) for item in primary_match.get("missing_skills", [])[:6]],
            ]
        )

    student_hit_terms = _dedupe_keep_order(
        [
            normalize_skill_alias(str(item))
            for item in primary_match.get("shared_skills", [])
            if normalize_skill_alias(str(item))
        ]
    )
    student_gap_terms = _dedupe_keep_order(
        [
            normalize_skill_alias(str(item))
            for item in primary_match.get("missing_skills", [])
            if normalize_skill_alias(str(item))
        ]
    )

    unique_term_set = _lowered_set(unique_terms)
    hit_terms = [term for term in requirement_terms if term.lower() in unique_term_set]
    evidence_hit_rate = int(len(hit_terms) / max(1, len(requirement_terms)) * 100)
    student_match_rate = int(len(student_hit_terms) / max(1, len(requirement_terms)) * 100)
    source_count = len({item.get("job_code") or item.get("source_title") for item in evidence_items})
    retrieval_mode = "template+jd" if template and matching_rows else "global-jd"
    matched_copy = "、".join(student_hit_terms[:4]) or "暂无已明确命中的核心要求"
    gap_copy = "、".join(student_gap_terms[:3]) or "当前没有明显待补项"
    summary = (
        f"围绕 {role_title} 从 {source_count} 个证据源检索出 {len(evidence_items)} 条高相关片段，"
        f"官方样本稳定支持 {'、'.join(hit_terms[:5]) or role_title} 等岗位要求；"
        f"你当前已具备 {matched_copy}，仍需补强 {gap_copy}。"
    )

    return {
        "role_title": role_title,
        "retrieval_mode": retrieval_mode,
        "query_terms": query_terms,
        "summary": summary,
        "source_title": source_title,
        "target_terms": requirement_terms,
        "requirement_terms": requirement_terms,
        "hit_terms": hit_terms,
        "student_hit_terms": student_hit_terms,
        "student_gap_terms": student_gap_terms,
        "student_match_rate": student_match_rate,
        "evidence_hit_rate": evidence_hit_rate,
        "items": evidence_items,
    }
