from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Any


_ROLE_RULES: list[dict[str, Any]] = [
    {
        "canonical_title": "测试开发工程师",
        "role_family": "测试",
        "aliases": ("测试开发", "自动化测试开发", "sdet"),
    },
    {
        "canonical_title": "软件测试工程师",
        "role_family": "测试",
        "aliases": ("软件测试",),
    },
    {
        "canonical_title": "硬件测试工程师",
        "role_family": "测试",
        "aliases": ("硬件测试", "可靠性测试"),
    },
    {
        "canonical_title": "测试工程师",
        "role_family": "测试",
        "aliases": ("测试工程师", "质量管理/测试"),
    },
    {
        "canonical_title": "Java开发工程师",
        "role_family": "开发",
        "aliases": ("java",),
    },
    {
        "canonical_title": "Python开发工程师",
        "role_family": "开发",
        "aliases": ("python开发", "python工程师"),
    },
    {
        "canonical_title": "前端开发工程师",
        "role_family": "开发",
        "aliases": ("前端", "web前端", "h5"),
    },
    {
        "canonical_title": "C/C++开发工程师",
        "role_family": "开发",
        "aliases": ("c/c++", "c++", "cpp", "嵌入式开发"),
    },
    {
        "canonical_title": "数据分析师",
        "role_family": "数据",
        "aliases": ("数据分析", "商业分析", "bi"),
    },
    {
        "canonical_title": "算法工程师",
        "role_family": "算法",
        "aliases": ("算法", "机器学习", "深度学习", "nlp", "大模型"),
    },
    {
        "canonical_title": "实施工程师",
        "role_family": "交付",
        "aliases": ("实施工程师", "交付工程师"),
    },
    {
        "canonical_title": "技术支持工程师",
        "role_family": "服务",
        "aliases": ("技术支持", "售后支持", "运维支持"),
    },
    {
        "canonical_title": "售前工程师",
        "role_family": "服务",
        "aliases": ("售前", "解决方案"),
    },
    {
        "canonical_title": "产品助理",
        "role_family": "产品",
        "aliases": ("产品专员/助理", "产品助理"),
    },
    {
        "canonical_title": "产品经理",
        "role_family": "产品",
        "aliases": ("产品经理",),
    },
    {
        "canonical_title": "项目专员",
        "role_family": "项目",
        "aliases": ("项目专员/助理",),
    },
    {
        "canonical_title": "项目经理",
        "role_family": "项目",
        "aliases": ("项目经理/主管", "项目经理"),
    },
    {
        "canonical_title": "运营专员",
        "role_family": "运营",
        "aliases": ("运营助理/专员", "运营专员", "社区运营", "内容运营", "新媒体运营"),
    },
]

_ROLE_FAMILY_LOOKUP = {rule["canonical_title"]: rule["role_family"] for rule in _ROLE_RULES}

_TARGET_INDUSTRY_KEYWORDS = (
    "计算机",
    "软件",
    "互联网",
    "IT",
    "通信",
    "电子",
    "半导体",
    "人工智能",
    "数据",
    "网络游戏",
    "信息安全",
    "系统集成",
    "物联网",
    "智能硬件",
    "电子商务",
    "新能源",
    "汽车",
    "企业服务",
)

_TARGET_DETAIL_KEYWORDS = (
    "开发",
    "测试",
    "接口",
    "数据库",
    "系统部署",
    "故障排查",
    "前端",
    "后端",
    "自动化测试",
    "需求分析",
    "数据分析",
    "python",
    "java",
    "sql",
    "linux",
    "spring",
    "vue",
    "react",
)

_NON_TARGET_TITLE_KEYWORDS = (
    "销售",
    "客服",
    "行政",
    "人事",
    "财务",
    "出纳",
    "前台",
    "推广",
    "科研",
    "研究员",
    "讲师",
    "老师",
    "市场",
    "招商",
    "采购",
    "律师",
    "法务",
    "档案",
    "统计",
    "质检员",
    "总助",
    "猎头",
    "电话销售",
    "网络销售",
)

_TITLE_SIGNAL_KEYWORDS = (
    "开发",
    "测试",
    "前端",
    "后端",
    "实施",
    "技术支持",
    "售前",
    "产品",
    "项目",
    "运营",
    "数据",
    "算法",
    "java",
    "python",
    "c++",
)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = text.replace("\r", "\n")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def _contains_role_alias(source: str, alias: str) -> bool:
    lowered_source = str(source or "").lower()
    lowered_alias = str(alias or "").strip().lower()
    if not lowered_source or not lowered_alias:
        return False
    if re.search(r"[a-zA-Z]", lowered_alias):
        pattern = rf"(?<![a-z0-9+#./-]){re.escape(lowered_alias)}(?![a-z0-9+#./-])"
        return re.search(pattern, lowered_source) is not None
    return lowered_alias in lowered_source


def infer_role_family(title: str | None) -> str:
    clean_title = str(title or "").strip()
    return _ROLE_FAMILY_LOOKUP.get(clean_title, "综合")


def normalize_job_title(title: str, detail: str = "", industry: str = "") -> str:
    raw_title = clean_text(title)
    lowered = raw_title.lower()
    detail_lower = clean_text(detail).lower()
    industry_lower = clean_text(industry).lower()

    if "销售工程师" in raw_title and any(term in detail_lower for term in ("方案", "客户需求", "技术交流", "解决方案")):
        return "售前工程师"

    for rule in _ROLE_RULES:
        for alias in rule["aliases"]:
            if _contains_role_alias(lowered, alias) or _contains_role_alias(detail_lower, alias):
                return str(rule["canonical_title"])

    if "产品" in raw_title and "经理" in raw_title:
        return "产品经理"
    if "项目" in raw_title and any(term in raw_title for term in ("经理", "主管")):
        return "项目经理"
    if any(term in industry_lower for term in ("人工智能", "数据", "互联网")) and "python" in detail_lower:
        return "Python开发工程师"

    return raw_title or "未命名岗位"


def normalize_address(value: str) -> str:
    text = clean_text(value)
    if not text:
        return ""
    text = text.replace("None", "").replace("none", "")
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"\s+", "", text)
    text = text.strip("-")
    return text


def normalize_update_date(value: str) -> str:
    text = clean_text(value)
    if not text:
        return ""

    full_date = re.search(r"(?P<year>\d{4})[年/-](?P<month>\d{1,2})[月/-](?P<day>\d{1,2})", text)
    if full_date:
        year = int(full_date.group("year"))
        month = int(full_date.group("month"))
        day = int(full_date.group("day"))
        return f"{year:04d}-{month:02d}-{day:02d}"

    compact_date = re.search(r"(?P<month>\d{1,2})月(?P<day>\d{1,2})日", text)
    if compact_date:
        month = int(compact_date.group("month"))
        day = int(compact_date.group("day"))
        return f"--{month:02d}-{day:02d}"

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return text


def normalize_salary_range(value: str) -> dict[str, object]:
    text = clean_text(value)
    result: dict[str, object] = {
        "display": text,
        "min": None,
        "max": None,
        "period": "",
    }
    if not text or text == "面议":
        return result

    period = "month"
    if "元/天" in text:
        period = "day"
    elif "元/年" in text or "万/年" in text:
        period = "year"
    result["period"] = period

    match = re.search(r"(?P<low>\d+(?:\.\d+)?)\s*[-~]\s*(?P<high>\d+(?:\.\d+)?)", text)
    if not match:
        return result

    low = float(match.group("low"))
    high = float(match.group("high"))
    multiplier = 1.0
    if "万" in text:
        multiplier = 10000.0
    elif re.search(r"[kK千]", text):
        multiplier = 1000.0

    result["min"] = int(low * multiplier)
    result["max"] = int(high * multiplier)

    unit = "元"
    if period == "day":
        unit = "元/天"
    elif period == "year":
        unit = "元/年"
    else:
        unit = "元/月"
    result["display"] = f"{int(low * multiplier)}-{int(high * multiplier)}{unit}"
    return result


def _count_target_signals(title: str, industry: str, detail: str) -> int:
    lowered_title = title.lower()
    lowered_industry = industry.lower()
    lowered_detail = detail.lower()
    signals = 0
    if any(keyword.lower() in lowered_title for keyword in _TITLE_SIGNAL_KEYWORDS):
        signals += 1
    if any(keyword.lower() in lowered_industry for keyword in _TARGET_INDUSTRY_KEYWORDS):
        signals += 1
    if any(keyword.lower() in lowered_detail for keyword in _TARGET_DETAIL_KEYWORDS):
        signals += 1
    return signals


def is_target_job(row: dict[str, str]) -> tuple[bool, str]:
    title = clean_text(row.get("岗位名称", ""))
    normalized_title = clean_text(row.get("_normalized_title", title))
    industry = clean_text(row.get("所属行业", ""))
    detail = clean_text(row.get("岗位详情", ""))

    if normalized_title in _ROLE_FAMILY_LOOKUP:
        return True, "recognized_role"

    if any(keyword in title for keyword in _NON_TARGET_TITLE_KEYWORDS):
        signals = _count_target_signals(title, industry, detail)
        if signals < 3:
            return False, "blacklist_title"

    signals = _count_target_signals(title, industry, detail)
    if signals >= 2:
        return True, "tech_signal_pass"
    return False, "insufficient_signal"


def clean_job_row(row: dict[str, str]) -> dict[str, object]:
    cleaned = {key: clean_text(value) for key, value in row.items()}
    cleaned["地址"] = normalize_address(cleaned.get("地址", ""))

    salary_meta = normalize_salary_range(cleaned.get("薪资范围", ""))
    cleaned["_normalized_title"] = normalize_job_title(
        cleaned.get("岗位名称", ""),
        detail=cleaned.get("岗位详情", ""),
        industry=cleaned.get("所属行业", ""),
    )
    cleaned["_role_family"] = infer_role_family(str(cleaned.get("_normalized_title", "")))
    cleaned["_normalized_address"] = normalize_address(cleaned.get("地址", ""))
    cleaned["_normalized_salary_range"] = str(salary_meta.get("display", ""))
    cleaned["_salary_min"] = salary_meta.get("min")
    cleaned["_salary_max"] = salary_meta.get("max")
    cleaned["_salary_period"] = str(salary_meta.get("period", ""))
    cleaned["_normalized_update_date"] = normalize_update_date(cleaned.get("更新日期", ""))

    quality_flags: list[str] = []
    if not cleaned.get("公司类型"):
        quality_flags.append("missing_company_type")
    if not cleaned.get("公司详情"):
        quality_flags.append("missing_company_detail")
    if not cleaned.get("岗位详情"):
        quality_flags.append("missing_job_detail")
    if "None" in row.get("地址", ""):
        quality_flags.append("dirty_address")
    cleaned["_quality_flags"] = quality_flags

    is_target, filter_reason = is_target_job({key: str(value) for key, value in cleaned.items()})
    cleaned["_is_target"] = is_target
    cleaned["_filter_reason"] = filter_reason
    return cleaned


def build_cleaning_report(raw_rows: list[dict[str, str]], cleaned_rows: list[dict[str, object]]) -> dict[str, object]:
    kept_rows = [row for row in cleaned_rows if bool(row.get("_is_target"))]
    dropped_rows = [row for row in cleaned_rows if not bool(row.get("_is_target"))]

    kept_titles = Counter(str(row.get("_normalized_title", row.get("岗位名称", ""))) for row in kept_rows)
    raw_title_counter = Counter(str(row.get("岗位名称", "")) for row in kept_rows)
    family_counter = Counter(str(row.get("_role_family", "综合")) for row in kept_rows)
    dropped_reason_counter = Counter(str(row.get("_filter_reason", "unknown")) for row in dropped_rows)
    dropped_titles = Counter(str(row.get("岗位名称", "")) for row in dropped_rows)
    quality_flag_counter = Counter(
        flag
        for row in kept_rows
        for flag in row.get("_quality_flags", [])
        if isinstance(flag, str)
    )

    return {
        "raw_row_count": len(raw_rows),
        "cleaned_row_count": len(cleaned_rows),
        "kept_row_count": len(kept_rows),
        "dropped_row_count": len(dropped_rows),
        "kept_ratio": round(len(kept_rows) / max(1, len(raw_rows)), 4),
        "top_normalized_titles": kept_titles.most_common(20),
        "top_source_titles": raw_title_counter.most_common(20),
        "role_family_distribution": family_counter.most_common(20),
        "drop_reason_distribution": dropped_reason_counter.most_common(20),
        "top_dropped_titles": dropped_titles.most_common(20),
        "quality_flags": quality_flag_counter.most_common(20),
    }
