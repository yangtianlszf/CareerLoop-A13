from __future__ import annotations

import json
import mimetypes
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from email.parser import BytesParser
from email.policy import default
from urllib.parse import parse_qs, quote, urlparse

from a13_starter.src.career_planner import apply_agent_answers, build_career_plan, rank_student_against_templates
from a13_starter.src.analysis_storage import (
    build_school_dashboard,
    find_previous_analysis,
    get_analysis,
    init_storage,
    list_reviews,
    list_analyses,
    save_review,
    save_analysis,
)
from a13_starter.src.benchmark import run_benchmark
from a13_starter.src.citation_utils import annotate_text_with_citations
from a13_starter.src.jd_search import get_template_evidence, load_role_templates, search_job_profiles
from a13_starter.src.matcher import match_student_to_job
from a13_starter.src.models import JobProfile
from a13_starter.src.parser_service import parse_job_profile, parse_student_profile
from a13_starter.src.report_exports import build_report_export_bundle, markdown_to_html
from a13_starter.src.report import build_career_report_markdown
from a13_starter.src.resume_file_parser import ResumeFileParseError, parse_resume_file
from a13_starter.src.system_checks import run_environment_checks
from a13_starter.src.paths import resolve_project_root


PROJECT_ROOT = resolve_project_root(__file__, 1)
TEMPLATES_PATH = PROJECT_ROOT / "a13_starter" / "generated" / "role_profile_templates.json"
WEB_DIR = PROJECT_ROOT / "a13_starter" / "web"
SAMPLE_RESUME_PATH = PROJECT_ROOT / "a13_starter" / "samples" / "student_resume.txt"
SAMPLES_DIR = PROJECT_ROOT / "a13_starter" / "samples"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def _load_templates() -> list[dict[str, object]]:
    return load_role_templates()


def _template_to_job_profile(template: dict[str, object]) -> JobProfile:
    return JobProfile(
        title=str(template.get("canonical_title", "")),
        raw_text=str(template.get("summary", "")),
        required_skills=list(template.get("core_skills", [])),
        soft_skills=list(template.get("soft_skills", [])),
        certificates=list(template.get("certificates", [])),
        education_requirement=str(template.get("education_requirement", "")),
        experience_requirement=str(template.get("experience_requirement", "")),
        city=None,
        salary_range=None,
        growth_path=list(template.get("vertical_growth_path", [])),
    )


def _sample_resume_catalog() -> list[dict[str, str]]:
    return [
        {
            "name": "demo_resume_backend.txt",
            "label": "后端开发样例",
            "description": "更适合展示后端开发、Java 开发方向的推荐结果。",
        },
        {
            "name": "demo_resume_implementation.txt",
            "label": "实施交付样例",
            "description": "更适合展示实施工程师、技术支持方向的推荐结果。",
        },
        {
            "name": "demo_resume_frontend.txt",
            "label": "前端产品样例",
            "description": "更适合展示前端、交互、产品协同方向的推荐结果。",
        },
        {
            "name": "student_resume.txt",
            "label": "基础学生样例",
            "description": "默认的基础演示样例，适合做系统联调。",
        },
        {
            "name": "demo_resume_data_analyst.txt",
            "label": "数据分析样例",
            "description": "更适合展示数据分析、业务洞察方向的推荐结果。",
        },
        {
            "name": "demo_resume_operations.txt",
            "label": "运营增长样例",
            "description": "更适合展示内容运营、用户增长方向的推荐结果。",
        },
        {
            "name": "demo_resume_testdev.txt",
            "label": "测试开发样例",
            "description": "更适合展示自动化测试、质量平台方向的推荐结果。",
        },
    ]


def _resolve_sample_resume(name: str | None) -> Path:
    if not name:
        return SAMPLE_RESUME_PATH

    allowed = {item["name"] for item in _sample_resume_catalog()}
    if name not in allowed:
        return SAMPLE_RESUME_PATH

    path = SAMPLES_DIR / name
    if not path.exists():
        return SAMPLE_RESUME_PATH
    return path


def _normalize_agent_answers(raw_answers: object) -> dict[str, str]:
    if not isinstance(raw_answers, dict):
        return {}
    normalized: dict[str, str] = {}
    for key, value in raw_answers.items():
        clean_key = str(key).strip()
        clean_value = str(value).strip()
        if clean_key and clean_value:
            normalized[clean_key] = clean_value
    return normalized


def _normalize_self_assessment(raw_answers: object) -> dict[str, int]:
    if not isinstance(raw_answers, dict):
        return {}
    normalized: dict[str, int] = {}
    for key, value in raw_answers.items():
        clean_key = str(key).strip()
        if not clean_key:
            continue
        try:
            score = int(value)
        except (TypeError, ValueError):
            continue
        normalized[clean_key] = max(0, min(score, 2))
    return normalized


def _safe_export_stem(value: str | None, fallback: str = "career_plan_report") -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", str(value or "").strip())
    text = text.strip("._-")
    return text or fallback


def _attach_evidence_citations(matches: list[dict[str, object]], career_plan: dict[str, object]) -> None:
    if not matches:
        return
    evidence_bundle = career_plan.get("evidence_bundle") if isinstance(career_plan, dict) else {}
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            continue
        preferred_terms = [
            str(match.get("role_title", "")),
            *[str(item) for item in match.get("shared_skills", [])[:3]],
            *[str(item) for item in match.get("missing_skills", [])[:2]],
        ]
        explanation = annotate_text_with_citations(
            str(match.get("explanation", "")),
            evidence_bundle if index == 0 else {},
            preferred_terms=preferred_terms,
            max_annotations=3,
        )
        match["explanation"] = explanation


class A13RequestHandler(BaseHTTPRequestHandler):
    server_version = "A13Starter/0.1"

    def _send_response(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_response(status, encoded, "application/json; charset=utf-8")

    def _send_file(self, filename: str, payload: bytes, content_type: str) -> None:
        ascii_fallback = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._") or "download"
        quoted_name = quote(filename)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header(
            "Content-Disposition",
            f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quoted_name}",
        )
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_report_export(self, *, markdown_text: str, title: str, base_name: str, export_format: str) -> None:
        bundle = build_report_export_bundle(markdown_text, title=title)
        if export_format == "markdown":
            self._send_file(
                f"{base_name}.md",
                str(bundle["markdown"]).encode("utf-8"),
                "text/markdown; charset=utf-8",
            )
            return
        if export_format == "html":
            self._send_file(
                f"{base_name}.html",
                str(bundle["html"]).encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        if export_format == "docx":
            self._send_file(
                f"{base_name}.docx",
                bytes(bundle["docx"]),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            return
        if export_format == "pdf":
            self._send_file(
                f"{base_name}.pdf",
                bytes(bundle["pdf"]),
                "application/pdf",
            )
            return
        if export_format == "print":
            self._send_response(HTTPStatus.OK, str(bundle["html"]).encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Unsupported export format"})

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _read_multipart_form_data(self) -> tuple[dict[str, str], dict[str, dict[str, object]]]:
        content_type = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", "0"))
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("Content-Type must be multipart/form-data")
        if length <= 0:
            raise ValueError("Empty upload body")
        if length > MAX_UPLOAD_BYTES:
            raise ValueError("上传文件过大，请控制在 5MB 以内。")

        raw = self.rfile.read(length)
        payload = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + raw
        message = BytesParser(policy=default).parsebytes(payload)

        fields: dict[str, str] = {}
        files: dict[str, dict[str, object]] = {}
        for part in message.iter_parts():
            name = part.get_param("name", header="Content-Disposition")
            if not name:
                continue
            filename = part.get_filename()
            content = part.get_payload(decode=True) or b""
            if filename:
                files[name] = {
                    "filename": filename,
                    "content": content,
                    "content_type": part.get_content_type(),
                }
            else:
                charset = part.get_content_charset() or "utf-8"
                fields[name] = content.decode(charset, errors="ignore")
        return fields, files

    def _serve_static_file(self, relative_path: str) -> None:
        file_path = WEB_DIR / relative_path
        if not file_path.exists() or not file_path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        self._send_response(
            HTTPStatus.OK,
            file_path.read_bytes(),
            content_type or "application/octet-stream",
        )

    def do_OPTIONS(self) -> None:
        self._send_json(HTTPStatus.OK, {"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self._serve_static_file("index.html")
            return

        if path == "/app.js":
            self._serve_static_file("app.js")
            return

        if path == "/styles.css":
            self._serve_static_file("styles.css")
            return

        if path == "/health":
            self._send_json(HTTPStatus.OK, {"ok": True})
            return

        if path == "/api/demo-resumes":
            self._send_json(HTTPStatus.OK, {"samples": _sample_resume_catalog()})
            return

        if path == "/api/demo-resume":
            sample_name = query.get("name", [None])[0]
            sample_path = _resolve_sample_resume(sample_name)
            self._send_json(
                HTTPStatus.OK,
                {
                    "sample_name": sample_path.name,
                    "resume_text": sample_path.read_text(encoding="utf-8").strip(),
                },
            )
            return

        if path == "/api/role-templates":
            self._send_json(HTTPStatus.OK, {"templates": _load_templates()})
            return

        if path == "/api/system-check":
            self._send_json(HTTPStatus.OK, run_environment_checks())
            return

        if path == "/api/jd-search":
            query_text = query.get("q", [""])[0]
            limit = int(query.get("limit", ["12"])[0])
            self._send_json(
                HTTPStatus.OK,
                {
                    "query": query_text,
                    "items": search_job_profiles(query_text, limit=limit),
                },
            )
            return

        if path == "/api/template-evidence":
            role_title = query.get("role_title", [""])[0]
            if not role_title:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "role_title is required"})
                return
            evidence = get_template_evidence(role_title)
            if evidence is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Role evidence not found"})
                return
            self._send_json(HTTPStatus.OK, evidence)
            return

        if path == "/api/history":
            self._send_json(HTTPStatus.OK, {"items": list_analyses(limit=30)})
            return

        if path == "/api/reviews":
            analysis_id = query.get("analysis_id", [None])[0]
            if analysis_id is None:
                self._send_json(HTTPStatus.OK, {"items": list_reviews(limit=50)})
                return
            try:
                parsed_id = int(analysis_id)
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid analysis id"})
                return
            self._send_json(HTTPStatus.OK, {"items": list_reviews(analysis_id=parsed_id, limit=50)})
            return

        if path == "/api/school-dashboard":
            limit = int(query.get("limit", ["80"])[0])
            self._send_json(HTTPStatus.OK, build_school_dashboard(limit=limit))
            return

        if path == "/api/benchmark":
            parser_mode = query.get("parser_mode", ["rule"])[0]
            self._send_json(HTTPStatus.OK, run_benchmark(parser_mode=parser_mode))
            return

        if path.startswith("/api/history/"):
            try:
                analysis_id = int(path.rsplit("/", 1)[-1])
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid analysis id"})
                return
            analysis = get_analysis(analysis_id)
            if analysis is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Analysis not found"})
                return
            analysis["reviews"] = list_reviews(analysis_id=analysis_id, limit=20)
            self._send_json(HTTPStatus.OK, analysis)
            return

        if path.startswith("/api/export/analysis/"):
            try:
                analysis_id = int(path.rsplit("/", 1)[-1])
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid analysis id"})
                return
            analysis = get_analysis(analysis_id)
            if analysis is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Analysis not found"})
                return

            export_format = query.get("format", ["markdown"])[0].lower()
            title = f"{analysis['student_profile'].get('name', '学生')}_职业规划报告"
            self._send_report_export(
                markdown_text=str(analysis["report_markdown"]),
                title=title,
                base_name=f"analysis_{analysis_id}",
                export_format=export_format,
            )
            return

        if path.startswith("/print-report/"):
            try:
                analysis_id = int(path.rsplit("/", 1)[-1])
            except ValueError:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid analysis id"})
                return
            analysis = get_analysis(analysis_id)
            if analysis is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Analysis not found"})
                return
            title = f"{analysis['student_profile'].get('name', '学生')}_职业规划报告"
            printable_html = markdown_to_html(analysis["report_markdown"], title=title)
            self._send_response(HTTPStatus.OK, printable_html.encode("utf-8"), "text/html; charset=utf-8")
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path == "/api/upload-resume-file":
            try:
                _, files = self._read_multipart_form_data()
            except ValueError as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return

            resume_file = files.get("resume_file")
            if not resume_file:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "resume_file is required"})
                return

            filename = str(resume_file.get("filename", "resume.txt"))
            content = resume_file.get("content", b"")
            if not isinstance(content, bytes):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid file content"})
                return

            try:
                resume_text = parse_resume_file(filename, content)
            except ResumeFileParseError as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return

            self._send_json(
                HTTPStatus.OK,
                {
                    "file_name": filename,
                    "resume_text": resume_text,
                    "message": f"已成功解析文件：{filename}",
                },
            )
            return

        try:
            body = self._read_json()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return

        try:
            self._handle_json_post(body)
        except Exception as error:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {
                    "error": str(error),
                    "path": self.path,
                },
            )

    def _handle_json_post(self, body: dict[str, object]) -> None:
        if self.path == "/api/student-profile":
            resume_text = str(body.get("resume_text", "")).strip()
            parser_mode = str(body.get("parser_mode", "auto"))
            if not resume_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "resume_text is required"})
                return
            profile, parser_metadata = parse_student_profile(resume_text, parser_mode=parser_mode)
            self._send_json(
                HTTPStatus.OK,
                {
                    "student_profile": profile.to_dict(),
                    "parser": parser_metadata.to_dict(),
                },
            )
            return

        if self.path == "/api/job-profile":
            job_text = str(body.get("job_text", "")).strip()
            parser_mode = str(body.get("parser_mode", "auto"))
            if not job_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "job_text is required"})
                return
            profile, parser_metadata = parse_job_profile(job_text, parser_mode=parser_mode)
            self._send_json(
                HTTPStatus.OK,
                {
                    "job_profile": profile.to_dict(),
                    "parser": parser_metadata.to_dict(),
                },
            )
            return

        if self.path == "/api/match-direct":
            resume_text = str(body.get("resume_text", "")).strip()
            job_text = str(body.get("job_text", "")).strip()
            parser_mode = str(body.get("parser_mode", "auto"))
            if not resume_text or not job_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "resume_text and job_text are required"})
                return
            student, student_parser = parse_student_profile(resume_text, parser_mode=parser_mode)
            job, job_parser = parse_job_profile(job_text, parser_mode=parser_mode)
            match = match_student_to_job(student, job)
            self._send_json(
                HTTPStatus.OK,
                {
                    "student_profile": student.to_dict(),
                    "job_profile": job.to_dict(),
                    "match_result": match.to_dict(),
                    "parsers": {
                        "student": student_parser.to_dict(),
                        "job": job_parser.to_dict(),
                    },
                },
            )
            return

        if self.path == "/api/export-report":
            markdown_text = str(body.get("report_markdown", "")).strip()
            export_format = str(body.get("format", "markdown")).strip().lower()
            title = str(body.get("title", "")).strip() or "职业规划报告"
            base_name = _safe_export_stem(body.get("filename"), fallback="career_plan_report")
            if not markdown_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "report_markdown is required"})
                return
            self._send_report_export(
                markdown_text=markdown_text,
                title=title,
                base_name=base_name,
                export_format=export_format,
            )
            return

        if self.path == "/api/match-templates":
            resume_text = str(body.get("resume_text", "")).strip()
            top_k = int(body.get("top_k", 5))
            parser_mode = str(body.get("parser_mode", "auto"))
            if not resume_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "resume_text is required"})
                return

            student, parser_metadata = parse_student_profile(resume_text, parser_mode=parser_mode)
            matches = rank_student_against_templates(student, _load_templates(), top_k=top_k)
            self._send_json(
                HTTPStatus.OK,
                {
                    "student_profile": student.to_dict(),
                    "matches": matches,
                    "parser": parser_metadata.to_dict(),
                },
            )
            return

        if self.path == "/api/career-plan":
            resume_text = str(body.get("resume_text", "")).strip()
            top_k = int(body.get("top_k", 5))
            parser_mode = str(body.get("parser_mode", "auto"))
            sample_name = str(body.get("sample_name", "")).strip() or None
            agent_answers = _normalize_agent_answers(body.get("agent_answers", {}))
            self_assessment_answers = _normalize_self_assessment(body.get("self_assessment_answers", {}))
            prior_analysis_id = body.get("prior_analysis_id")
            if not resume_text:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "resume_text is required"})
                return

            student, parser_metadata = parse_student_profile(resume_text, parser_mode=parser_mode)
            student = apply_agent_answers(student, agent_answers)
            matches = rank_student_against_templates(student, _load_templates())
            previous_analysis = None
            if prior_analysis_id is not None:
                try:
                    previous_analysis = get_analysis(int(prior_analysis_id))
                except (TypeError, ValueError):
                    previous_analysis = None
            if previous_analysis is None:
                previous_analysis = find_previous_analysis(student_name=student.name, sample_name=sample_name)
            career_plan = build_career_plan(
                student,
                matches,
                previous_analysis=previous_analysis,
                parser_metadata=parser_metadata.to_dict(),
                self_assessment_answers=self_assessment_answers,
            )
            _attach_evidence_citations(matches, career_plan.to_dict())
            report_markdown = build_career_report_markdown(student, matches, career_plan)
            analysis_id = save_analysis(
                sample_name=sample_name,
                parser_requested_mode=parser_mode,
                parser_used_mode=parser_metadata.used_mode,
                resume_text=resume_text,
                student_profile=student.to_dict(),
                matches=matches[:top_k],
                career_plan=career_plan.to_dict(),
                report_markdown=report_markdown,
            )
            self._send_json(
                HTTPStatus.OK,
                {
                    "analysis_id": analysis_id,
                    "student_profile": student.to_dict(),
                    "matches": matches[:top_k],
                    "career_plan": career_plan.to_dict(),
                    "report_markdown": report_markdown,
                    "parser": parser_metadata.to_dict(),
                    "previous_analysis_id": previous_analysis.get("id") if previous_analysis else None,
                },
            )
            return

        if self.path == "/api/reviews":
            try:
                analysis_id = int(body.get("analysis_id", 0))
            except (TypeError, ValueError):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "analysis_id is required"})
                return
            reviewer_name = str(body.get("reviewer_name", "")).strip()
            reviewer_role = str(body.get("reviewer_role", "")).strip() or "辅导员"
            decision = str(body.get("decision", "")).strip()
            notes = str(body.get("notes", "")).strip()
            if analysis_id <= 0:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "analysis_id is required"})
                return
            if not reviewer_name:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "reviewer_name is required"})
                return
            if decision not in {"通过", "需补强", "重点跟进"}:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "decision is invalid"})
                return
            if get_analysis(analysis_id) is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Analysis not found"})
                return

            review_id = save_review(
                analysis_id=analysis_id,
                reviewer_name=reviewer_name,
                reviewer_role=reviewer_role,
                decision=decision,
                notes=notes,
            )
            self._send_json(
                HTTPStatus.OK,
                {
                    "review_id": review_id,
                    "analysis_id": analysis_id,
                    "items": list_reviews(analysis_id=analysis_id, limit=20),
                },
            )
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    init_storage()
    env_host = os.getenv("A13_API_HOST")
    env_port = os.getenv("A13_API_PORT")
    if env_host:
        host = env_host
    if env_port:
        try:
            port = int(env_port)
        except ValueError as error:
            raise RuntimeError(f"A13_API_PORT 不是合法端口：{env_port}") from error

    try:
        server = ThreadingHTTPServer((host, port), A13RequestHandler)
    except PermissionError as error:
        raise RuntimeError(
            f"端口 {port} 无法绑定。请换一个端口后重试，例如设置 A13_API_PORT=8001。"
        ) from error
    print(f"A13 starter API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
