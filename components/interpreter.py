from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
    Print,
    Program,
    Return,
    While,
)
from components.symbol_table import LanguageType


class InterpreterError(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value: object) -> None:
        self.value = value


@dataclass
class _FunctionRuntime:
    node: FunctionDef


class _Environment:
    def __init__(self, parent: _Environment | None = None) -> None:
        self.parent = parent
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: str) -> object:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise InterpreterError(f"Undefined variable: {name}")

    def assign(self, name: str, value: object) -> None:
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None and self.parent.contains(name):
            self.parent.assign(name, value)
            return
        self.values[name] = value

    def contains(self, name: str) -> bool:
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.contains(name)
        return False


class Interpreter:
    def __init__(self, output_callback: Callable[[str], None] | None = None) -> None:
        self._functions: dict[str, _FunctionRuntime] = {}
        self._output_callback = output_callback or print

    def execute(self, program: Program) -> None:
        environment = _Environment()
        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                self._functions[statement.name] = _FunctionRuntime(node=statement)

        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                continue
            self._execute_statement(statement, environment)

    def _execute_statement(self, node: ASTNode, environment: _Environment) -> None:
        if isinstance(node, Assign):
            value = self._evaluate(node.value, environment)
            environment.assign(node.name, value)
            return

        if isinstance(node, Print):
            value = self._evaluate(node.expr, environment)
            self._output_callback(f"{self._format_value(value)} : {self._runtime_type(value).value}")
            return

        if isinstance(node, Return):
            raise _ReturnSignal(self._evaluate(node.expr, environment))

        if isinstance(node, If):
            condition = self._evaluate(node.condition, environment)
            if not isinstance(condition, bool):
                raise InterpreterError(self._error_at(node.condition, "If condition must evaluate to Boolean"))
            branch = node.then_block if condition else node.else_block
            if branch is not None:
                self._execute_block(branch, _Environment(parent=environment))
            return

        if isinstance(node, While):
            while True:
                condition = self._evaluate(node.condition, environment)
                if not isinstance(condition, bool):
                    raise InterpreterError(self._error_at(node.condition, "While condition must evaluate to Boolean"))
                if not condition:
                    break
                self._execute_block(node.body, _Environment(parent=environment))
            return

        if isinstance(node, Block):
            self._execute_block(node, _Environment(parent=environment))
            return

        if isinstance(node, FunctionCall):
            self._evaluate(node, environment)
            return

        raise InterpreterError(self._error_at(node, f"Unsupported statement node: {type(node).__name__}"))

    def _execute_block(self, block: Block, environment: _Environment) -> None:
        for statement in block.statements:
            self._execute_statement(statement, environment)

    def _evaluate(self, node: ASTNode, environment: _Environment) -> object:
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Identifier):
            return environment.get(node.name)

        if isinstance(node, BinaryOp):
            left_value = self._evaluate(node.left, environment)
            right_value = self._evaluate(node.right, environment)
            return self._evaluate_binary(node, left_value, right_value)

        if isinstance(node, FunctionCall):
            return self._call_function(node, environment)

        raise InterpreterError(self._error_at(node, f"Unsupported expression node: {type(node).__name__}"))

    def _call_function(self, node: FunctionCall, environment: _Environment) -> object:
        function_runtime = self._functions.get(node.name)
        if function_runtime is None:
            raise InterpreterError(self._error_at(node, f"Undefined function: {node.name}"))

        if len(node.args) != len(function_runtime.node.params):
            raise InterpreterError(
                self._error_at(
                    node,
                    f"Function '{node.name}' expects {len(function_runtime.node.params)} argument(s), got {len(node.args)}",
                )
            )

        call_environment = _Environment(parent=environment)
        argument_values = [self._evaluate(argument, environment) for argument in node.args]
        for parameter_name, argument_value in zip(function_runtime.node.params, argument_values, strict=False):
            call_environment.define(parameter_name, argument_value)

        try:
            self._execute_block(function_runtime.node.body, call_environment)
        except _ReturnSignal as signal:
            return signal.value
        return None

    def _evaluate_binary(self, node: BinaryOp, left_value: object, right_value: object) -> object:
        if node.op == "+":
            return left_value + right_value
        if node.op == "-":
            return left_value - right_value
        if node.op == "*":
            return left_value * right_value
        if node.op == "/":
            return left_value / right_value
        if node.op == "==":
            return left_value == right_value
        if node.op == "!=":
            return left_value != right_value
        raise InterpreterError(self._error_at(node, f"Unsupported operator: {node.op}"))

    @staticmethod
    def _format_value(value: object) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _runtime_type(value: object) -> LanguageType:
        if isinstance(value, bool):
            return LanguageType.BOOLEAN
        if isinstance(value, int):
            return LanguageType.INTEGER
        if isinstance(value, float):
            return LanguageType.FLOAT
        if isinstance(value, str):
            return LanguageType.STRING
        return LanguageType.VOID

    @staticmethod
    def _error_at(node: ASTNode, message: str) -> str:
        return f"[line {node.line}, col {node.column}] RuntimeError: {message}"