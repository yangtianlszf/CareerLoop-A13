from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import xlrd
except Exception:  # pragma: no cover - optional dependency fallback
    xlrd = None

from a13_starter.src.extractors import build_job_profile


EXPECTED_HEADERS = [
    "岗位名称",
    "地址",
    "薪资范围",
    "公司名称",
    "所属行业",
    "公司规模",
    "公司类型",
    "岗位编码",
    "岗位详情",
    "更新日期",
    "公司详情",
    "岗位来源地址",
]


def _normalize_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = text.replace("\r", "\n")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERATED_DIR = PROJECT_ROOT / "a13_starter" / "generated"
JOB_PROFILES_PATH = GENERATED_DIR / "job_profiles.jsonl"
JD_ROWS_PATH = GENERATED_DIR / "jd_rows.json"


def _sheet_headers(sheet: Any) -> list[str]:
    return [_normalize_cell(cell) for cell in sheet.row_values(0)]


def load_job_rows(xls_path: str | Path) -> list[dict[str, str]]:
    if xlrd is None:
        cached_rows = _load_cached_job_rows()
        if cached_rows:
            return cached_rows
        raise RuntimeError(
            "未安装 xlrd，且本地没有可回退的岗位缓存数据。"
            "请先安装 xlrd，或保留 generated/job_profiles.jsonl 与 generated/jd_rows.json。"
        )

    workbook = xlrd.open_workbook(str(xls_path))
    sheet = workbook.sheet_by_index(0)
    headers = _sheet_headers(sheet)
    rows: list[dict[str, str]] = []

    for row_index in range(1, sheet.nrows):
        values = [_normalize_cell(value) for value in sheet.row_values(row_index)]
        row = {headers[col]: values[col] if col < len(values) else "" for col in range(len(headers))}
        if any(row.values()):
            rows.append(row)
    return rows


def _load_cached_job_rows() -> list[dict[str, str]]:
    if JOB_PROFILES_PATH.exists():
        rows: list[dict[str, str]] = []
        with JOB_PROFILES_PATH.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                source = item.get("source")
                if isinstance(source, dict) and source:
                    rows.append({str(key): _normalize_cell(value) for key, value in source.items()})
        if rows:
            return rows

    if JD_ROWS_PATH.exists():
        raw_rows = json.loads(JD_ROWS_PATH.read_text(encoding="utf-8"))
        if isinstance(raw_rows, list):
            return [
                {str(key): _normalize_cell(value) for key, value in row.items()}
                for row in raw_rows
                if isinstance(row, dict) and row
            ]

    return []


def build_job_text_from_row(row: dict[str, str]) -> str:
    parts = [
        row.get("岗位名称", ""),
        f"工作地点：{row.get('地址', '')}",
        f"薪资：{row.get('薪资范围', '')}",
        f"公司名称：{row.get('公司名称', '')}",
        f"所属行业：{row.get('所属行业', '')}",
        f"公司规模：{row.get('公司规模', '')}",
        f"公司类型：{row.get('公司类型', '')}",
        "岗位详情：",
        row.get("岗位详情", ""),
        "公司详情：",
        row.get("公司详情", ""),
    ]
    return "\n".join(part for part in parts if part and part.strip())


def profile_job_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    profiled_rows: list[dict[str, object]] = []
    for row in rows:
        profile = build_job_profile(build_job_text_from_row(row))
        profiled_rows.append(
            {
                "source": row,
                "profile": profile.to_dict(),
            }
        )
    return profiled_rows


def build_dataset_summary(profiled_rows: list[dict[str, object]]) -> dict[str, object]:
    title_counter = Counter()
    industry_counter = Counter()
    skill_counter = Counter()
    city_counter = Counter()

    for item in profiled_rows:
        source = item["source"]
        profile = item["profile"]
        title_counter.update([source.get("岗位名称", "")])
        industry_counter.update(
            [part.strip() for part in source.get("所属行业", "").split(",") if part.strip()]
        )
        skill_counter.update(profile.get("required_skills", []))
        if profile.get("city"):
            city_counter.update([profile["city"]])

    return {
        "job_count": len(profiled_rows),
        "top_job_titles": title_counter.most_common(20),
        "top_industries": industry_counter.most_common(20),
        "top_skills": skill_counter.most_common(20),
        "top_cities": city_counter.most_common(20),
    }


def write_json(path: str | Path, data: object) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: str | Path, rows: list[dict[str, object]]) -> None:
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
