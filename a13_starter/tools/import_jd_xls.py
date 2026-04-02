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

# 1. 行业白名单
TARGET_INDUSTRY_KEYWORDS = [
    "计算机", "软件", "互联网", "IT", "通信", "电子", 
    "半导体", "人工智能", "数据", "网络游戏", "信息安全", 
    "系统集成", "物联网", "智能硬件", "电子商务", "新能源", "汽车"
]

# 2. 岗位名称白名单
TARGET_TITLE_KEYWORDS = [
    "开发", "测试", "前端", "后端", "Java", "C++", "C语言", "Python", 
    "算法", "数据", "运维", "实施", "架构", "产品", "硬件", "UI", 
    "网络", "IT", "信息", "全栈", "嵌入式", "安卓", "Android", "iOS"
]

# 🌟 3. 新增：岗位名称黑名单（最高优先级拦截）
BLACKLIST_KEYWORDS = [
    "销售", "客服", "行政", "人事", "财务", "出纳", "前台", "推广", 
    "科研", "研究员", "讲师", "老师", "市场", "招商", "采购"
]

def _is_target_job(row: dict[str, str]) -> bool:
    """三重验证逻辑：黑名单拦截 -> 行业白名单 -> 岗位白名单"""
    industry_str = row.get("所属行业", "")
    title_str = row.get("岗位名称", "")
    
    # 🌟 策略 A (新增)：黑名单一票否决
    for black_word in BLACKLIST_KEYWORDS:
        if black_word in title_str:
            return False
            
    # 策略 B：行业白名单放行
    for keyword in TARGET_INDUSTRY_KEYWORDS:
        if keyword in industry_str:
            return True
            
    # 策略 C：岗位白名单放行
    for keyword in TARGET_TITLE_KEYWORDS:
        if keyword.lower() in title_str.lower():
            return True
            
    return False

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    xls_path = project_root / "A13_官方资料" / "A13-JD采样数据.xls"
    output_dir = project_root / "a13_starter" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_job_rows = load_job_rows(xls_path)
    if not raw_job_rows:
        raise SystemExit("No rows loaded from xls file.")

    # 🌟 调用升级后的双重过滤逻辑
    initial_count = len(raw_job_rows)
    job_rows = [row for row in raw_job_rows if _is_target_job(row)]
    filtered_count = initial_count - len(job_rows)
    print(f"✅ 智能清洗完成：总计 {initial_count} 条，精准剔除 {filtered_count} 条无关数据，最终保留 {len(job_rows)} 条高质量泛IT岗位。")

    if not job_rows:
        raise SystemExit("过滤后没有剩余的岗位数据了，请检查白名单关键词设置。")

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

    print("Wrote:", raw_output)
    print("Wrote:", profiles_output)
    print("Wrote:", summary_output)
    print("Wrote:", sample_output)
    print("Top titles:", summary["top_job_titles"][:10])
    print("Top skills:", summary["top_skills"][:10])


if __name__ == "__main__":
    main()