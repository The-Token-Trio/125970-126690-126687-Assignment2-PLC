from components.lexica import Lexer
from components.symbol_table import LanguageType, SymbolTable
from components.parser import Parser
from components.ast_printer import ASTPrinter


def run_demo() -> None:
    # Change source code to test
    source_code = """
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

    # ── Member 1: Lexer ──────────────────────────────────────────────────────
    print("=" * 60)
    print("  STAGE 1 — TOKENS")
    print("=" * 60)
    tokens = Lexer(source_code).tokenize()
    for token in tokens:
        print(
            f"  {token.token_type.name:<14} {token.lexeme!r:<12}"
            f" line={token.line} col={token.column}"
        )

    # ── Member 1: Symbol table (manual demo) ────────────────────────────────
    print("\n" + "=" * 60)
    print("  STAGE 1 — SYMBOL TABLE (demo)")
    print("=" * 60)
    global_scope = SymbolTable()
    global_scope.define_function(
        name="add",
        return_type=LanguageType.INTEGER,
        parameters=[("a", LanguageType.INTEGER), ("b", LanguageType.INTEGER)],
    )
    global_scope.define_variable("x", LanguageType.INTEGER, initialized=True)
    global_scope.define_variable("y", LanguageType.FLOAT, initialized=True)
    global_scope.define_variable("flag", LanguageType.BOOLEAN, initialized=True)
    global_scope.define_variable("name", LanguageType.STRING, initialized=True)
    print(global_scope.format_table())

    # ── Member 2: Parser ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  STAGE 2 — AST (parser output)")
    print("=" * 60)
    tree = Parser(tokens).parse()
    print(ASTPrinter().print(tree))


if __name__ == "__main__":
    run_demo()