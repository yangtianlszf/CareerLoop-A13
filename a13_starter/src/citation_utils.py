from __future__ import annotations

import re
from typing import Any


def build_term_citation_map(evidence_bundle: dict[str, Any] | None) -> dict[str, list[str]]:
    term_map: dict[str, list[str]] = {}
    for item in (evidence_bundle or {}).get("items", []):
        citation = str(item.get("citation_id", "")).strip()
        if not citation:
            continue
        for raw_term in item.get("matched_terms", []) or []:
            term = str(raw_term).strip()
            if not term:
                continue
            bucket = term_map.setdefault(term.lower(), [])
            if citation not in bucket:
                bucket.append(citation)
    role_title = str((evidence_bundle or {}).get("role_title", "")).strip()
    if role_title:
        role_key = role_title.lower()
        citations = term_map.setdefault(role_key, [])
        if not citations:
            first_citation = str(((evidence_bundle or {}).get("items", [{}])[0] or {}).get("citation_id", "")).strip()
            if first_citation:
                citations.append(first_citation)
    return term_map


def annotate_text_with_citations(
    text: str | None,
    evidence_bundle: dict[str, Any] | None,
    *,
    preferred_terms: list[str] | None = None,
    max_annotations: int = 3,
) -> str:
    source = str(text or "").strip()
    if not source:
        return ""

    term_map = build_term_citation_map(evidence_bundle)
    if not term_map:
        return source

    ordered_terms = preferred_terms or []
    if not ordered_terms:
        ordered_terms = list((evidence_bundle or {}).get("target_terms", [])) + list(term_map.keys())

    unique_terms: list[str] = []
    seen: set[str] = set()
    for term in ordered_terms:
        cleaned = str(term).strip()
        lowered = cleaned.lower()
        if cleaned and lowered not in seen:
            seen.add(lowered)
            unique_terms.append(cleaned)

    result = source
    annotated_count = 0
    for term in sorted(unique_terms, key=len, reverse=True):
        if annotated_count >= max_annotations:
            break
        citations = term_map.get(term.lower())
        if not citations:
            continue
        pattern = re.compile(rf"(?<!\w)({re.escape(term)})(?!\s*\[E\d+\])", re.IGNORECASE)
        replacement = f"\\1 {' '.join(citations[:2])}"
        updated, count = pattern.subn(replacement, result, count=1)
        if count:
            result = updated
            annotated_count += 1
    return result
