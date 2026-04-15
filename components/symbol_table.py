from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LanguageType(Enum):
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    STRING = "String"
    VOID = "Void"


@dataclass
class Symbol:
    name: str
    symbol_type: LanguageType


@dataclass
class VariableSymbol(Symbol):
    initialized: bool = False


@dataclass
class FunctionSymbol(Symbol):
    parameters: list[tuple[str, LanguageType]] = field(default_factory=list)


class SymbolTableError(Exception):
    pass


class SymbolTable:
    def __init__(self, parent: SymbolTable | None = None) -> None:
        self.parent = parent
        self._symbols: dict[str, Symbol] = {}

    def define_variable(self, name: str, symbol_type: LanguageType, initialized: bool = False) -> VariableSymbol:
        if name in self._symbols:
            raise SymbolTableError(f"Symbol already defined in this scope: {name}")
        symbol = VariableSymbol(name=name, symbol_type=symbol_type, initialized=initialized)
        self._symbols[name] = symbol
        return symbol

    def define_function(
        self,
        name: str,
        return_type: LanguageType,
        parameters: list[tuple[str, LanguageType]],
    ) -> FunctionSymbol:
        if name in self._symbols:
            raise SymbolTableError(f"Symbol already defined in this scope: {name}")
        symbol = FunctionSymbol(name=name, symbol_type=return_type, parameters=parameters)
        self._symbols[name] = symbol
        return symbol

    def lookup(self, name: str) -> Symbol:
        symbol = self._symbols.get(name)
        if symbol is not None:
            return symbol
        if self.parent is not None:
            return self.parent.lookup(name)
        raise SymbolTableError(f"Undefined symbol: {name}")

    def exists_in_current_scope(self, name: str) -> bool:
        return name in self._symbols

    def child_scope(self) -> SymbolTable:
        return SymbolTable(parent=self)

    def set_initialized(self, name: str) -> None:
        symbol = self.lookup(name)
        if not isinstance(symbol, VariableSymbol):
            raise SymbolTableError(f"Cannot initialize non-variable symbol: {name}")
        symbol.initialized = True

    def snapshot(self) -> dict[str, Symbol]:
        return dict(self._symbols)

    def format_table(self) -> str:
        lines = [
            f"{'Name':<12} {'Kind':<10} {'Type':<10} {'Initialized':<12} Parameters",
            "-" * 72,
        ]

        for name, symbol in self._symbols.items():
            if isinstance(symbol, FunctionSymbol):
                params = ", ".join(f"{param_name}: {param_type.value}" for param_name, param_type in symbol.parameters)
                lines.append(
                    f"{name:<12} {'function':<10} {symbol.symbol_type.value:<10} {'-':<12} {params or '-'}"
                )
            elif isinstance(symbol, VariableSymbol):
                initialized = "yes" if symbol.initialized else "no"
                lines.append(
                    f"{name:<12} {'variable':<10} {symbol.symbol_type.value:<10} {initialized:<12} -"
                )
            else:
                lines.append(f"{name:<12} {'symbol':<10} {symbol.symbol_type.value:<10} {'-':<12} -")

        return "\n".join(lines)

