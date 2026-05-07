from __future__ import annotations

import unittest

from components.interpreter import InterpreterError
from components.lexica import Lexer, LexerError
from components.parser import Parser, ParseError
from components.pipeline import run_pipeline
from components.symbol_table import LanguageType, SymbolTable, SymbolTableError
from components.tokens import TokenType
from components.type_checker import TypeCheckError


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class LexerTests(unittest.TestCase):
    """Tests for components/lexica.py — lexical analysis and tokenisation."""

    def test_integer_literal_token(self) -> None:
        tokens = Lexer("42").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[0].lexeme, "42")

    def test_float_literal_token(self) -> None:
        tokens = Lexer("3.14").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[0].lexeme, "3.14")

    def test_bool_literals_produce_bool_literal_tokens(self) -> None:
        tokens = Lexer("true false").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.BOOL_LITERAL)
        self.assertEqual(tokens[0].lexeme, "true")
        self.assertEqual(tokens[1].token_type, TokenType.BOOL_LITERAL)
        self.assertEqual(tokens[1].lexeme, "false")

    def test_keywords_produce_correct_token_types(self) -> None:
        tokens = Lexer("if else while def return").tokenize()
        expected = [
            TokenType.IF, TokenType.ELSE, TokenType.WHILE, TokenType.DEF, TokenType.RETURN,
        ]
        actual = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
        self.assertEqual(actual, expected)

    def test_identifier_not_confused_with_keyword(self) -> None:
        tokens = Lexer("iffy whileloop print").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].token_type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].token_type, TokenType.IDENTIFIER)

    def test_two_character_operators(self) -> None:
        tokens = Lexer("== !=").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.EQUAL_EQUAL)
        self.assertEqual(tokens[1].token_type, TokenType.BANG_EQUAL)

    def test_float_dot_operators_tokenised(self) -> None:
        tokens = Lexer("+. -. *. /.").tokenize()
        expected = [TokenType.PLUS_DOT, TokenType.MINUS_DOT, TokenType.STAR_DOT, TokenType.SLASH_DOT]
        actual = [t.token_type for t in tokens if t.token_type != TokenType.EOF]
        self.assertEqual(actual, expected)

    def test_float_literal_not_confused_with_dot_operator(self) -> None:
        # "3.14" must produce FLOAT_LITERAL, not INT_LITERAL followed by something
        tokens = Lexer("3.14").tokenize()
        self.assertEqual(tokens[0].token_type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[0].lexeme, "3.14")

    def test_source_position_tracked_across_lines(self) -> None:
        tokens = Lexer("x\ny").tokenize()
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[1].line, 2)

    def test_unexpected_character_raises_lexer_error(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("@").tokenize()

    def test_lone_exclamation_raises_lexer_error(self) -> None:
        with self.assertRaises(LexerError):
            Lexer("!5").tokenize()

    def test_unterminated_string_raises_lexer_error(self) -> None:
        with self.assertRaises(LexerError):
            Lexer('"hello').tokenize()


# ---------------------------------------------------------------------------
# Symbol table
# ---------------------------------------------------------------------------

class SymbolTableTests(unittest.TestCase):
    """Tests for components/symbol_table.py — scoped symbol table and semantic types."""

    def test_define_variable_and_lookup(self) -> None:
        table = SymbolTable()
        table.define_variable("x", LanguageType.INTEGER, initialized=True)
        symbol = table.lookup("x")
        self.assertEqual(symbol.symbol_type, LanguageType.INTEGER)

    def test_duplicate_variable_definition_raises_error(self) -> None:
        table = SymbolTable()
        table.define_variable("x", LanguageType.INTEGER)
        with self.assertRaises(SymbolTableError):
            table.define_variable("x", LanguageType.FLOAT)

    def test_duplicate_function_definition_raises_error(self) -> None:
        table = SymbolTable()
        table.define_function("f", LanguageType.INTEGER, [])
        with self.assertRaises(SymbolTableError):
            table.define_function("f", LanguageType.FLOAT, [])

    def test_lookup_in_parent_scope(self) -> None:
        parent = SymbolTable()
        parent.define_variable("x", LanguageType.INTEGER, initialized=True)
        child = parent.child_scope()
        symbol = child.lookup("x")
        self.assertEqual(symbol.symbol_type, LanguageType.INTEGER)

    def test_undefined_symbol_raises_error(self) -> None:
        table = SymbolTable()
        with self.assertRaises(SymbolTableError):
            table.lookup("z")

    def test_format_table_contains_variable_row(self) -> None:
        table = SymbolTable()
        table.define_variable("counter", LanguageType.INTEGER, initialized=True)
        output = table.format_table()
        self.assertIn("counter", output)
        self.assertIn("variable", output)
        self.assertIn("Integer", output)

    def test_format_table_contains_function_row(self) -> None:
        table = SymbolTable()
        table.define_function("add", LanguageType.INTEGER, [("a", LanguageType.INTEGER)])
        output = table.format_table()
        self.assertIn("add", output)
        self.assertIn("function", output)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ParserTests(unittest.TestCase):
    """Tests for components/parser.py — recursive-descent parsing."""

    def _parse(self, source: str):
        return Parser(Lexer(source).tokenize()).parse()

    def test_missing_semicolon_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            self._parse("x = 5")

    def test_unclosed_brace_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            self._parse("if (true) { x = 1;")

    def test_operator_precedence_mul_before_add(self) -> None:
        # 2 + 3 * 4 must be 14, not 20
        result = run_pipeline("x = 2 + 3 * 4; print(x);")
        self.assertEqual(result.outputs, ["14 : Integer"])

    def test_operator_left_associativity(self) -> None:
        # 10 - 3 - 2 must be 5 (left-assoc), not 9
        result = run_pipeline("x = 10 - 3 - 2; print(x);")
        self.assertEqual(result.outputs, ["5 : Integer"])

    def test_parentheses_override_precedence(self) -> None:
        # (2 + 3) * 4 must be 20
        result = run_pipeline("x = (2 + 3) * 4; print(x);")
        self.assertEqual(result.outputs, ["20 : Integer"])

    def test_float_operator_precedence_mul_before_add(self) -> None:
        # 1.0 +. 2.0 *. 3.0 must be 7.0 (*.  binds tighter than +.)
        result = run_pipeline("x = 1.0 +. 2.0 *. 3.0; print(x);")
        self.assertEqual(result.outputs, ["7.0 : Float"])

    def test_pipeline_exposes_parse_tree_and_ast(self) -> None:
        result = run_pipeline("x = 5; print(x);")
        self.assertIn("program", result.parse_tree_text)
        self.assertIn("assignment", result.parse_tree_text)
        self.assertIn("additive", result.parse_tree_text)
        self.assertIn("term", result.parse_tree_text)
        self.assertIn("factor", result.parse_tree_text)
        self.assertIn("function_call", result.parse_tree_text)
        self.assertIn("Program", result.ast_text)
        self.assertIn("Assign", result.ast_text)
        self.assertIn("FunctionCall  'print'", result.ast_text)


# ---------------------------------------------------------------------------
# Type checker
# ---------------------------------------------------------------------------

class TypeCheckerTests(unittest.TestCase):
    """Tests for components/type_checker.py — static type inference and checking."""

    def test_integer_arithmetic_stays_integer(self) -> None:
        result = run_pipeline("x = 3 + 4; print(x);")
        self.assertEqual(result.outputs, ["7 : Integer"])

    def test_division_always_produces_integer(self) -> None:
        # integer / integer -> Integer (no implicit float conversion)
        result = run_pipeline("x = 10 / 2; print(x);")
        self.assertEqual(result.outputs, ["5 : Integer"])

    def test_float_dot_operators_produce_float(self) -> None:
        result = run_pipeline("x = 1.0 +. 2.5; print(x);")
        self.assertEqual(result.outputs, ["3.5 : Float"])

    def test_float_subtraction_produces_float(self) -> None:
        result = run_pipeline("x = 5.0 -. 1.5; print(x);")
        self.assertEqual(result.outputs, ["3.5 : Float"])

    def test_float_multiplication_produces_float(self) -> None:
        result = run_pipeline("x = 2.0 *. 3.0; print(x);")
        self.assertEqual(result.outputs, ["6.0 : Float"])

    def test_float_division_produces_float(self) -> None:
        result = run_pipeline("x = 9.0 /. 4.0; print(x);")
        self.assertEqual(result.outputs, ["2.25 : Float"])

    def test_integer_with_float_op_raises_type_error(self) -> None:
        # +. requires Float operands; integers must not be accepted
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = 2 +. 3; print(x);")

    def test_mixed_int_float_addition_raises_type_error(self) -> None:
        # Integer + Float is no longer valid; must use +.
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = 1 + 2.5; print(x);")

    def test_string_variable_type_inferred(self) -> None:
        result = run_pipeline('x = "hello"; print(x);')
        self.assertEqual(result.outputs, ['"hello" : String'])

    def test_boolean_literal_type_inferred(self) -> None:
        result = run_pipeline("x = true; print(x);")
        self.assertEqual(result.outputs, ["true : Boolean"])

    def test_boolean_equality_raises_type_error(self) -> None:
        # Boolean == Boolean is not allowed; == only accepts arithmetic operands
        with self.assertRaises(TypeCheckError):
            run_pipeline('x = true; if (x == false) { print("then"); } else { print("else"); }')

    def test_mixed_int_float_equality_raises_type_error(self) -> None:
        # == and != must not accept mixed Integer/Float (no overloading)
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = 5; y = 3.14; if (x == y) { print(x); }")

    def test_mixed_int_float_inequality_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = 5; y = 3.14; if (x != y) { print(x); }")

    def test_arithmetic_on_string_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline('x = "a" + 1;')

    def test_if_non_boolean_condition_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("if (1) { x = 2; }")

    def test_while_non_boolean_condition_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = 0; while (x) { x = x + 1; }")

    def test_assignment_type_mismatch_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline('x = 5; x = "hello";')

    def test_undefined_variable_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("print(z);")

    def test_function_wrong_arg_count_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("def f(a) { return a; } f(1, 2);")

    def test_function_arg_type_mismatch_raises_type_error(self) -> None:
        # first call infers a: Integer; second call with String must fail
        with self.assertRaises(TypeCheckError):
            run_pipeline('def f(a) { return a; } f(1); f("hello");')

    def test_uncalled_function_body_type_error_is_caught(self) -> None:
        # type error inside body must be detected even if function is never called
        with self.assertRaises(TypeCheckError):
            run_pipeline('def bad() { y = "hello" + 1; }')

    def test_valid_uncalled_function_does_not_raise(self) -> None:
        # a well-typed but uncalled function should not raise
        result = run_pipeline("def add(a, b) { return a + b; }")
        self.assertEqual(result.outputs, [])


# ---------------------------------------------------------------------------
# Integration (full pipeline)
# ---------------------------------------------------------------------------

class IntegrationTests(unittest.TestCase):
    """End-to-end tests through all four pipeline stages."""

    # --- Unary minus ---

    def test_unary_minus_integer(self) -> None:
        result = run_pipeline("x = -5; print(x);")
        self.assertEqual(result.outputs, ["-5 : Integer"])

    def test_unary_minus_float(self) -> None:
        result = run_pipeline("y = -. 3.14; print(y);")
        self.assertEqual(result.outputs, ["-3.14 : Float"])

    def test_unary_minus_dot_variable(self) -> None:
        result = run_pipeline("x = 1.5; y = -. x; print(y);")
        self.assertEqual(result.outputs, ["-1.5 : Float"])

    def test_unary_minus_variable(self) -> None:
        result = run_pipeline("x = 10; y = -x; print(y);")
        self.assertEqual(result.outputs, ["-10 : Integer"])

    def test_unary_minus_inside_expression(self) -> None:
        result = run_pipeline("x = 3 + -2; print(x);")
        self.assertEqual(result.outputs, ["1 : Integer"])

    # --- Control flow ---

    def test_if_then_branch_executes(self) -> None:
        result = run_pipeline(
            'x = 5; if (x == 5) { print("yes"); } else { print("no"); }'
        )
        self.assertEqual(result.outputs, ['"yes" : String'])

    def test_if_else_branch_executes_when_condition_false(self) -> None:
        result = run_pipeline(
            'x = 0; if (x == 5) { print("yes"); } else { print("no"); }'
        )
        self.assertEqual(result.outputs, ['"no" : String'])

    def test_while_loop_executes_repeatedly(self) -> None:
        result = run_pipeline("x = 3; while (x != 0) { print(x); x = x - 1; }")
        self.assertEqual(result.outputs, ["3 : Integer", "2 : Integer", "1 : Integer"])

    # --- Division by zero ---

    def test_integer_division_by_zero_raises_error(self) -> None:
        with self.assertRaises(InterpreterError):
            run_pipeline("x = 10 / 0; print(x);")

    def test_float_division_by_zero_raises_error(self) -> None:
        with self.assertRaises(InterpreterError):
            run_pipeline("x = 10.0 /. 0.0; print(x);")

    # --- Functions ---

    def test_function_integer_return(self) -> None:
        result = run_pipeline("def square(n) { return n * n; } print(square(7));")
        self.assertEqual(result.outputs, ["49 : Integer"])

    def test_function_type_inference(self) -> None:
        result = run_pipeline(
            "def add(a, b) { return a +. b; } result = add(2.0, 3.5); print(result);"
        )
        self.assertEqual(result.outputs, ["5.5 : Float"])
        self.assertIn("result       variable   Float", result.checked_scope.format_table())

    def test_function_value_parameter_passing(self) -> None:
        # Modifying a parameter inside a function must not affect the caller's variable
        result = run_pipeline(
            "def inc(a) { a = a + 1; return a; } x = 10; y = inc(x); print(x); print(y);"
        )
        self.assertEqual(result.outputs, ["10 : Integer", "11 : Integer"])

    def test_nested_function_calls(self) -> None:
        result = run_pipeline(
            "def add(a, b) { return a + b; } print(add(add(1, 2), 3));"
        )
        self.assertEqual(result.outputs, ["6 : Integer"])

    # --- print() with all four types ---

    def test_print_integer(self) -> None:
        result = run_pipeline("print(42);")
        self.assertEqual(result.outputs, ["42 : Integer"])

    def test_print_float(self) -> None:
        result = run_pipeline("print(3.14);")
        self.assertEqual(result.outputs, ["3.14 : Float"])

    def test_print_boolean(self) -> None:
        result = run_pipeline("print(true);")
        self.assertEqual(result.outputs, ["true : Boolean"])

    def test_print_string(self) -> None:
        result = run_pipeline('print("plc");')
        self.assertEqual(result.outputs, ['"plc" : String'])

    # --- Boolean expressions as values ---

    def test_comparison_result_assigned_to_variable(self) -> None:
        result = run_pipeline("x = 5; y = 5; flag = (x == y); print(flag);")
        self.assertEqual(result.outputs, ["true : Boolean"])

    def test_comparison_result_printed_directly(self) -> None:
        result = run_pipeline("x = 10; print(x != 0);")
        self.assertEqual(result.outputs, ["true : Boolean"])

    def test_comparison_result_false(self) -> None:
        result = run_pipeline("a = 1; b = 2; eq = (a == b); print(eq);")
        self.assertEqual(result.outputs, ["false : Boolean"])

    # --- Reassignment ---

    def test_variable_can_be_reassigned_same_type(self) -> None:
        result = run_pipeline("x = 1; x = 2; x = 3; print(x);")
        self.assertEqual(result.outputs, ["3 : Integer"])

    def test_scope_isolation_if_block(self) -> None:
        # Variable defined inside an if-block must not be visible outside it
        with self.assertRaises(TypeCheckError):
            run_pipeline(
                "x = 1; if (x == 1) { inner = 99; } print(inner);"
            )

    def test_string_equality_raises_type_error(self) -> None:
        # == is only valid between arithmetic (Integer/Float) operands
        with self.assertRaises(TypeCheckError):
            run_pipeline('a = "hello"; b = "world"; if (a == b) { print(a); }')

    def test_integer_floor_division(self) -> None:
        # 7 / 2 must be 3 (floor), not 3.5
        result = run_pipeline("x = 7 / 2; print(x);")
        self.assertEqual(result.outputs, ["3 : Integer"])

    def test_void_function_assignment_raises_type_error(self) -> None:
        # Assigning the result of a void function (no return) must be a type error
        with self.assertRaises(TypeCheckError):
            run_pipeline("def greet() { print(42); } x = greet();")

    def test_builtin_print_assignment_raises_type_error(self) -> None:
        with self.assertRaises(TypeCheckError):
            run_pipeline("x = print(42);")


if __name__ == "__main__":
    unittest.main()
