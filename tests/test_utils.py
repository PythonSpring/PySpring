

import pytest
from py_spring.core.utils import check_type_hints_for_callable, TypeHintsNotProvidedError, check_type_hints_for_class


class TestCheckTypeHintsForCallable:
    def test_function_with_argument_type_hints_but_no_return_type(self):
        def test_func(a: int, b: str):
            pass  # No return type hint
        with pytest.raises(TypeHintsNotProvidedError, match="Type hints for 'return type' not provided for the function"):
            check_type_hints_for_callable(test_func)

    def test_function_with_no_arguments(self):
        def test_func() -> None:
            pass
        # No exception should be raised for a function with no arguments
        check_type_hints_for_callable(test_func)

    def test_function_with_correct_type_hints(self):
        def test_func(a: int, b: str) -> None:
            pass
        # No exception should be raised
        check_type_hints_for_callable(test_func)

    def test_function_with_no_type_hints(self):
        def test_func(a, b) -> None:
            pass
        with pytest.raises(TypeHintsNotProvidedError, match="Number of type hints does not match the number of arguments"):
            check_type_hints_for_callable(test_func)

    def test_function_with_mismatched_type_hints(self):
        def test_func(a: int, b, c) -> None:
            pass
        # Intentionally using only one type hint
        
        with pytest.raises(TypeHintsNotProvidedError, match="Number of type hints does not match the number of arguments in the function"):
            check_type_hints_for_callable(test_func)


class TestCheckTypeHintsForClass:
    def test_class_with_method_and_return_type_hints(self):
        class TestClass:
            def method(self, a: int, b: str) -> bool:
                return True

        # No exception should be raised
        check_type_hints_for_class(TestClass)

    def test_class_with_method_missing_return_type_hint(self):
        class TestClass:
            def method(self, a: int, b: str):
                pass  # No return type hint

        with pytest.raises(TypeHintsNotProvidedError, match="Type hints for 'return type' not provided for the function"):
            check_type_hints_for_class(TestClass)

    def test_class_with_method_missing_argument_type_hint(self):
        class TestClass:
            def method(self, a, b: str) -> bool:
                return True

        with pytest.raises(TypeHintsNotProvidedError, match="Number of type hints does not match the number of arguments in the function"):
            check_type_hints_for_class(TestClass)

    def test_class_with_method_having_no_arguments_but_return_type_hint(self):
        class TestClass:
            def method(self) -> bool:
                return True

        # No exception should be raised
        check_type_hints_for_class(TestClass)

    def test_class_with_method_having_no_type_hints(self):
        class TestClass:
            def method(self):
                pass  # No type hints at all

        with pytest.raises(TypeHintsNotProvidedError, match="Type hints for 'return type' not provided for the function"):
            check_type_hints_for_class(TestClass)