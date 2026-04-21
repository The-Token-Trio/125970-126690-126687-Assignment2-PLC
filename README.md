# Programming Language Project

**AT70.07 — Programming Languages and Compilers**
Assignment 2 | Asian Institute of Technology

---

## Team Members

| Name | Student ID |
| --- | --- |
| Aye Khin Khin Hpone (Yolanda Lim) | st125970 |
| Applegate Tun Oo | st126690 |
| Win Htut Naing | st126687 |

---

## Project Description

Building a statically-typed programming language with the following features:

* **Types:** Integer, Float, Boolean, String
* **Typing:** Static typing with type inference (no explicit declarations)
* **Arithmetic:** `+`, `-`, `*`, `/` with standard precedence (`*`/`/` over `+`/`-`)
* **Boolean Expressions:** Equality (`==`) and inequality (`!=`) between arithmetic expressions
* **Control Flow:** If-then-else, while-loop
* **Functions:** Function abstraction with value parameter passing
* **Built-in:** `print()` function

---

## Submission

* **Submission:** 09 May 2025
* **Project Checking:** 10 May 2025
* **Presentation:** 11 May 2025, 1pm

---

## Code Base

```
components/
├── tokens.py        - Token model and TokenType enum         [Member 1]
├── lexica.py        - Lexer: source → list[Token]            [Member 1]
├── symbol_table.py  - Scoped symbol/type storage             [Member 1]
├── ast_nodes.py     - AST node dataclasses                   [Member 2]
├── parser.py        - Recursive-descent parser               [Member 2]
├── ast_printer.py   - AST pretty-printer for debug/report    [Member 2]
├── type_checker.py  - Static typing and inference            [Member 3]
├── interpreter.py   - Tree-walking interpreter               [Member 3]
└── pipeline.py      - Shared runner for CLI/UI/tests
main.py              - CLI runner for demo or script files
ui.py                - Tkinter UI for script input/output
tests/               - Automated regression tests
```

---

## Member 1 Deliverables — Lexer + Symbol/Type Storage

Stable base for:

* **Token definitions** — `TokenType` enum and `Token` dataclass (with `line`/`column` for diagnostics) in `components/tokens.py`.
* **Keywords and operators** — keyword mapping and operator tokenization in `components/lexica.py`. Handles `==`, `!=`, `=`, arithmetic operators, and delimiters.
* **Identifiers and literals** — identifier scanning with keyword fallback; integer, float, boolean (`true`/`false`), and string literals.
* **Variable/function storage** — scoped `SymbolTable` in `components/symbol_table.py` with duplicate detection and lookup.
* **Type storage** — `LanguageType` enum (`Integer`, `Float`, `Boolean`, `String`, `Void`) attached to variables and function signatures.

### Stable APIs — Member 1

`components/lexica.py`:
* `Lexer(source: str).tokenize() -> list[Token]`
* `iter_tokens(source: str) -> Iterator[Token]`

`components/symbol_table.py`:
* `SymbolTable.define_variable(name, symbol_type, initialized=False)`
* `SymbolTable.define_function(name, return_type, parameters)`
* `SymbolTable.lookup(name)`
* `SymbolTable.exists_in_current_scope(name)`
* `SymbolTable.child_scope()`
* `SymbolTable.set_initialized(name)`
* `SymbolTable.snapshot()`
* `SymbolTable.format_table()`

---

## Member 2 Deliverables — Parser + AST

Builds on Member 1's lexer output to produce a full Abstract Syntax Tree (AST).

* **AST node definitions** — all node dataclasses in `components/ast_nodes.py`. Every node carries `line` and `column` for diagnostics, matching Member 1's error format.
* **Recursive-descent parser** — `components/parser.py` consumes `list[Token]` from the lexer and returns a `Program` node. Implements the full grammar from `HANDOFF_SPEC.md` including operator precedence, if/else, while, function definitions, function calls, and all literal types.
* **AST pretty-printer** — `components/ast_printer.py` walks the AST and renders an indented, human-readable tree. Used for debugging and the project report.

### Stable APIs — Member 2

`components/parser.py`:
* `Parser(tokens: list[Token]).parse() -> Program`

`components/ast_nodes.py` — node classes consumed by Member 3:
* `Program(statements)`
* `Assign(name, value)`
* `If(condition, then_block, else_block)`
* `While(condition, body)`
* `FunctionDef(name, params, body)`
* `FunctionCall(name, args)`
* `Print(expr)`
* `Return(expr)`
* `BinaryOp(op, left, right)`
* `Literal(value)`
* `Identifier(name)`
* `Block(statements)`

`components/ast_printer.py`:
* `ASTPrinter().print(node: ASTNode) -> str`

### Error format — Member 2

Parser errors follow Member 1's convention:
* `[line X, col Y] ParseError: <message>`

---

## Member 3 Deliverables — Type Checker + Interpreter

Completed components:

* **Static type checking with inference** — `components/type_checker.py` infers variable types from first assignment, checks control-flow conditions, validates arithmetic and comparisons, infers function parameter types from first call, and infers function return types from `return` statements.
* **Interpreter/runtime execution** — `components/interpreter.py` executes assignments, `if`, `while`, functions, returns, and `print()` with immediate line-by-line output.
* **Reusable pipeline** — `components/pipeline.py` powers the CLI runner, desktop UI, and tests from one execution path.

---

## Running the System

```bash
python3 main.py
```

This runs the default sample program through all pipeline stages:
1. **Stage 1** — tokenize the source and display the token list
2. **Stage 2** — parse the tokens and print the full AST
3. **Stage 3** — infer/check types and display the symbol table
4. **Stage 4** — execute the program and print runtime output

To run a source file instead of the built-in sample:

```bash
python3 main.py path/to/script.txt
```

To launch the desktop UI:

```bash
python3 ui.py
```

The UI provides:
* script input/editing on the left
* execution output on the right
* separate tabs for tokens, AST, and inferred types

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

Current automated checks cover:
* loop execution with progressive output
* assignment type mismatch detection
* function parameter and return type inference

## Report

The report is located in the `report/` directory. To compile:

```bash
cd report
pdflatex main.tex
pdflatex main.tex
```