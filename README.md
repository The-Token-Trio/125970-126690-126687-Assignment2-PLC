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

## Contribution Table

| Name | Student ID | Assignment Scope |
| --- | --- | --- |
| Applegate Tun Oo | st126690 | Token definitions; Keywords and operators; Identifiers and literals; Variable/function storage; Type storage |
| Win Htut Naing | st126687 | Arithmetic expressions; Boolean expressions; Assignment statements; If-then-else; While-loop; Function definitions; Function calls; `print()` syntax |
| Aye Khin Khin Hpone (Yolanda Lim) | st125970 | Static typing rules; Type checking; Assignment execution; If execution; While execution; Function execution; `print()` execution |

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

**Dependencies:** No external Python dependencies are required. The project uses only the Python standard library on the implementation side.

**GitHub Repository:** https://github.com/The-Token-Trio/125970-126690-126687-Assignment2-PLC

---

## Code Base

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
ui.py                - Tkinter UI for script input/output
tests/               - Automated regression tests
```

---

## Lexer And Symbol Table

Stable base for:

* **Token definitions** — `TokenType` enum and `Token` dataclass (with `line`/`column` for diagnostics) in `components/tokens.py`.
* **Keywords and operators** — keyword mapping and operator tokenization in `components/lexica.py`. Handles `==`, `!=`, `=`, arithmetic operators, and delimiters.
* **Identifiers and literals** — identifier scanning with keyword fallback; integer, float, boolean (`true`/`false`), and string literals.
* **Variable/function storage** — scoped `SymbolTable` in `components/symbol_table.py` with duplicate detection and lookup.
* **Type storage** — `LanguageType` enum (`Integer`, `Float`, `Boolean`, `String`, `Void`) attached to variables and function signatures.

### Stable APIs

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

## Parser And AST

Builds on the lexer output to produce a full Abstract Syntax Tree (AST).

* **AST node definitions** — all node dataclasses in `components/ast_nodes.py`. Every node carries `line` and `column` for diagnostics, matching the lexer's error format.
* **Recursive-descent parser** — `components/parser.py` consumes `list[Token]` from the lexer and returns a `Program` node. Implements the full grammar from `HANDOFF_SPEC.md` including operator precedence, if/else, while, function definitions, function calls, and all literal types.
* **AST pretty-printer** — `components/ast_printer.py` walks the AST and renders an indented, human-readable tree. Used for debugging and the project report.

### Stable APIs

`components/parser.py`:
* `Parser(tokens: list[Token]).parse() -> Program`

`components/ast_nodes.py` — node classes consumed by the type checker and interpreter:
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

### Error Format

Parser errors follow the lexer's convention:
* `[line X, col Y] ParseError: <message>`

---

## Type Checker And Interpreter

Completed components:

* **Static typing rules** — arithmetic expressions require numeric operands, conditions must be Boolean, assignments must remain type-consistent, and function calls must match inferred parameter types.
* **Type checking** — `components/type_checker.py` infers variable types from first assignment, validates arithmetic and comparisons, checks control-flow conditions, infers function parameter types from the first call, and infers function return types from `return` statements.
* **Assignment execution** — runtime assignment stores values in the active lexical environment while preserving inferred types from the checking stage.
* **If execution** — the interpreter evaluates the condition and runs only the selected branch.
* **While execution** — loop conditions are re-evaluated every iteration and `print()` output appears progressively during execution.
* **Function execution** — `components/interpreter.py` supports value parameter passing, local function scope, and return propagation.
* **`print()` execution** — the built-in print emits the runtime value together with its type, for example `29.5 : Float`.
* **Reusable pipeline and system wiring** — `components/pipeline.py`, `main.py`, `ui.py`, and the automated tests connect the type checker and interpreter into the CLI runner, desktop UI, and regression checks.

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