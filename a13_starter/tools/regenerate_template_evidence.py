from __future__ import annotations

import json
from pathlib import Path

from a13_starter.src.dataset import (
    CLEANED_JD_ROWS_PATH,
    CLEANING_REPORT_PATH,
    GENERATED_DIR,
    JD_ROWS_PATH,
    build_dataset_summary,
    load_job_rows,
    profile_job_rows,
    write_json,
    write_jsonl,
)
from a13_starter.src.jd_search import JD_XLS_PATH, load_role_templates
from a13_starter.src.role_normalizer import build_cleaning_report, clean_job_row
from a13_starter.src.template_evidence_regenerator import (
    refresh_templates_with_evidence,
    render_role_profile_templates_markdown,
)


ROLE_TEMPLATES_PATH = GENERATED_DIR / "role_profile_templates.json"
ROLE_TEMPLATES_MD_PATH = GENERATED_DIR / "role_profile_templates.md"
DATASET_SUMMARY_PATH = GENERATED_DIR / "dataset_summary.json"


def main() -> None:
    raw_rows = load_job_rows(JD_XLS_PATH)
    cleaned_rows = [clean_job_row(row) for row in raw_rows]
    cleaning_report = build_cleaning_report(raw_rows, cleaned_rows)
    profiled_rows = profile_job_rows([{str(key): value for key, value in row.items()} for row in cleaned_rows])
    dataset_summary = build_dataset_summary(profiled_rows)

    templates = load_role_templates()
    refreshed_templates = refresh_templates_with_evidence(templates, cleaned_rows)

    write_json(JD_ROWS_PATH, raw_rows)
    write_json(CLEANED_JD_ROWS_PATH, cleaned_rows)
    write_json(CLEANING_REPORT_PATH, cleaning_report)
    write_json(DATASET_SUMMARY_PATH, dataset_summary)
    write_jsonl(GENERATED_DIR / "job_profiles.jsonl", profiled_rows)
    ROLE_TEMPLATES_PATH.write_text(json.dumps(refreshed_templates, ensure_ascii=False, indent=2), encoding="utf-8")
    ROLE_TEMPLATES_MD_PATH.write_text(
        render_role_profile_templates_markdown(refreshed_templates),
        encoding="utf-8",
    )

    print("模板证据已重生成。")
    print("rows:", len(raw_rows))
    print("templates:", len(refreshed_templates))
    print("wrote:", ROLE_TEMPLATES_PATH)
    print("wrote:", ROLE_TEMPLATES_MD_PATH)
    print("wrote:", CLEANED_JD_ROWS_PATH)
    print("wrote:", CLEANING_REPORT_PATH)
    print("wrote:", DATASET_SUMMARY_PATH)


if __name__ == "__main__":
    main()
