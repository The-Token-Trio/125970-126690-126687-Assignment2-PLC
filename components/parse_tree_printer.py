from __future__ import annotations

from dataclasses import dataclass, field

from components.ast_nodes import (
    ASTNode,
    Assign,
    BinaryOp,
    Block,
    FunctionCall,
    FunctionDef,
    Identifier,
    If,
    Literal,
    Program,
    Return,
    While,
)


@dataclass
class ParseTreeNode:
    label: str
    children: list["ParseTreeNode"] = field(default_factory=list)


class ParseTreePrinter:
    """Renders a textbook-style concrete parse tree using ASCII branches."""

    def print(self, node: Program) -> str:
        root = self._program_node(node)
        lines: list[str] = []
        self._render(root, lines, prefix="", is_last=True, is_root=True)
        return "\n".join(lines)

    def _render(
        self,
        node: ParseTreeNode,
        lines: list[str],
        prefix: str,
        is_last: bool,
        is_root: bool = False,
    ) -> None:
        if is_root:
            lines.append(node.label)
        else:
            branch = "`-- " if is_last else "|-- "
            lines.append(f"{prefix}{branch}{node.label}")

        child_prefix = prefix + ("    " if is_last else "|   ")
        for index, child in enumerate(node.children):
            self._render(
                child,
                lines,
                prefix=child_prefix if not is_root else "",
                is_last=index == len(node.children) - 1,
            )

    def _program_node(self, node: Program) -> ParseTreeNode:
        children = [self._statement_node(statement) for statement in node.statements]
        children.append(ParseTreeNode("EOF"))
        return ParseTreeNode("program", children)

    def _statement_node(self, node: ASTNode) -> ParseTreeNode:
        if isinstance(node, Assign):
            return ParseTreeNode("statement", [self._assignment_node(node)])
        if isinstance(node, If):
            return ParseTreeNode("statement", [self._if_node(node)])
        if isinstance(node, While):
            return ParseTreeNode("statement", [self._while_node(node)])
        if isinstance(node, FunctionDef):
            return ParseTreeNode("statement", [self._function_def_node(node)])
        if isinstance(node, Return):
            return ParseTreeNode("statement", [self._return_node(node)])
        return ParseTreeNode(
            "statement",
            [
                ParseTreeNode(
                    "expr_stmt",
                    [self._expr_node(node), ParseTreeNode("';'")],
                )
            ],
        )

    def _assignment_node(self, node: Assign) -> ParseTreeNode:
        return ParseTreeNode(
            "assignment",
            [
                ParseTreeNode(f"IDENTIFIER({node.name})"),
                ParseTreeNode("'='"),
                self._expr_node(node.value),
                ParseTreeNode("';'"),
            ],
        )

    def _if_node(self, node: If) -> ParseTreeNode:
        children = [
            ParseTreeNode("'if'"),
            ParseTreeNode("'('"),
            self._expr_node(node.condition),
            ParseTreeNode("')'"),
            self._block_node(node.then_block),
        ]
        if node.else_block is not None:
            children.extend([ParseTreeNode("'else'"), self._block_node(node.else_block)])
        return ParseTreeNode("if_stmt", children)

    def _while_node(self, node: While) -> ParseTreeNode:
        return ParseTreeNode(
            "while_stmt",
            [
                ParseTreeNode("'while'"),
                ParseTreeNode("'('"),
                self._expr_node(node.condition),
                ParseTreeNode("')'"),
                self._block_node(node.body),
            ],
        )

    def _function_def_node(self, node: FunctionDef) -> ParseTreeNode:
        return ParseTreeNode(
            "func_def",
            [
                ParseTreeNode("'def'"),
                ParseTreeNode(f"IDENTIFIER({node.name})"),
                ParseTreeNode("'('"),
                self._params_node(node.params),
                ParseTreeNode("')'"),
                self._block_node(node.body),
            ],
        )

    def _params_node(self, params: list[str]) -> ParseTreeNode:
        if not params:
            return ParseTreeNode("params", [ParseTreeNode("epsilon")])

        children: list[ParseTreeNode] = []
        for index, param in enumerate(params):
            children.append(ParseTreeNode(f"IDENTIFIER({param})"))
            if index < len(params) - 1:
                children.append(ParseTreeNode("','"))
        return ParseTreeNode("params", children)

    def _return_node(self, node: Return) -> ParseTreeNode:
        return ParseTreeNode(
            "return_stmt",
            [
                ParseTreeNode("'return'"),
                self._expr_node(node.expr),
                ParseTreeNode("';'"),
            ],
        )

    def _block_node(self, node: Block) -> ParseTreeNode:
        children = [ParseTreeNode("'{'")]
        children.extend(self._statement_node(statement) for statement in node.statements)
        children.append(ParseTreeNode("'}'"))
        return ParseTreeNode("block", children)

    def _expr_node(self, node: ASTNode) -> ParseTreeNode:
        if isinstance(node, BinaryOp) and node.op in {"==", "!="}:
            child = ParseTreeNode(
                "comparison",
                [
                    self._additive_node(node.left),
                    ParseTreeNode(f"'{node.op}'"),
                    self._additive_node(node.right),
                ],
            )
            return ParseTreeNode("expr", [child])
        return ParseTreeNode("expr", [self._additive_node(node)])

    def _additive_node(self, node: ASTNode) -> ParseTreeNode:
        if isinstance(node, BinaryOp) and node.op in {"+", "-", "+.", "-."}:
            return ParseTreeNode(
                "additive",
                [
                    self._additive_node(node.left),
                    ParseTreeNode(f"'{node.op}'"),
                    self._term_node(node.right),
                ],
            )
        return ParseTreeNode("additive", [self._term_node(node)])

    def _term_node(self, node: ASTNode) -> ParseTreeNode:
        if isinstance(node, BinaryOp) and node.op in {"*", "/", "*.", "/."}:
            return ParseTreeNode(
                "term",
                [
                    self._term_node(node.left),
                    ParseTreeNode(f"'{node.op}'"),
                    self._factor_node(node.right),
                ],
            )
        return ParseTreeNode("term", [self._factor_node(node)])

    def _factor_node(self, node: ASTNode) -> ParseTreeNode:
        if self._is_integer_unary_minus(node):
            binary = node
            assert isinstance(binary, BinaryOp)
            return ParseTreeNode("factor", [ParseTreeNode("'-'"), self._factor_node(binary.right)])
        if self._is_float_unary_minus(node):
            binary = node
            assert isinstance(binary, BinaryOp)
            return ParseTreeNode("factor", [ParseTreeNode("'-.'"), self._factor_node(binary.right)])
        if isinstance(node, Literal):
            return ParseTreeNode("factor", [ParseTreeNode(self._literal_label(node.value))])
        if isinstance(node, Identifier):
            return ParseTreeNode("factor", [ParseTreeNode(f"IDENTIFIER({node.name})")])
        if isinstance(node, FunctionCall):
            return ParseTreeNode("factor", [self._function_call_node(node)])
        return ParseTreeNode(
            "factor",
            [ParseTreeNode("'('"), self._expr_node(node), ParseTreeNode("')'")],
        )

    def _function_call_node(self, node: FunctionCall) -> ParseTreeNode:
        return ParseTreeNode(
            "function_call",
            [
                ParseTreeNode(f"IDENTIFIER({node.name})"),
                ParseTreeNode("'('"),
                self._args_node(node.args),
                ParseTreeNode("')'"),
            ],
        )

    def _args_node(self, args: list[ASTNode]) -> ParseTreeNode:
        if not args:
            return ParseTreeNode("args", [ParseTreeNode("epsilon")])

        children: list[ParseTreeNode] = []
        for index, arg in enumerate(args):
            children.append(self._expr_node(arg))
            if index < len(args) - 1:
                children.append(ParseTreeNode("','"))
        return ParseTreeNode("args", children)

    @staticmethod
    def _is_integer_unary_minus(node: ASTNode) -> bool:
        return (
            isinstance(node, BinaryOp)
            and node.op == "-"
            and isinstance(node.left, Literal)
            and node.left.value == 0
        )

    @staticmethod
    def _is_float_unary_minus(node: ASTNode) -> bool:
        return (
            isinstance(node, BinaryOp)
            and node.op == "-."
            and isinstance(node.left, Literal)
            and node.left.value == 0.0
        )

    @staticmethod
    def _literal_label(value: object) -> str:
        if isinstance(value, bool):
            return f"BOOL_LITERAL({'true' if value else 'false'})"
        if isinstance(value, int):
            return f"INT_LITERAL({value})"
        if isinstance(value, float):
            return f"FLOAT_LITERAL({value})"
        if isinstance(value, str):
            return f'STRING_LITERAL("{value}")'
        return f"LITERAL({value!r})"
