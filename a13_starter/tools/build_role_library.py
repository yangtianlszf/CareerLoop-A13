from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROLE_KEYWORDS = [
    "开发",
    "测试",
    "Java",
    "C/C++",
    "前端",
    "后端",
    "算法",
    "数据",
    "运维",
    "实施",
    "技术支持",
    "产品",
    "设计",
    "网络",
    "硬件",
    "软件",
]

EXCLUDE_KEYWORDS = [
    "销售",
    "客服",
    "助理",
    "运营",
    "审核",
    "代表",
    "BD",
    "顾问",
    "律师",
    "质检",
    "统计",
    "储备",
    "经理人",
    "总助",
]

INDUSTRY_KEYWORDS = [
    "计算机",
    "互联网",
    "IT服务",
    "物联网",
    "通信",
    "电子商务",
    "企业服务",
    "计算机硬件",
]


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _is_tech_role(source: dict[str, str], profile: dict[str, object]) -> bool:
    title = source.get("岗位名称", "")
    industry = source.get("所属行业", "")
    if any(keyword in title for keyword in EXCLUDE_KEYWORDS):
        return False
    if any(keyword in title for keyword in ROLE_KEYWORDS):
        return True
    if any(keyword in industry for keyword in INDUSTRY_KEYWORDS) and profile.get("required_skills"):
        return True
    return False


def _top_values(items: list[str], limit: int = 10) -> list[list[object]]:
    counter = Counter(item for item in items if item)
    return [[name, count] for name, count in counter.most_common(limit)]


def build_role_library(profiled_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in profiled_rows:
        source = item["source"]
        title = source.get("岗位名称", "").strip() or "未命名岗位"
        grouped[title].append(item)

    all_roles = []
    tech_roles = []

    for title, items in grouped.items():
        first_source = items[0]["source"]
        skills = []
        soft_skills = []
        cities = []
        salaries = []
        companies = []
        industries = []

        for item in items:
            source = item["source"]
            profile = item["profile"]
            skills.extend(profile.get("required_skills", []))
            soft_skills.extend(profile.get("soft_skills", []))
            cities.append(source.get("地址", ""))
            salaries.append(source.get("薪资范围", ""))
            companies.append(source.get("公司名称", ""))
            industries.extend(
                [part.strip() for part in source.get("所属行业", "").split(",") if part.strip()]
            )

        role = {
            "title": title,
            "count": len(items),
            "top_skills": _top_values(skills, 10),
            "top_soft_skills": _top_values(soft_skills, 8),
            "top_cities": _top_values(cities, 8),
            "top_salary_ranges": _top_values(salaries, 8),
            "top_companies": _top_values(companies, 5),
            "top_industries": _top_values(industries, 8),
            "representative_job": {
                "company_name": first_source.get("公司名称", ""),
                "city": first_source.get("地址", ""),
                "salary_range": first_source.get("薪资范围", ""),
                "job_code": first_source.get("岗位编码", ""),
                "job_url": first_source.get("岗位来源地址", ""),
                "job_detail_excerpt": first_source.get("岗位详情", "")[:400],
            },
        }
        all_roles.append(role)
        first_profile = items[0]["profile"]
        if _is_tech_role(first_source, first_profile):
            tech_roles.append(role)

    all_roles.sort(key=lambda item: (-item["count"], item["title"]))
    tech_roles.sort(key=lambda item: (-item["count"], item["title"]))
    return all_roles, tech_roles


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    generated_dir = project_root / "a13_starter" / "generated"
    profiles_path = generated_dir / "job_profiles.jsonl"
    output_all = generated_dir / "role_library.json"
    output_tech = generated_dir / "recommended_tech_roles.json"

    profiled_rows = _load_jsonl(profiles_path)
    all_roles, tech_roles = build_role_library(profiled_rows)

    output_all.write_text(json.dumps(all_roles, ensure_ascii=False, indent=2), encoding="utf-8")
    output_tech.write_text(json.dumps(tech_roles[:20], ensure_ascii=False, indent=2), encoding="utf-8")

    print("Total unique roles:", len(all_roles))
    print("Wrote:", output_all)
    print("Wrote:", output_tech)
    print("Top tech roles:")
    for item in tech_roles[:12]:
        print("-", item["title"], item["count"])


if __name__ == "__main__":
    main()
