from __future__ import annotations

import json
from pathlib import Path


INITIAL_ROLE_TITLES = [
    "Java",
    "C/C++",
    "前端开发",
    "实施工程师",
    "技术支持工程师",
    "测试工程师",
    "软件测试",
    "硬件测试",
    "质量管理/测试",
    "产品专员/助理",
]


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    generated_dir = project_root / "a13_starter" / "generated"
    role_library_path = generated_dir / "role_library.json"
    output_path = generated_dir / "initial_role_seeds.json"

    roles = json.loads(role_library_path.read_text(encoding="utf-8"))
    role_map = {role["title"]: role for role in roles}

    selected = []
    for title in INITIAL_ROLE_TITLES:
        role = role_map.get(title)
        if role:
            selected.append(role)

    output_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Selected roles:", len(selected))
    print("Wrote:", output_path)
    for role in selected:
        print("-", role["title"], role["count"])


if __name__ == "__main__":
    main()
