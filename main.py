from components.lexica import Lexer
from components.symbol_table import LanguageType, SymbolTable


def run_demo() -> None:
    # Change source code to test
    source_code = """
def add(a, b) {
    result = a + b;
    print(result);
}
x = 10;
y = 20.5;
flag = true;
name = "plc";
if (x != 0) {
    print(name);
}
"""

    print("=== TOKENS ===")
    tokens = Lexer(source_code).tokenize()
    for token in tokens:
        print(f"{token.token_type.name:<14} {token.lexeme!r:<12} line={token.line} col={token.column}")

    print("\n=== SYMBOL TABLE ===")
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


if __name__ == "__main__":
    run_demo()

