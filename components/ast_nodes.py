from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    """Base class for every AST node. Carries source location for diagnostics."""
    line: int = field(default=0, kw_only=True)
    column: int = field(default=0, kw_only=True)


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class Literal(ASTNode):
    """An integer, float, boolean, or string literal.

    Examples:  42   3.14   true   "hello"
    """
    value: int | float | bool | str


@dataclass
class Identifier(ASTNode):
    """A variable or function name used as an expression.

    Example:  x
    """
    name: str


@dataclass
class BinaryOp(ASTNode):
    """An arithmetic or comparison binary operation.

    op is one of: '+' '-' '*' '/' '==' '!='
    Example:  a + b   x == 0
    """
    op: str
    left: ASTNode
    right: ASTNode


@dataclass
class FunctionCall(ASTNode):
    """A call to a user-defined function.

    Example:  add(1, 2)
    """
    name: str
    args: list[ASTNode] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class Assign(ASTNode):
    """Variable assignment (first use infers type; later uses must match).

    Example:  x = 10;
    """
    name: str
    value: ASTNode


@dataclass
class Print(ASTNode):
    """Built-in print statement.

    Example:  print(x);
    """
    expr: ASTNode


@dataclass
class Return(ASTNode):
    """Return statement inside a function body.

    Example:  return result;
    """
    expr: ASTNode


@dataclass
class Block(ASTNode):
    """A brace-enclosed sequence of statements.

    Example:  { x = 1; print(x); }
    """
    statements: list[ASTNode] = field(default_factory=list)


@dataclass
class If(ASTNode):
    """If / optional else control flow.

    Example:  if (x != 0) { print(x); } else { print(0); }
    """
    condition: ASTNode
    then_block: Block
    else_block: Optional[Block]


@dataclass
class While(ASTNode):
    """While loop.

    Example:  while (x != 0) { x = x - 1; }
    """
    condition: ASTNode
    body: Block


@dataclass
class FunctionDef(ASTNode):
    """Function definition.

    Example:  def add(a, b) { return a + b; }

    Note: parameter types are unknown at parse time — Member 3's type checker
    will infer them from usage. We store only the parameter names here.
    """
    name: str
    params: list[str]
    body: Block


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

@dataclass
class Program(ASTNode):
    """Root node: the entire source file as a list of statements."""
    statements: list[ASTNode] = field(default_factory=list)