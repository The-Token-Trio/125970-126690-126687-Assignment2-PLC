# Programming Language Project

**AT70.07 — Programming Languages and Compilers**  
Assignment 2 | Asian Institute of Technology

---

## Team Members

| Name                              | Student ID |
| --------------------------------- | ---------- |
| Aye Khin Khin Hpone (Yolanda Lim) | st125970   |
| Applegate T. Tun Oo               | st126690   |
| Win Htut Naing                    | st126687   |

## Contribution Table

| Name                              | Student ID | Assignment Scope                                                                                                                                     |
| --------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Aye Khin Khin Hpone (Yolanda Lim) | st125970   | Static typing rules; Type checking; Assignment execution; If execution; While execution; Function execution; `print()` execution; Unary minus type inference and execution; Pipeline integration (`pipeline.py`); Automated test suite (`tests/test_pipeline.py`, 45 tests) |
| Applegate T. Tun Oo               | st126690   | Token definitions; Keywords and operators; Identifiers and literals; Variable/function storage; Type storage                                         |
| Win Htut Naing                    | st126687   | Arithmetic expressions (incl. unary minus); Boolean expressions; Assignment statements; If-then-else; While-loop; Function definitions; Function calls; `print()` syntax |

---

## Overview

A statically-typed interpreted language built from scratch in Python, implementing the full pipeline from source text to execution output.

| Feature       | Detail                                                        |
| ------------- | ------------------------------------------------------------- |
| Types         | `Integer`, `Float`, `Boolean`, `String`                       |
| Typing        | Static, with type inference — no explicit declarations needed |
| Arithmetic    | `+`, `-`, `*`, `/` with standard precedence; unary `-`        |
| Comparisons   | `==`, `!=` between numeric or Boolean values                  |
| Control flow  | `if`/`else`, `while`                                          |
| Functions     | Definition, value-parameter calls, `return`                   |
| Built-in      | `print()` — outputs value with its inferred type              |

No external Python packages are required. The project uses only the Python standard library.

**Repository:** https://github.com/The-Token-Trio/125970-126690-126687-Assignment2-PLC

---

## Quick Example

```
def add(a, b) {
    return a + b;
}

x = 10;
y = 20.5;
z = add(x, y);
print(z);

i = 3;
while (i != 0) {
    print(i);
    i = i - 1;
}
```

Output:

```
30.5 : Float
3 : Integer
2 : Integer
1 : Integer
```

---

## Pipeline

Source code flows through four sequential stages:

```
Source code
    │
    ▼
  Lexer          →  token list
    │
    ▼
  Parser         →  Abstract Syntax Tree (AST)
    │
    ▼
  Type Checker   →  validates types; populates symbol table
    │
    ▼
  Interpreter    →  execution output
```

All stages are wired together in `components/pipeline.py` and shared by the CLI runner, desktop UI, and test suite.

---

## Project Structure

```
components/
├── tokens.py        - Token model and TokenType enum
├── lexica.py        - Lexer: source → list[Token]
├── symbol_table.py  - Scoped symbol/type storage
├── ast_nodes.py     - AST node dataclasses
├── parser.py        - Recursive-descent parser
├── ast_printer.py   - AST pretty-printer for debug/report
├── type_checker.py  - Static typing and inference
├── interpreter.py   - Tree-walking interpreter
└── pipeline.py      - Shared runner for CLI/UI/tests
main.py              - CLI runner for demo or script files
ui.py                - Tkinter desktop UI
tests/               - Automated regression tests
report/              - LaTeX report source and compiled PDF
```

---

## Running

**CLI — built-in sample:**

```bash
python3 main.py
```

**CLI — run a source file:**

```bash
python3 main.py path/to/script.txt
```

Each run prints four labelled stages: token list, AST, inferred type table, and execution output.

**Desktop UI:**

```bash
python3 ui.py
```

Edit a script on the left panel and click Run. Results appear in tabbed panes on the right: Tokens, AST, Types, and Output.

---

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

45 tests across 4 classes in `tests/test_pipeline.py`:

| Class | Stage | Tests |
|---|---|---|
| `LexerTests` | Tokenisation | 10 |
| `ParserTests` | Parsing and precedence | 5 |
| `TypeCheckerTests` | Static type inference and error detection | 13 |
| `IntegrationTests` | Full pipeline execution | 17 |

---

## Error Reporting

Errors are reported at the appropriate stage with source positions:

| Stage        | Example message                                                              |
| ------------ | ---------------------------------------------------------------------------- |
| Lexer        | `[line 1, col 7] Unterminated string literal`                                |
| Parser       | `[line 2, col 1] ParseError: Expected ';' after expression`                  |
| Type checker | `[line 3, col 5] TypeError: Cannot assign String to variable 'x' of type Integer` |


