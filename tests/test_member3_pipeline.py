from __future__ import annotations

import unittest

from components.pipeline import run_pipeline
from components.type_checker import TypeCheckError


class Member3PipelineTests(unittest.TestCase):
    def test_while_loop_prints_each_iteration(self) -> None:
        source = """
x = 3;
while (x != 0) {
    print(x);
    x = x - 1;
}
"""

        result = run_pipeline(source)

        self.assertEqual(result.outputs, ["3 : Integer", "2 : Integer", "1 : Integer"])

    def test_assignment_type_mismatch_raises_error(self) -> None:
        source = """
x = 5;
x = \"hello\";
"""

        with self.assertRaises(TypeCheckError):
            run_pipeline(source)

    def test_function_call_inferrs_parameter_and_return_types(self) -> None:
        source = """
def add(a, b) {
    return a + b;
}

result = add(2, 3.5);
print(result);
"""

        result = run_pipeline(source)

        self.assertEqual(result.outputs, ["5.5 : Float"])
        self.assertIn("result       variable   Float", result.checked_scope.format_table())


    def test_unary_minus_integer(self) -> None:
        source = "x = -5; print(x);"
        result = run_pipeline(source)
        self.assertEqual(result.outputs, ["-5 : Integer"])

    def test_unary_minus_float(self) -> None:
        source = "y = -3.14; print(y);"
        result = run_pipeline(source)
        self.assertEqual(result.outputs, ["-3.14 : Float"])

    def test_unary_minus_variable(self) -> None:
        source = "x = 10; y = -x; print(y);"
        result = run_pipeline(source)
        self.assertEqual(result.outputs, ["-10 : Integer"])

    def test_unary_minus_in_expression(self) -> None:
        source = "x = 3 + -2; print(x);"
        result = run_pipeline(source)
        self.assertEqual(result.outputs, ["1 : Integer"])


if __name__ == "__main__":
    unittest.main()