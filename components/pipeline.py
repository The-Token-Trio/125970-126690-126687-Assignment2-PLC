from __future__ import annotations

from dataclasses import dataclass

from components.ast_printer import ASTPrinter
from components.interpreter import Interpreter
from components.lexica import Lexer
from components.parser import Parser
from components.symbol_table import SymbolTable
from components.tokens import Token
from components.type_checker import TypeChecker


@dataclass
class PipelineResult:
    tokens: list[Token]
    ast_text: str
    checked_scope: SymbolTable
    outputs: list[str]


def run_pipeline(source_code: str) -> PipelineResult:
    tokens = Lexer(source_code).tokenize()
    tree = Parser(tokens).parse()
    ast_text = ASTPrinter().print(tree)
    checked_scope = TypeChecker().check(tree)

    outputs: list[str] = []
    Interpreter(output_callback=outputs.append).execute(tree)

    return PipelineResult(
        tokens=tokens,
        ast_text=ast_text,
        checked_scope=checked_scope,
        outputs=outputs,
    )


def format_tokens(tokens: list[Token]) -> str:
    lines = []
    for token in tokens:
        lines.append(
            f"  {token.token_type.name:<14} {token.lexeme!r:<12} line={token.line} col={token.column}"
        )
    return "\n".join(lines)


def format_stage_output(result: PipelineResult) -> str:
    sections = [
        "=" * 60,
        "  STAGE 1 — TOKENS",
        "=" * 60,
        format_tokens(result.tokens),
        "",
        "=" * 60,
        "  STAGE 2 — AST (parser output)",
        "=" * 60,
        result.ast_text,
        "",
        "=" * 60,
        "  STAGE 3 — TYPE CHECK",
        "=" * 60,
        result.checked_scope.format_table(),
        "",
        "=" * 60,
        "  STAGE 4 — EXECUTION",
        "=" * 60,
        "\n".join(result.outputs) if result.outputs else "(no output)",
    ]
    return "\n".join(sections)