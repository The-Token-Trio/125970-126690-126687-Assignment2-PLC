# Programming Language Project

**AT70.07 — Programming Languages and Compilers**
Assignment 2 | Asian Institute of Technology

---

## Team Members

| Name | Student ID |
|---|---|
| Aye Khin Khin Hpone (Yolanda Lim) | st125970 |
| Applegate Tun Oo | st126690 |
| Win Htut Naing | st126687 |
---

## Project Description

Building a statically-typed programming language with the following features:

- **Types:** Integer, Float, Boolean, String
- **Typing:** Static typing with type inference (no explicit declarations)
- **Arithmetic:** `+`, `-`, `*`, `/` with standard precedence (`*`/`/` over `+`/`-`)
- **Boolean Expressions:** Equality (`==`) and inequality (`!=`) between arithmetic expressions
- **Control Flow:** If-then-else, while-loop
- **Functions:** Function abstraction with value parameter passing
- **Built-in:** `print()` function

---

## Submission

- **Submission:** 09 May 2025
- **Project Checking:** 10 May 2025
- **Presentation:** 11 May 2025, 1pm

---
## Code Base

Initial compiler components are available in:

- `components/tokens.py` - token model and token type definitions
- `components/lexica.py` - lexer implementation (keywords, operators, identifiers, literals)
- `components/symbol_table.py` - symbol/type storage for variables and functions
- `main.py` - small demo for tokenization + symbol table
- `HANDOFF_SPEC.md` - interface contracts for Parser and Type/Interpreter teammates
- `SAMPLE_PROGRAMS.md` - valid/invalid integration fixtures

### Member 1 Deliverables (Lexer + Symbol/Type Storage)

This part includes a stable base for:

- **Token definitions**
  - Canonical token enum in `components/tokens.py` (`TokenType`).
  - Structured token data model (`Token`) including `line`/`column` for diagnostics.
- **Keywords and operators**
  - Keyword mapping and operator tokenization rules in `components/lexica.py`.
  - Includes handling for `==`, `!=`, `=`, arithmetic operators, and delimiters.
- **Identifiers and literals**
  - Identifier scanning with keyword fallback.
  - Literal support for integer, float, boolean (`true`/`false`), and string.
- **Variable/function storage**
  - Scoped symbol table in `components/symbol_table.py` with duplicate detection and lookup.
  - Variable and function symbols stored using dedicated dataclasses.
- **Type storage**
  - Canonical language types in `LanguageType` enum (`Integer`, `Float`, `Boolean`, `String`, `Void`).
  - Type metadata attached to both variables and function signatures.

### Integration Notes for upcoming features

If you are implementing parser, type checker, or interpreter:

- Read `HANDOFF_SPEC.md` first for stable contracts and grammar target.
- Use `SAMPLE_PROGRAMS.md` as shared fixtures for positive/negative testing.
- Keep token names unchanged unless all members agree and update contracts together.

### Stable APIs Exposed

`components/lexica.py`:

- `Lexer(source: str).tokenize() -> list[Token]`
- `iter_tokens(source: str) -> Iterator[Token]`

`components/symbol_table.py`:

- `SymbolTable.define_variable(name, symbol_type, initialized=False)`
- `SymbolTable.define_function(name, return_type, parameters)`
- `SymbolTable.lookup(name)`
- `SymbolTable.exists_in_current_scope(name)`
- `SymbolTable.child_scope()`
- `SymbolTable.set_initialized(name)`
- `SymbolTable.snapshot()`
- `SymbolTable.format_table()`

Run:

```bash
python3 main.py
```

## Report

The report is located in the `report/` directory. To compile:

```bash
cd report
pdflatex main.tex
pdflatex main.tex
```
