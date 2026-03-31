from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "a13_starter" / "generated" / "analysis_history.db"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_storage() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                sample_name TEXT,
                parser_requested_mode TEXT,
                parser_used_mode TEXT,
                resume_text TEXT NOT NULL,
                student_profile_json TEXT NOT NULL,
                matches_json TEXT NOT NULL,
                career_plan_json TEXT NOT NULL,
                report_markdown TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_analysis(
    *,
    sample_name: str | None,
    parser_requested_mode: str,
    parser_used_mode: str,
    resume_text: str,
    student_profile: dict[str, Any],
    matches: list[dict[str, Any]],
    career_plan: dict[str, Any],
    report_markdown: str,
) -> int:
    init_storage()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (
                created_at,
                sample_name,
                parser_requested_mode,
                parser_used_mode,
                resume_text,
                student_profile_json,
                matches_json,
                career_plan_json,
                report_markdown
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                sample_name,
                parser_requested_mode,
                parser_used_mode,
                resume_text,
                json.dumps(student_profile, ensure_ascii=False),
                json.dumps(matches, ensure_ascii=False),
                json.dumps(career_plan, ensure_ascii=False),
                report_markdown,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_analyses(limit: int = 20) -> list[dict[str, Any]]:
    init_storage()
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                created_at,
                sample_name,
                parser_requested_mode,
                parser_used_mode,
                student_profile_json,
                career_plan_json
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()

    items: list[dict[str, Any]] = []
    for row in rows:
        student_profile = json.loads(row["student_profile_json"])
        career_plan = json.loads(row["career_plan_json"])
        items.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "sample_name": row["sample_name"],
                "parser_requested_mode": row["parser_requested_mode"],
                "parser_used_mode": row["parser_used_mode"],
                "student_name": student_profile.get("name"),
                "student_major": student_profile.get("major"),
                "primary_role": career_plan.get("primary_role"),
                "primary_score": career_plan.get("primary_score"),
            }
        )
    return items


def get_analysis(analysis_id: int) -> dict[str, Any] | None:
    init_storage()
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "sample_name": row["sample_name"],
        "parser_requested_mode": row["parser_requested_mode"],
        "parser_used_mode": row["parser_used_mode"],
        "resume_text": row["resume_text"],
        "student_profile": json.loads(row["student_profile_json"]),
        "matches": json.loads(row["matches_json"]),
        "career_plan": json.loads(row["career_plan_json"]),
        "report_markdown": row["report_markdown"],
    }
