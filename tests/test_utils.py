

import pytest
from py_spring.core.utils import checking_type_hints_for_callable, TypeHintsNotProvidedError


class TestFrameworkUtils:

    def test_function_with_argument_type_hints_but_no_return_type(self):
        def test_func(a: int, b: str):
            pass  # No return type hint
        with pytest.raises(TypeHintsNotProvidedError, match="Type hints for 'return type' not provided for the function"):
            checking_type_hints_for_callable(test_func)

    def test_function_with_no_arguments(self):
        def test_func() -> None:
            pass
        # No exception should be raised for a function with no arguments
        checking_type_hints_for_callable(test_func)

    def test_function_with_correct_type_hints(self):
        def test_func(a: int, b: str) -> None:
            pass
        # No exception should be raised
        checking_type_hints_for_callable(test_func)

    def test_function_with_no_type_hints(self):
        def test_func(a, b) -> None:
            pass
        with pytest.raises(TypeHintsNotProvidedError, match="Number of type hints does not match the number of arguments"):
            checking_type_hints_for_callable(test_func)

    def test_function_with_mismatched_type_hints(self):
        def test_func(a: int, b, c) -> None:
            pass
        # Intentionally using only one type hint
        
        with pytest.raises(TypeHintsNotProvidedError, match="Number of type hints does not match the number of arguments in the function"):
            checking_type_hints_for_callable(test_func)

