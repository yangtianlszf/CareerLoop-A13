from __future__ import annotations

from pathlib import Path

from a13_starter.src.dataset import (
    EXPECTED_HEADERS,
    build_dataset_summary,
    load_job_rows,
    profile_job_rows,
    write_json,
    write_jsonl,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    xls_path = project_root / "A13_官方资料" / "A13-JD采样数据.xls"
    output_dir = project_root / "a13_starter" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    job_rows = load_job_rows(xls_path)
    if not job_rows:
        raise SystemExit("No rows loaded from xls file.")

    headers = list(job_rows[0].keys())
    if headers != EXPECTED_HEADERS:
        print("Warning: headers differ from expected schema.")
        print("Actual headers:", headers)

    profiled_rows = profile_job_rows(job_rows)
    summary = build_dataset_summary(profiled_rows)

    raw_output = output_dir / "jd_rows.json"
    profiles_output = output_dir / "job_profiles.jsonl"
    summary_output = output_dir / "dataset_summary.json"
    sample_output = output_dir / "sample_profile.json"

    write_json(raw_output, job_rows[:100])
    write_jsonl(profiles_output, profiled_rows)
    write_json(summary_output, summary)
    write_json(sample_output, profiled_rows[0])

    print("Loaded rows:", len(job_rows))
    print("Wrote:", raw_output)
    print("Wrote:", profiles_output)
    print("Wrote:", summary_output)
    print("Wrote:", sample_output)
    print("Top titles:", summary["top_job_titles"][:10])
    print("Top skills:", summary["top_skills"][:10])


if __name__ == "__main__":
    main()
