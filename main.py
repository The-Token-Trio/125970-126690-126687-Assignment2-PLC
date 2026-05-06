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

def addf(a, b) {
    result = a +. b;
    print(result);
    return result;
}

x = 10;
y = 20;
pi = 3.14;
half = 0.5;
name = "plc";
flag = true;

if (x != 0) {
    print(name);
} else {
    print(x);
}

i = 3;
while (i != 0) {
    print(i);
    i = i - 1;
}

z = add(x, y);
print(z);

w = addf(pi, half);
print(w);
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