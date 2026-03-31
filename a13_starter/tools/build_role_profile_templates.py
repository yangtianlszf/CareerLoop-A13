from __future__ import annotations

import json
from pathlib import Path

from a13_starter.src.role_template_specs import ROLE_TEMPLATE_SPECS


NOISY_SKILLS = {"C"}


def _merge_unique(primary: list[str], secondary: list[str], limit: int | None = None) -> list[str]:
    merged: list[str] = []
    for item in primary + secondary:
        if not item or item in merged:
            continue
        merged.append(item)
        if limit is not None and len(merged) >= limit:
            break
    return merged


def _render_markdown(templates: list[dict[str, object]]) -> str:
    lines = ["# 首批岗位画像模板", ""]
    for item in templates:
        lines.append(f"## {item['canonical_title']}")
        lines.append(f"- 原始岗位名：{item['source_title']}")
        lines.append(f"- 岗位族：{item['role_family']}")
        lines.append(f"- 数据样本量：{item['dataset_job_count']}")
        lines.append(f"- 岗位说明：{item['summary']}")
        lines.append(f"- 核心技能：{'、'.join(item['core_skills'])}")
        lines.append(f"- 加分技能：{'、'.join(item['preferred_skills'])}")
        lines.append(f"- 软技能：{'、'.join(item['soft_skills'])}")
        lines.append(f"- 证书要求：{'、'.join(item['certificates'])}")
        lines.append(f"- 学历要求：{item['education_requirement']}")
        lines.append(f"- 经验要求：{item['experience_requirement']}")
        lines.append(f"- 典型行业：{'、'.join(item['typical_industries'])}")
        lines.append(f"- 典型城市：{'、'.join(item['typical_cities'])}")
        lines.append(f"- 常见薪资：{'、'.join(item['sample_salary_ranges'])}")
        lines.append(f"- 纵向成长路径：{' -> '.join(item['vertical_growth_path'])}")
        lines.append(f"- 横向转岗路径：{'、'.join(item['transition_paths'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    generated_dir = project_root / "a13_starter" / "generated"
    seeds_path = generated_dir / "initial_role_seeds.json"
    output_json = generated_dir / "role_profile_templates.json"
    output_md = generated_dir / "role_profile_templates.md"

    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))
    seed_map = {seed["title"]: seed for seed in seeds}

    templates = []
    for source_title, spec in ROLE_TEMPLATE_SPECS.items():
        seed = seed_map.get(source_title)
        if not seed:
            continue

        extracted_skills = [
            name
            for name, _count in seed.get("top_skills", [])
            if name and name not in NOISY_SKILLS
        ]
        extracted_soft_skills = [name for name, _count in seed.get("top_soft_skills", []) if name]
        industries = [name for name, _count in seed.get("top_industries", []) if name][:5]
        cities = [name for name, _count in seed.get("top_cities", []) if name][:5]
        salary_ranges = [name for name, _count in seed.get("top_salary_ranges", []) if name][:5]

        template = {
            "source_title": source_title,
            "canonical_title": spec["canonical_title"],
            "role_family": spec["role_family"],
            "dataset_job_count": seed["count"],
            "summary": spec["summary"],
            "core_skills": list(spec["must_have_skills"]),
            "preferred_skills": _merge_unique(
                spec["preferred_skills"],
                [skill for skill in extracted_skills if skill not in spec["must_have_skills"]],
                limit=8,
            ),
            "soft_skills": _merge_unique(spec["soft_skills"], extracted_soft_skills, limit=8),
            "certificates": spec["certificates"],
            "education_requirement": spec["education_requirement"],
            "experience_requirement": spec["experience_requirement"],
            "typical_industries": industries,
            "typical_cities": cities,
            "sample_salary_ranges": salary_ranges,
            "vertical_growth_path": spec["vertical_growth_path"],
            "transition_paths": spec["transition_paths"],
            "match_weights": {
                "basic_requirements": 0.2,
                "professional_skills": 0.4,
                "professional_literacy": 0.2,
                "growth_potential": 0.2,
            },
            "dataset_evidence": {
                "top_skills": seed.get("top_skills", [])[:10],
                "top_soft_skills": seed.get("top_soft_skills", [])[:8],
                "top_industries": seed.get("top_industries", [])[:5],
                "top_cities": seed.get("top_cities", [])[:5],
            },
        }
        templates.append(template)

    output_json.write_text(json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(_render_markdown(templates), encoding="utf-8")

    print("Generated templates:", len(templates))
    print("Wrote:", output_json)
    print("Wrote:", output_md)
    for item in templates:
        print("-", item["canonical_title"], item["dataset_job_count"])


if __name__ == "__main__":
    main()
