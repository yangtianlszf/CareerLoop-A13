from __future__ import annotations

import json
import sqlite3
from collections import Counter
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


def find_previous_analysis(
    *,
    student_name: str | None,
    sample_name: str | None = None,
    limit: int = 30,
) -> dict[str, Any] | None:
    init_storage()
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()

    for row in rows:
        row_sample_name = row["sample_name"]
        student_profile = json.loads(row["student_profile_json"])
        if sample_name and row_sample_name == sample_name:
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "sample_name": row_sample_name,
                "parser_requested_mode": row["parser_requested_mode"],
                "parser_used_mode": row["parser_used_mode"],
                "resume_text": row["resume_text"],
                "student_profile": student_profile,
                "matches": json.loads(row["matches_json"]),
                "career_plan": json.loads(row["career_plan_json"]),
                "report_markdown": row["report_markdown"],
            }
        if student_name and student_profile.get("name") == student_name:
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "sample_name": row_sample_name,
                "parser_requested_mode": row["parser_requested_mode"],
                "parser_used_mode": row["parser_used_mode"],
                "resume_text": row["resume_text"],
                "student_profile": student_profile,
                "matches": json.loads(row["matches_json"]),
                "career_plan": json.loads(row["career_plan_json"]),
                "report_markdown": row["report_markdown"],
            }
    return None


def build_school_dashboard(limit: int = 80) -> dict[str, Any]:
    init_storage()
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, limit),),
        ).fetchall()

    if not rows:
        return {
            "summary_cards": [],
            "top_roles": [],
            "major_distribution": [],
            "city_distribution": [],
            "follow_up_students": [],
            "advice": [],
        }

    role_counter: Counter[str] = Counter()
    major_counter: Counter[str] = Counter()
    city_counter: Counter[str] = Counter()
    follow_up_students: list[dict[str, Any]] = []
    avg_score_total = 0
    score_band_counter: Counter[str] = Counter()

    for row in rows:
        student_profile = json.loads(row["student_profile_json"])
        career_plan = json.loads(row["career_plan_json"])
        student_name = student_profile.get("name") or "未命名学生"
        primary_role = career_plan.get("primary_role") or "未生成"
        primary_score = int(career_plan.get("primary_score") or 0)
        completeness = int(student_profile.get("profile_completeness") or 0)
        competitiveness = int(student_profile.get("competitiveness_score") or 0)

        role_counter[primary_role] += 1
        major_counter[student_profile.get("major") or "专业未填写"] += 1
        city_counter[student_profile.get("city_preference") or "城市未填写"] += 1
        avg_score_total += primary_score

        if primary_score >= 80:
            score_band_counter["强匹配"] += 1
        elif primary_score >= 65:
            score_band_counter["潜力可转化"] += 1
        else:
            score_band_counter["重点帮扶"] += 1

        if primary_score < 65 or completeness < 75:
            follow_up_students.append(
                {
                    "name": student_name,
                    "major": student_profile.get("major") or "专业未填写",
                    "primary_role": primary_role,
                    "primary_score": primary_score,
                    "completeness": completeness,
                    "competitiveness": competitiveness,
                    "created_at": row["created_at"],
                }
            )

    analysis_count = len(rows)
    summary_cards = [
        {"label": "已分析学生", "value": analysis_count, "detail": "来自历史分析记录，可作为学院就业服务沉淀数据。"},
        {"label": "平均主岗分", "value": round(avg_score_total / analysis_count), "detail": "反映当前样本整体就业准备度。"},
        {"label": "重点帮扶人数", "value": score_band_counter["重点帮扶"], "detail": "主岗分偏低或画像不完整，建议辅导员优先跟进。"},
        {"label": "强匹配人数", "value": score_band_counter["强匹配"], "detail": "适合直接推岗、推实习或重点投递。"},
    ]

    advice = [
        "对主岗分低于 65 的学生，先补画像完整度和一项可展示项目。",
        "对强匹配学生，优先推送对应岗位招聘信息和模拟面试机会。",
        "对城市偏好集中的学生，可做区域化推岗和宣讲活动配置。",
    ]

    return {
        "summary_cards": summary_cards,
        "top_roles": [{"name": name, "count": count} for name, count in role_counter.most_common(5)],
        "major_distribution": [{"name": name, "count": count} for name, count in major_counter.most_common(5)],
        "city_distribution": [{"name": name, "count": count} for name, count in city_counter.most_common(5)],
        "score_bands": [{"name": name, "count": count} for name, count in score_band_counter.items()],
        "follow_up_students": sorted(follow_up_students, key=lambda item: item["primary_score"])[:6],
        "advice": advice,
    }
