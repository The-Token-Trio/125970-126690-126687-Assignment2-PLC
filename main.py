from __future__ import annotations

import argparse
import sys
from pathlib import Path

from components.interpreter import InterpreterError
from components.lexica import LexerError
from components.parser import ParseError
from components.pipeline import format_stage_output, run_pipeline
from components.type_checker import TypeCheckError


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
    try:
        result = run_pipeline(source_code)
        print(format_stage_output(result))
    except (LexerError, ParseError, TypeCheckError, InterpreterError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the programming language pipeline.")
    parser.add_argument("script", nargs="?", help="Optional path to a source file to run")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.script:
        path = Path(args.script)
        if not path.exists():
            print(f"ERROR: File not found: {args.script}", file=sys.stderr)
            sys.exit(1)
        source_code = path.read_text(encoding="utf-8")
    else:
        source_code = DEFAULT_SOURCE
    run_source(source_code)


if __name__ == "__main__":
    main()