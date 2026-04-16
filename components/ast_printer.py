from __future__ import annotations

from components.ast_nodes import (
    ASTNode,
    Program,
    Block,
    Assign,
    If,
    While,
    FunctionDef,
    FunctionCall,
    Print,
    Return,
    BinaryOp,
    Literal,
    Identifier,
)


class ASTPrinter:
    """Walks an AST and returns a human-readable, indented string.

    Usage:
        tree = Parser(tokens).parse()
        print(ASTPrinter().print(tree))

    Output style — resembles the original source but annotated with node types,
    making it easy to verify the tree structure during development and in reports.
    """

    INDENT = "    "  # 4 spaces per level

    def print(self, node: ASTNode) -> str:
        lines: list[str] = []
        self._visit(node, lines, level=0)
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Dispatcher
    # -----------------------------------------------------------------------

    def _visit(self, node: ASTNode, lines: list[str], level: int) -> None:
        method_name = "_visit_" + type(node).__name__
        visitor = getattr(self, method_name, self._visit_unknown)
        visitor(node, lines, level)

    def _pad(self, level: int) -> str:
        return self.INDENT * level

    # -----------------------------------------------------------------------
    # Node visitors
    # -----------------------------------------------------------------------

    def _visit_Program(self, node: Program, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Program  [{len(node.statements)} statement(s)]")
        for stmt in node.statements:
            self._visit(stmt, lines, level + 1)

    def _visit_Block(self, node: Block, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Block  [{len(node.statements)} statement(s)]")
        for stmt in node.statements:
            self._visit(stmt, lines, level + 1)

    def _visit_Assign(self, node: Assign, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Assign  {node.name!r}  =")
        self._visit(node.value, lines, level + 1)

    def _visit_If(self, node: If, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}If")
        lines.append(f"{self._pad(level + 1)}condition:")
        self._visit(node.condition, lines, level + 2)
        lines.append(f"{self._pad(level + 1)}then:")
        self._visit(node.then_block, lines, level + 2)
        if node.else_block is not None:
            lines.append(f"{self._pad(level + 1)}else:")
            self._visit(node.else_block, lines, level + 2)

    def _visit_While(self, node: While, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}While")
        lines.append(f"{self._pad(level + 1)}condition:")
        self._visit(node.condition, lines, level + 2)
        lines.append(f"{self._pad(level + 1)}body:")
        self._visit(node.body, lines, level + 2)

    def _visit_FunctionDef(self, node: FunctionDef, lines: list[str], level: int) -> None:
        params = ", ".join(node.params) if node.params else "(none)"
        lines.append(f"{self._pad(level)}FunctionDef  {node.name!r}  params=({params})")
        self._visit(node.body, lines, level + 1)

    def _visit_FunctionCall(self, node: FunctionCall, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}FunctionCall  {node.name!r}  [{len(node.args)} arg(s)]")
        for i, arg in enumerate(node.args):
            lines.append(f"{self._pad(level + 1)}arg[{i}]:")
            self._visit(arg, lines, level + 2)

    def _visit_Print(self, node: Print, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Print")
        self._visit(node.expr, lines, level + 1)

    def _visit_Return(self, node: Return, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Return")
        self._visit(node.expr, lines, level + 1)

    def _visit_BinaryOp(self, node: BinaryOp, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}BinaryOp  '{node.op}'")
        lines.append(f"{self._pad(level + 1)}left:")
        self._visit(node.left, lines, level + 2)
        lines.append(f"{self._pad(level + 1)}right:")
        self._visit(node.right, lines, level + 2)

    def _visit_Literal(self, node: Literal, lines: list[str], level: int) -> None:
        type_name = type(node.value).__name__
        lines.append(f"{self._pad(level)}Literal  {node.value!r}  ({type_name})")

    def _visit_Identifier(self, node: Identifier, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}Identifier  {node.name!r}")

    def _visit_unknown(self, node: ASTNode, lines: list[str], level: int) -> None:
        lines.append(f"{self._pad(level)}??? Unknown node: {type(node).__name__}")