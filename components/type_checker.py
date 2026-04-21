from __future__ import annotations

from dataclasses import dataclass

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
from components.symbol_table import FunctionSymbol, LanguageType, SymbolTable, SymbolTableError, VariableSymbol


class TypeCheckError(Exception):
    pass


@dataclass
class _FunctionState:
    node: FunctionDef
    body_checked: bool = False


@dataclass
class _FunctionContext:
    name: str
    return_type: LanguageType | None = None


class TypeChecker:
    def __init__(self) -> None:
        self.global_scope = SymbolTable()
        self._functions: dict[str, _FunctionState] = {}
        self._active_calls: list[str] = []

    def check(self, program: Program) -> SymbolTable:
        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                self._register_function(statement)

        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                continue
            self._check_statement(statement, self.global_scope, None)

        return self.global_scope

    def _register_function(self, node: FunctionDef) -> None:
        if node.name in self._functions:
            raise TypeCheckError(self._error_at(node, f"Function '{node.name}' is already defined"))

        placeholder_parameters = [(param_name, LanguageType.VOID) for param_name in node.params]
        try:
            self.global_scope.define_function(node.name, LanguageType.VOID, placeholder_parameters)
        except SymbolTableError as error:
            raise TypeCheckError(self._error_at(node, str(error))) from error
        self._functions[node.name] = _FunctionState(node=node)

    def _check_statement(
        self,
        node: ASTNode,
        scope: SymbolTable,
        function_context: _FunctionContext | None,
    ) -> None:
        if isinstance(node, Assign):
            value_type = self._infer_expr_type(node.value, scope)
            self._assign_variable_type(scope, node, value_type)
            return

        if isinstance(node, Print):
            self._infer_expr_type(node.expr, scope)
            return

        if isinstance(node, Return):
            if function_context is None:
                raise TypeCheckError(self._error_at(node, "'return' is only valid inside a function"))
            expr_type = self._infer_expr_type(node.expr, scope)
            if function_context.return_type is None:
                function_context.return_type = expr_type
            elif function_context.return_type != expr_type:
                raise TypeCheckError(
                    self._error_at(
                        node,
                        f"Function '{function_context.name}' returns both {function_context.return_type.value} and {expr_type.value}",
                    )
                )
            return

        if isinstance(node, If):
            condition_type = self._infer_expr_type(node.condition, scope)
            if condition_type != LanguageType.BOOLEAN:
                raise TypeCheckError(self._error_at(node.condition, "If condition must have type Boolean"))
            self._check_block(node.then_block, scope.child_scope(), function_context)
            if node.else_block is not None:
                self._check_block(node.else_block, scope.child_scope(), function_context)
            return

        if isinstance(node, While):
            condition_type = self._infer_expr_type(node.condition, scope)
            if condition_type != LanguageType.BOOLEAN:
                raise TypeCheckError(self._error_at(node.condition, "While condition must have type Boolean"))
            self._check_block(node.body, scope.child_scope(), function_context)
            return

        if isinstance(node, Block):
            self._check_block(node, scope.child_scope(), function_context)
            return

        if isinstance(node, FunctionCall):
            self._infer_function_call_type(node, scope)
            return

        raise TypeCheckError(self._error_at(node, f"Unsupported statement node: {type(node).__name__}"))

    def _check_block(
        self,
        block: Block,
        scope: SymbolTable,
        function_context: _FunctionContext | None,
    ) -> None:
        for statement in block.statements:
            self._check_statement(statement, scope, function_context)

    def _infer_expr_type(self, node: ASTNode, scope: SymbolTable) -> LanguageType:
        if isinstance(node, Literal):
            return self._literal_type(node)

        if isinstance(node, Identifier):
            try:
                symbol = scope.lookup(node.name)
            except SymbolTableError as error:
                raise TypeCheckError(self._error_at(node, str(error))) from error
            if not isinstance(symbol, VariableSymbol):
                raise TypeCheckError(self._error_at(node, f"'{node.name}' is not a variable"))
            return symbol.symbol_type

        if isinstance(node, FunctionCall):
            return self._infer_function_call_type(node, scope)

        if isinstance(node, BinaryOp):
            left_type = self._infer_expr_type(node.left, scope)
            right_type = self._infer_expr_type(node.right, scope)
            return self._infer_binary_type(node, left_type, right_type)

        raise TypeCheckError(self._error_at(node, f"Unsupported expression node: {type(node).__name__}"))

    def _infer_function_call_type(self, node: FunctionCall, scope: SymbolTable) -> LanguageType:
        function_state = self._functions.get(node.name)
        if function_state is None:
            raise TypeCheckError(self._error_at(node, f"Undefined function: {node.name}"))
        if node.name in self._active_calls:
            raise TypeCheckError(self._error_at(node, f"Recursive function calls are not supported: {node.name}"))

        argument_types = [self._infer_expr_type(argument, scope) for argument in node.args]
        function_symbol = self._lookup_function_symbol(node)

        if len(argument_types) != len(function_symbol.parameters):
            raise TypeCheckError(
                self._error_at(
                    node,
                    f"Function '{node.name}' expects {len(function_symbol.parameters)} argument(s), got {len(argument_types)}",
                )
            )

        declared_parameter_types = [param_type for _, param_type in function_symbol.parameters]
        if all(param_type == LanguageType.VOID for param_type in declared_parameter_types):
            function_symbol.parameters = list(zip(function_state.node.params, argument_types, strict=False))
        else:
            for index, ((_, expected_type), actual_type) in enumerate(zip(function_symbol.parameters, argument_types, strict=False)):
                if expected_type != actual_type:
                    raise TypeCheckError(
                        self._error_at(
                            node.args[index],
                            f"Argument {index + 1} of '{node.name}' must be {expected_type.value}, got {actual_type.value}",
                        )
                    )

        if not function_state.body_checked:
            self._check_function_body(function_state, function_symbol)

        return function_symbol.symbol_type

    def _check_function_body(self, function_state: _FunctionState, function_symbol: FunctionSymbol) -> None:
        function_context = _FunctionContext(name=function_state.node.name)
        function_scope = self.global_scope.child_scope()
        for parameter_name, parameter_type in function_symbol.parameters:
            function_scope.define_variable(parameter_name, parameter_type, initialized=True)

        self._active_calls.append(function_state.node.name)
        try:
            self._check_block(function_state.node.body, function_scope, function_context)
        finally:
            self._active_calls.pop()

        function_symbol.symbol_type = function_context.return_type or LanguageType.VOID
        function_state.body_checked = True

    def _assign_variable_type(self, scope: SymbolTable, node: Assign, value_type: LanguageType) -> None:
        try:
            symbol = scope.lookup(node.name)
        except SymbolTableError:
            scope.define_variable(node.name, value_type, initialized=True)
            return

        if not isinstance(symbol, VariableSymbol):
            raise TypeCheckError(self._error_at(node, f"'{node.name}' is not a variable"))
        if symbol.symbol_type != value_type:
            raise TypeCheckError(
                self._error_at(
                    node,
                    f"Cannot assign {value_type.value} to variable '{node.name}' of type {symbol.symbol_type.value}",
                )
            )
        symbol.initialized = True

    def _infer_binary_type(
        self,
        node: BinaryOp,
        left_type: LanguageType,
        right_type: LanguageType,
    ) -> LanguageType:
        if node.op in {"+", "-", "*", "/"}:
            if not self._is_numeric(left_type) or not self._is_numeric(right_type):
                raise TypeCheckError(self._error_at(node, f"Operator '{node.op}' requires numeric operands"))
            if node.op == "/":
                return LanguageType.FLOAT
            if left_type == LanguageType.FLOAT or right_type == LanguageType.FLOAT:
                return LanguageType.FLOAT
            return LanguageType.INTEGER

        if node.op in {"==", "!="}:
            numeric_comparison = self._is_numeric(left_type) and self._is_numeric(right_type)
            boolean_comparison = left_type == right_type == LanguageType.BOOLEAN
            if not numeric_comparison and not boolean_comparison:
                raise TypeCheckError(
                    self._error_at(
                        node,
                        f"Operator '{node.op}' requires either two numeric operands or two Boolean operands",
                    )
                )
            return LanguageType.BOOLEAN

        raise TypeCheckError(self._error_at(node, f"Unsupported operator: {node.op}"))

    def _lookup_function_symbol(self, node: FunctionCall) -> FunctionSymbol:
        try:
            symbol = self.global_scope.lookup(node.name)
        except SymbolTableError as error:
            raise TypeCheckError(self._error_at(node, str(error))) from error
        if not isinstance(symbol, FunctionSymbol):
            raise TypeCheckError(self._error_at(node, f"'{node.name}' is not a function"))
        return symbol

    @staticmethod
    def _is_numeric(language_type: LanguageType) -> bool:
        return language_type in {LanguageType.INTEGER, LanguageType.FLOAT}

    @staticmethod
    def _literal_type(node: Literal) -> LanguageType:
        if isinstance(node.value, bool):
            return LanguageType.BOOLEAN
        if isinstance(node.value, int):
            return LanguageType.INTEGER
        if isinstance(node.value, float):
            return LanguageType.FLOAT
        if isinstance(node.value, str):
            return LanguageType.STRING
        raise TypeCheckError(f"Unsupported literal value: {node.value!r}")

    @staticmethod
    def _error_at(node: ASTNode, message: str) -> str:
        return f"[line {node.line}, col {node.column}] TypeError: {message}"