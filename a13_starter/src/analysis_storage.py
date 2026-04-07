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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                reviewer_name TEXT NOT NULL,
                reviewer_role TEXT NOT NULL,
                decision TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
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


def save_review(
    *,
    analysis_id: int,
    reviewer_name: str,
    reviewer_role: str,
    decision: str,
    notes: str,
) -> int:
    init_storage()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_reviews (
                analysis_id,
                created_at,
                reviewer_name,
                reviewer_role,
                decision,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_id,
                created_at,
                reviewer_name,
                reviewer_role,
                decision,
                notes,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_reviews(*, analysis_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    init_storage()
    query = """
        SELECT
            r.id,
            r.analysis_id,
            r.created_at,
            r.reviewer_name,
            r.reviewer_role,
            r.decision,
            r.notes,
            a.student_profile_json,
            a.career_plan_json
        FROM analysis_reviews r
        JOIN analyses a ON a.id = r.analysis_id
    """
    params: list[Any] = []
    if analysis_id is not None:
        query += " WHERE r.analysis_id = ?"
        params.append(int(analysis_id))
    query += " ORDER BY r.id DESC LIMIT ?"
    params.append(max(1, limit))

    with _get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    items: list[dict[str, Any]] = []
    for row in rows:
        student_profile = json.loads(row["student_profile_json"])
        career_plan = json.loads(row["career_plan_json"])
        items.append(
            {
                "id": row["id"],
                "analysis_id": row["analysis_id"],
                "created_at": row["created_at"],
                "reviewer_name": row["reviewer_name"],
                "reviewer_role": row["reviewer_role"],
                "decision": row["decision"],
                "notes": row["notes"] or "",
                "student_name": student_profile.get("name"),
                "primary_role": career_plan.get("primary_role"),
                "primary_score": career_plan.get("primary_score"),
            }
        )
    return items


def _latest_review_map() -> dict[int, dict[str, Any]]:
    latest: dict[int, dict[str, Any]] = {}
    for review in list_reviews(limit=500):
        analysis_id = int(review["analysis_id"])
        if analysis_id not in latest:
            latest[analysis_id] = review
    return latest


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


def find_similar_analyses(
    *,
    student_name: str | None,
    major: str | None,
    target_roles: list[str] | None,
    city_preference: str | None,
    primary_role: str | None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    init_storage()
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM analyses
            ORDER BY id DESC
            LIMIT 80
            """
        ).fetchall()

    latest_review_by_analysis = _latest_review_map()
    target_role_set = {str(item).strip() for item in target_roles or [] if str(item).strip()}
    results: list[dict[str, Any]] = []
    for row in rows:
        student_profile = json.loads(row["student_profile_json"])
        career_plan = json.loads(row["career_plan_json"])
        candidate_name = student_profile.get("name")
        if student_name and candidate_name == student_name:
            continue

        score = 0
        reasons: list[str] = []
        if primary_role and career_plan.get("primary_role") == primary_role:
            score += 40
            reasons.append("主推荐岗位一致")
        if major and student_profile.get("major") == major:
            score += 26
            reasons.append("专业背景相近")
        if city_preference and student_profile.get("city_preference") == city_preference:
            score += 16
            reasons.append("城市偏好接近")
        role_overlap = target_role_set & {
            str(item).strip() for item in student_profile.get("target_roles", []) if str(item).strip()
        }
        if role_overlap:
            score += 18
            reasons.append("目标岗位意向重叠")

        skill_overlap = len(
            {
                str(item).strip()
                for item in student_profile.get("skills", [])
                if str(item).strip()
            }
            & {
                str(item).strip()
                for item in career_plan.get("evidence_bundle", {}).get("hit_terms", [])
                if str(item).strip()
            }
        )
        if skill_overlap:
            score += min(skill_overlap * 3, 12)
            reasons.append(f"命中 {skill_overlap} 个相近技能词")

        if score <= 0:
            continue

        latest_review = latest_review_by_analysis.get(int(row["id"]))
        results.append(
            {
                "analysis_id": row["id"],
                "student_name": candidate_name or "匿名学生",
                "major": student_profile.get("major") or "专业未填写",
                "primary_role": career_plan.get("primary_role") or "未生成",
                "primary_score": career_plan.get("primary_score") or 0,
                "created_at": row["created_at"],
                "similarity_score": score,
                "reasons": reasons,
                "takeaway": "可参考其项目举证、技能补强顺序和岗位收敛策略。",
                "review_status": latest_review.get("decision") if latest_review else "未复核",
            }
        )

    results.sort(key=lambda item: (item["similarity_score"], item["primary_score"]), reverse=True)
    return results[: max(1, limit)]


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

    latest_review_by_analysis = _latest_review_map()
    recent_reviews = list_reviews(limit=8)

    if not rows:
        return {
            "summary_cards": [],
            "top_roles": [],
            "major_distribution": [],
            "city_distribution": [],
            "follow_up_students": [],
            "review_metrics": [],
            "recent_reviews": [],
            "advice": [],
        }

    role_counter: Counter[str] = Counter()
    major_counter: Counter[str] = Counter()
    city_counter: Counter[str] = Counter()
    role_city_counter: Counter[str] = Counter()
    role_major_counter: Counter[str] = Counter()
    follow_up_students: list[dict[str, Any]] = []
    audit_queue: list[dict[str, Any]] = []
    avg_score_total = 0
    score_band_counter: Counter[str] = Counter()
    evidence_hit_total = 0
    loop_completion_total = 0
    fallback_count = 0
    llm_count = 0
    reviewed_count = 0
    approved_count = 0
    revise_count = 0

    for row in rows:
        student_profile = json.loads(row["student_profile_json"])
        career_plan = json.loads(row["career_plan_json"])
        student_name = student_profile.get("name") or "未命名学生"
        primary_role = career_plan.get("primary_role") or "未生成"
        primary_score = int(career_plan.get("primary_score") or 0)
        completeness = int(student_profile.get("profile_completeness") or 0)
        competitiveness = int(student_profile.get("competitiveness_score") or 0)
        city = student_profile.get("city_preference") or "城市未填写"
        major = student_profile.get("major") or "专业未填写"
        evidence_hit_rate = int((career_plan.get("evidence_bundle") or {}).get("evidence_hit_rate") or 0)
        evaluation_metrics = career_plan.get("evaluation_metrics") or []
        loop_metric = next((item for item in evaluation_metrics if item.get("name") == "闭环完成度"), None)
        loop_completion = int(loop_metric.get("score") or 0) if loop_metric else 0
        latest_review = latest_review_by_analysis.get(int(row["id"]))

        role_counter[primary_role] += 1
        major_counter[major] += 1
        city_counter[city] += 1
        role_city_counter[f"{primary_role}｜{city}"] += 1
        role_major_counter[f"{major}｜{primary_role}"] += 1
        avg_score_total += primary_score
        evidence_hit_total += evidence_hit_rate
        loop_completion_total += loop_completion
        if row["parser_used_mode"] == "rule" and row["parser_requested_mode"] in {"auto", "llm"}:
            fallback_count += 1
        if row["parser_used_mode"] == "llm":
            llm_count += 1
        if latest_review:
            reviewed_count += 1
            if latest_review.get("decision") == "通过":
                approved_count += 1
            elif latest_review.get("decision") == "需补强":
                revise_count += 1

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
                    "review_status": latest_review.get("decision") if latest_review else "待复核",
                }
            )

        audit_reasons: list[str] = []
        if evidence_hit_rate < 65:
            audit_reasons.append("证据命中率偏低")
        if completeness < 75:
            audit_reasons.append("画像完整度不足")
        if row["parser_used_mode"] == "rule" and row["parser_requested_mode"] in {"auto", "llm"}:
            audit_reasons.append("本次触发规则回退")
        if primary_score < 68:
            audit_reasons.append("主岗位匹配分偏低")
        if audit_reasons:
            audit_queue.append(
                {
                    "name": student_name,
                    "primary_role": primary_role,
                    "major": major,
                    "city": city,
                    "primary_score": primary_score,
                    "completeness": completeness,
                    "evidence_hit_rate": evidence_hit_rate,
                    "reasons": audit_reasons,
                    "created_at": row["created_at"],
                    "review_status": latest_review.get("decision") if latest_review else "待复核",
                }
            )

    analysis_count = len(rows)
    avg_evidence_hit = round(evidence_hit_total / analysis_count)
    avg_loop_completion = round(loop_completion_total / analysis_count)
    summary_cards = [
        {"label": "已分析学生", "value": analysis_count, "detail": "来自历史分析记录，可作为学院就业服务沉淀数据。"},
        {"label": "平均主岗分", "value": round(avg_score_total / analysis_count), "detail": "反映当前样本整体就业准备度。"},
        {"label": "重点帮扶人数", "value": score_band_counter["重点帮扶"], "detail": "主岗分偏低或画像不完整，建议辅导员优先跟进。"},
        {"label": "强匹配人数", "value": score_band_counter["强匹配"], "detail": "适合直接推岗、推实习或重点投递。"},
        {"label": "证据命中均分", "value": avg_evidence_hit, "detail": "衡量推荐结果是否被官方 JD 和岗位模板片段充分支撑。"},
        {"label": "闭环完成均分", "value": avg_loop_completion, "detail": "反映追问、自测、复测与补强任务的执行成熟度。"},
    ]

    advice = [
        "对主岗分低于 65 的学生，先补画像完整度和一项可展示项目。",
        "对强匹配学生，优先推送对应岗位招聘信息和模拟面试机会。",
        "对城市偏好集中的学生，可做区域化推岗和宣讲活动配置。",
    ]

    service_segments = [
        {
            "label": "强匹配直推",
            "count": score_band_counter["强匹配"],
            "detail": "优先投递、推送实习和企业直连活动。",
        },
        {
            "label": "潜力转化",
            "count": score_band_counter["潜力可转化"],
            "detail": "围绕技能补强和项目举证做 2 到 4 周集中训练。",
        },
        {
            "label": "重点帮扶",
            "count": score_band_counter["重点帮扶"],
            "detail": "辅导员跟进画像补全、岗位收敛与一生一策辅导。",
        },
    ]

    push_recommendations = []
    for name, count in role_city_counter.most_common(4):
        role_name, city_name = name.split("｜", 1)
        push_recommendations.append(
            {
                "type": "区域推岗",
                "title": f"{city_name} · {role_name}",
                "count": count,
                "detail": "适合做城市专场推岗、区域化企业推送和宣讲活动配置。",
            }
        )
    for name, count in role_major_counter.most_common(3):
        major_name, role_name = name.split("｜", 1)
        push_recommendations.append(
            {
                "type": "专业定向",
                "title": f"{major_name} · {role_name}",
                "count": count,
                "detail": "适合做学院定向岗位包、课程补强和重点群体投递建议。",
            }
        )
    push_recommendations = push_recommendations[:6]

    governance_metrics = [
        {
            "label": "规则回退次数",
            "value": fallback_count,
            "detail": "用于定位网络异常或解析不稳定场景，辅助现场兜底和系统治理。",
        },
        {
            "label": "LLM 直出次数",
            "value": llm_count,
            "detail": "反映模型可用时的自动解析覆盖情况。",
        },
        {
            "label": "待抽检记录",
            "value": len(audit_queue),
            "detail": "聚合证据命中率偏低、画像不完整或匹配分偏低的记录。",
        },
        {
            "label": "已复核记录",
            "value": reviewed_count,
            "detail": "反映辅导员或就业老师已完成抽检、通过或退回补强的记录数量。",
        },
    ]

    review_metrics = [
        {
            "label": "复核覆盖数",
            "value": reviewed_count,
            "detail": "已有老师留痕的分析记录数，可用于证明人机协同治理真实存在。",
        },
        {
            "label": "复核通过数",
            "value": approved_count,
            "detail": "已确认结果可信、可直接推岗或进入下一轮服务的记录数。",
        },
        {
            "label": "待补强数",
            "value": revise_count,
            "detail": "被老师标记为需补充证据、需继续训练或需调整岗位方向的记录数。",
        },
        {
            "label": "待复核数",
            "value": max(analysis_count - reviewed_count, 0),
            "detail": "尚未留痕复核的记录，可进入辅导员抽检队列。",
        },
    ]

    return {
        "summary_cards": summary_cards,
        "top_roles": [{"name": name, "count": count} for name, count in role_counter.most_common(5)],
        "major_distribution": [{"name": name, "count": count} for name, count in major_counter.most_common(5)],
        "city_distribution": [{"name": name, "count": count} for name, count in city_counter.most_common(5)],
        "score_bands": [{"name": name, "count": count} for name, count in score_band_counter.items()],
        "follow_up_students": sorted(follow_up_students, key=lambda item: item["primary_score"])[:6],
        "audit_queue": sorted(audit_queue, key=lambda item: (item["primary_score"], item["evidence_hit_rate"]))[:6],
        "governance_metrics": governance_metrics,
        "review_metrics": review_metrics,
        "recent_reviews": recent_reviews,
        "service_segments": service_segments,
        "push_recommendations": push_recommendations,
        "advice": advice,
    }
