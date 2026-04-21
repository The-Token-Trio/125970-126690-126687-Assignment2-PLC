from __future__ import annotations

import argparse
from pathlib import Path

from components.pipeline import format_stage_output, run_pipeline


DEFAULT_SOURCE = """
def add(a, b) {
    result = a + b;
    print(result);
    return result;
}

x = 10;
y = 20.5;
flag = true;
name = "plc";

if (x != 0) {
    print(name);
} else {
    print(x);
}

while (flag != false) {
    x = x - 1;
    flag = false;
}

z = add(x, y);
print(z);
"""


def run_source(source_code: str) -> None:
    result = run_pipeline(source_code)
    print(format_stage_output(result))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the programming language pipeline.")
    parser.add_argument("script", nargs="?", help="Optional path to a source file to run")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.script:
        source_code = Path(args.script).read_text(encoding="utf-8")
    else:
        source_code = DEFAULT_SOURCE
    run_source(source_code)


if __name__ == "__main__":
    main()