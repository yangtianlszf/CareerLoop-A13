from __future__ import annotations

import argparse
import json
from pathlib import Path

from a13_starter.src.benchmark import run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 A13 内置样例基准评测")
    parser.add_argument("--parser-mode", default="rule", help="rule / auto / llm")
    parser.add_argument("--output", help="可选，输出 JSON 文件路径")
    args = parser.parse_args()

    result = run_benchmark(parser_mode=args.parser_mode)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
