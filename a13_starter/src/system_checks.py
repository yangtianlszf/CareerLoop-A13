from __future__ import annotations

import sqlite3
import sys
from typing import Any

from a13_starter.src.analysis_storage import DB_PATH, init_storage
from a13_starter.src.jd_search import JD_XLS_PATH, ROLE_TEMPLATES_PATH
from a13_starter.src.paths import resolve_project_root
from a13_starter.src.settings import get_llm_provider, llm_is_configured


PROJECT_ROOT = resolve_project_root(__file__, 2)
JOB_PROFILES_PATH = PROJECT_ROOT / "a13_starter" / "generated" / "job_profiles.jsonl"


def _module_available(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def run_environment_checks() -> dict[str, Any]:
    init_storage()
    db_ok = False
    db_message = "未检查"
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
        db_message = "数据库可读写"
    except Exception as error:
        db_message = f"数据库不可用：{error}"

    pdf_ready = _module_available("pypdf") or _module_available("PyPDF2")
    checks = [
        {
            "name": "Python 环境",
            "status": "ok",
            "detail": f"Python {sys.version.split()[0]}",
        },
        {
            "name": "LLM Key",
            "status": "ok" if llm_is_configured() else "warn",
            "detail": "已配置，可直接走 LLM" if llm_is_configured() else "未配置，将回退到规则解析",
        },
        {
            "name": "LLM Provider",
            "status": "ok",
            "detail": get_llm_provider(),
        },
        {
            "name": "官方 JD Excel",
            "status": "ok" if JD_XLS_PATH.exists() else "warn",
            "detail": "已找到官方原始数据文件" if JD_XLS_PATH.exists() else "未找到 A13-JD采样数据.xls",
        },
        {
            "name": "全量 JD 数据集",
            "status": "ok" if JOB_PROFILES_PATH.exists() else "error",
            "detail": "job_profiles.jsonl 已存在" if JOB_PROFILES_PATH.exists() else "缺少 job_profiles.jsonl",
        },
        {
            "name": "岗位模板库",
            "status": "ok" if ROLE_TEMPLATES_PATH.exists() else "error",
            "detail": "role_profile_templates.json 已存在"
            if ROLE_TEMPLATES_PATH.exists()
            else "缺少 role_profile_templates.json",
        },
        {
            "name": "PDF 解析依赖",
            "status": "ok" if pdf_ready else "warn",
            "detail": "已安装 PDF 解析依赖" if pdf_ready else "未安装，建议优先上传 docx/txt/md",
        },
        {
            "name": "历史记录数据库",
            "status": "ok" if db_ok else "error",
            "detail": db_message,
        },
    ]

    overall = "ok"
    if any(item["status"] == "error" for item in checks):
        overall = "error"
    elif any(item["status"] == "warn" for item in checks):
        overall = "warn"

    return {
        "overall_status": overall,
        "checks": checks,
    }
