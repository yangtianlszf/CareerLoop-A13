from __future__ import annotations

import argparse
import json
from pathlib import Path

from a13_starter.src.career_planner import build_career_plan, rank_student_against_templates
from a13_starter.src.jd_search import load_role_templates
from a13_starter.src.parser_service import parse_student_profile
from a13_starter.src.report import build_career_report_markdown


def _load_resume_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resume",
        default="a13_starter/samples/student_resume.txt",
        help="Path to the resume text file.",
    )
    parser.add_argument(
        "--parser-mode",
        default="auto",
        choices=["auto", "rule", "llm"],
        help="Choose rule-based parsing, LLM parsing, or auto mode.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    resume_path = project_root / args.resume
    output_dir = project_root / "a13_starter" / "generated"

    templates = load_role_templates()
    resume_text = _load_resume_text(resume_path)
    student, parser_metadata = parse_student_profile(resume_text, parser_mode=args.parser_mode)
    matches = rank_student_against_templates(student, templates)
    career_plan = build_career_plan(student, matches)

    json_output = output_dir / "student_role_matches.json"
    md_output = output_dir / "student_role_matches.md"
    plan_output = output_dir / "career_plan.json"
    report_output = output_dir / "career_plan_report.md"

    json_output.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8")
    md_output.write_text(build_career_report_markdown(student, matches, career_plan), encoding="utf-8")
    plan_output.write_text(json.dumps(career_plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    report_output.write_text(build_career_report_markdown(student, matches, career_plan), encoding="utf-8")

    print("Student:", student.name)
    print("Parser:", parser_metadata.to_dict())
    print("Wrote:", json_output)
    print("Wrote:", md_output)
    print("Wrote:", plan_output)
    print("Wrote:", report_output)
    print("Top 5 matches:")
    for item in matches[:5]:
        print("-", item["role_title"], item["score"])


if __name__ == "__main__":
    main()
