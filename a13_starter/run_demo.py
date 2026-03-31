from pathlib import Path

from a13_starter.src.matcher import match_student_to_job
from a13_starter.src.report import build_report_markdown
from a13_starter.src.parser_service import parse_job_profile, parse_student_profile


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    sample_dir = base_dir / "samples"

    job_text = read_text_file(sample_dir / "job_backend_engineer.txt")
    resume_text = read_text_file(sample_dir / "student_resume.txt")

    job_profile, job_parser = parse_job_profile(job_text, parser_mode="auto")
    student_profile, student_parser = parse_student_profile(resume_text, parser_mode="auto")
    match_result = match_student_to_job(student_profile, job_profile)
    report = build_report_markdown(student_profile, job_profile, match_result)

    print("=" * 80)
    print("PARSER INFO")
    print("=" * 80)
    print("student:", student_parser.to_dict())
    print("job:", job_parser.to_dict())
    print()

    print("=" * 80)
    print("JOB PROFILE")
    print("=" * 80)
    print(job_profile.to_pretty_json())
    print()

    print("=" * 80)
    print("STUDENT PROFILE")
    print("=" * 80)
    print(student_profile.to_pretty_json())
    print()

    print("=" * 80)
    print("MATCH RESULT")
    print("=" * 80)
    print(match_result.to_pretty_json())
    print()

    print("=" * 80)
    print("REPORT")
    print("=" * 80)
    print(report)


if __name__ == "__main__":
    main()
