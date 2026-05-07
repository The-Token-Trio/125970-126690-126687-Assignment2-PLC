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
| Aye Khin Khin Hpone (Yolanda Lim) | st125970   | Static typing rules; Type checking; Assignment execution; If execution; While execution; Function execution; `print()` execution; Unary minus type inference and execution; Pipeline integration (`pipeline.py`); Parse-tree/AST stage exposure and documentation alignment; Automated test suite (`tests/test_pipeline.py`, 75 tests) |
| Applegate T. Tun Oo               | st126690   | Lexer implementation (character scanning, tokenisation, line/column tracking, error reporting); Token definitions; Keywords and operators; Identifiers and literals; Variable/function storage; Type storage |
| Win Htut Naing                    | st126687   | Arithmetic expressions (incl. unary minus); Boolean expressions; Assignment statements; If-then-else; While-loop; Function definitions; Function calls; `print()` syntax |

---

## Overview

A statically-typed interpreted language built from scratch in Python, implementing the full pipeline from source text to execution output.

| Feature       | Detail                                                        |
| ------------- | ------------------------------------------------------------- |
| Types         | `Integer`, `Float`, `Boolean`, `String`                       |
| Typing        | Static, with type inference — no explicit declarations needed |
| Arithmetic    | `+`, `-`, `*`, `/` (Integer); `+.`, `-.`, `*.`, `/.` (Float); no overloading |
| Comparisons   | `==`, `!=` between two same-type arithmetic expressions        |
| Control flow  | `if`/`else`, `while`                                          |
| Functions     | Definition, value-parameter calls, `return`                   |
| Built-in      | `print()` — callable built-in function that outputs `value : Type` |

No external Python packages are required. The project uses only the Python standard library.

**Repository:** https://github.com/The-Token-Trio/125970-126690-126687-Assignment2-PLC

---

## Quick Example

```
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
```

Output:

```
"plc" : String
3 : Integer
2 : Integer
1 : Integer
30 : Integer
30 : Integer
3.64 : Float
3.64 : Float
```

---

## Pipeline

Source code flows through four processing stages, exposing five labelled output sections:

```
Source code
    │
    ▼
  Lexer          →  token list
    │
    ▼
  Parser         →  Parse Tree + Abstract Syntax Tree (AST)
    │
    ▼
  Type Checker   →  validates types; populates symbol table
    │
    ▼
  Interpreter    →  execution output
```

All stages are wired together in `components/pipeline.py` and shared by the CLI runner, desktop UI, and test suite.

For inspection purposes, the pipeline now exposes both a grammar-oriented parse tree and the executable AST. The parser still builds the AST used by the type checker and interpreter; the parse tree is an additional ASCII branch rendering that shows grammar layers such as `expr`, `additive`, `term`, `factor`, `args`, punctuation tokens, and `EOF` so the grammar-to-program correspondence is explicit in the submission.

---

## Project Structure

```
components/
├── tokens.py        - Token model and TokenType enum
├── lexica.py        - Lexer: source → list[Token]
├── symbol_table.py  - Scoped symbol/type storage
├── ast_nodes.py     - AST node dataclasses
├── parser.py        - Recursive-descent parser
├── parse_tree_printer.py - Parse-tree renderer for debug/report
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
.\.venv\Scripts\python.exe main.py
```

**CLI — run a source file:**

```bash
.\.venv\Scripts\python.exe main.py path\to\script.txt
```

Each run prints five labelled stages: token list, parse tree, AST, inferred type table, and execution output.

**Desktop UI:**

```bash
.\.venv\Scripts\python.exe ui.py
```

Edit a script on the left panel and click Run. Results appear in six tabbed panes on the right: Execution Output, Tokens, Parse Tree, AST, Type Table, and Errors. The Parse Tree tab shows a grammar-oriented ASCII branch tree, while the AST tab shows the simplified executable tree. On success the Errors tab is cleared; on failure all other tabs are cleared and the error message appears in the Errors tab.

If Python is already on your `PATH`, `python` or `python3` can be used in place of the explicit virtual-environment interpreter above.

---

## Running Tests

```bash
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

75 tests across 5 classes in `tests/test_pipeline.py`:

| Class | Stage | Tests |
|---|---|---|
| `LexerTests` | Tokenisation | 12 |
| `SymbolTableTests` | Scoped symbol table | 7 |
| `ParserTests` | Parsing and precedence | 7 |
| `TypeCheckerTests` | Static type inference and error detection | 22 |
| `IntegrationTests` | Full pipeline execution | 27 |

---

## Error Reporting

Errors are reported at the appropriate stage with source positions:

| Stage        | Example message                                                              |
| ------------ | ---------------------------------------------------------------------------- |
| Lexer        | `[line 1, col 7] LexerError: Unterminated string literal`                    |
| Parser       | `[line 2, col 1] ParseError: Expected ';' after expression`                  |
| Type checker | `[line 3, col 5] TypeError: Cannot assign String to variable 'x' of type Integer` |


