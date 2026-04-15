## 1) Scope Delivered by Member 1

Delivered modules:

- `components/tokens.py`
- `components/lexica.py`
- `components/symbol_table.py`

Delivered capabilities:

- Token type definitions and token object model.
- Lexical analysis for keywords, operators, delimiters, identifiers, and literals.
- Symbol and type storage for variables/functions with scoped lookup.

## 2) Stable Token Contract (For Member 2 Parser)

Token enum lives in `TokenType` with these categories:

- Literals: `INT_LITERAL`, `FLOAT_LITERAL`, `BOOL_LITERAL`, `STRING_LITERAL`
- Identifier: `IDENTIFIER`
- Keywords: `IF`, `ELSE`, `WHILE`, `DEF`, `RETURN`, `PRINT`
- Operators: `PLUS`, `MINUS`, `STAR`, `SLASH`, `EQUAL_EQUAL`, `BANG_EQUAL`, `ASSIGN`
- Delimiters: `LPAREN`, `RPAREN`, `LBRACE`, `RBRACE`, `COMMA`, `SEMICOLON`
- End marker: `EOF`

Token object fields:

- `token_type: TokenType`
- `lexeme: str`
- `line: int`
- `column: int`

Keywords recognized by lexer:

- `if`, `else`, `while`, `def`, `return`, `print`, `true`, `false`

Operator behavior:

- `=` -> `ASSIGN`
- `==` -> `EQUAL_EQUAL`
- `!=` -> `BANG_EQUAL`
- `+`, `-`, `*`, `/` -> arithmetic operators

Literal behavior:

- Integer: one or more digits (example: `10`)
- Float: digits + dot + digits (example: `20.5`)
- Boolean: `true`/`false` (tokenized as `BOOL_LITERAL`)
- String: double-quoted text (example: `"hello"`)

## 3) Parser Contract (Member 2)

Can use the following grammar target (minimal project grammar):

```txt
program      -> statement* EOF

statement    -> assignment ";"
             | if_stmt
             | while_stmt
             | func_def
             | print_stmt ";"
             | return_stmt ";"
             | expr ";"

assignment   -> IDENTIFIER "=" expr
if_stmt      -> "if" "(" bool_expr ")" block ("else" block)?
while_stmt   -> "while" "(" bool_expr ")" block
func_def     -> "def" IDENTIFIER "(" params? ")" block
print_stmt   -> "print" "(" expr ")"
return_stmt  -> "return" expr

params       -> IDENTIFIER ("," IDENTIFIER)*
args         -> expr ("," expr)*
block        -> "{" statement* "}"

bool_expr    -> expr ("==" | "!=") expr
             | BOOL_LITERAL

expr         -> term (("+" | "-") term)*
term         -> factor (("*" | "/") factor)*
factor       -> INT_LITERAL
             | FLOAT_LITERAL
             | STRING_LITERAL
             | BOOL_LITERAL
             | IDENTIFIER
             | IDENTIFIER "(" args? ")"
             | "(" expr ")"
```

Precedence/associativity requirements:

- Highest: `*`, `/` (left-associative)
- Next: `+`, `-` (left-associative)
- Lowest: `==`, `!=` (non-associative in checker, parse as binary comparison)

## 4) AST Interface (Member 2 -> Member 3)

Member 2 should expose AST node classes equivalent to:

- `Program(statements)`
- `Assign(name, value_expr)`
- `If(condition, then_block, else_block_or_none)`
- `While(condition, body)`
- `FunctionDef(name, params, body)`
- `FunctionCall(name, args)`
- `Print(expr)`
- `Return(expr)`
- `BinaryOp(op, left, right)`
- `Literal(value)`
- `Identifier(name)`
- `Block(statements)`

Minimum expected fields:

- Every node should carry enough data for type checker and interpreter.
- Optional but recommended: source location metadata (`line`, `column`) for better diagnostics.

## 5) Type/Runtime Contract (Member 3)

Type domain:

- `Integer`, `Float`, `Boolean`, `String`, `Void`

Static typing rules:

- Arithmetic operators (`+`, `-`, `*`, `/`) accept only numeric operands.
- Numeric promotion allowed: `Integer` with `Float` yields `Float`.
- `==` and `!=` compare arithmetic expressions per assignment requirement.
- `if`/`while` condition must be `Boolean`.
- Assignment binds variable type on first assignment; subsequent assignments must match bound type.
- Function parameter types and return type should be inferred/validated consistently by checker design.

Runtime rules:

- Value parameter passing for function calls.
- Lexical scope for variables/functions (global + child scopes).
- `print()` evaluates and prints expression value.

## 6) Symbol Table API Contract (Stable)

`SymbolTable` methods delivered and considered stable:

- `define_variable(name, symbol_type, initialized=False)`
- `define_function(name, return_type, parameters)`
- `lookup(name)`
- `exists_in_current_scope(name)`
- `child_scope()`
- `set_initialized(name)`
- `snapshot()`
- `format_table()`

Symbol kinds:

- `VariableSymbol(name, symbol_type, initialized)`
- `FunctionSymbol(name, symbol_type, parameters)`

Notes:

- `symbol_type` in `FunctionSymbol` is function return type.
- `parameters` in `FunctionSymbol` is a list of `(parameter_name, LanguageType)`.

## 7) Error Message Convention

Lexer uses format:

- `[line X, col Y] <message>`

