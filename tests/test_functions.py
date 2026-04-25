import pytest
import numpy as np

from src.functions import MathFunction, Polynomial, ExpressionFunction
from src.models import Interval
from src.exceptions import EvaluationError


# dummy class for testing MathFunction

class DummyFunction(MathFunction):
    def __init__(self):
        super().__init__("dummy")

    def evaluate_scalar(self, x: float) -> float:
        return x ** 2

# MathFunction tests

def test_mathfunction_call_scalar():
    f = DummyFunction()
    assert f(2) == 4


def test_mathfunction_call_array():
    f = DummyFunction()
    result = f(np.array([1, 2, 3]))

    assert isinstance(result, np.ndarray)
    assert np.allclose(result, [1, 4, 9])


def test_mathfunction_derivative_approx():
    f = DummyFunction()  # f(x) = x^2  f'(x)=2x
    result = f.derivative(2)

    assert result == pytest.approx(4, rel = 1e-3)


def test_mathfunction_sample():
    f = DummyFunction()
    interval = Interval(0, 2)

    xs, ys = f.sample(interval, values = 5)

    assert len(xs) == 5
    assert len(ys) == 5
    assert ys[0] == 0


def test_mathfunction_description():
    f = DummyFunction()
    assert f.description() == "dummy"


def test_mathfunction_str():
    f = DummyFunction()
    assert str(f) == "dummy"

# Polynomial tests

def test_polynomial_creation_and_degree():
    p = Polynomial([1, 2, 3])
    assert p.degree == 2


def test_polynomial_trim_coefficients():
    p = Polynomial([1, 2, 0, 0])
    assert p.coefficients == (1.0, 2.0)


def test_polynomial_evaluate_scalar_basic():
    p = Polynomial([1, 2, 3])

    assert p.evaluate_scalar(0) == 1
    assert p.evaluate_scalar(1) == 6
    assert p.evaluate_scalar(2) == 17


def test_polynomial_evaluate_scalar_negative():
    p = Polynomial([0, 1])
    assert p.evaluate_scalar(-3) == -3


def test_polynomial_evaluate_scalar_float():
    p = Polynomial([1, 0, 1])
    assert p.evaluate_scalar(0.5) == pytest.approx(1.25)


def test_polynomial_derivative_polynomial():
    p = Polynomial([1, 2, 3])
    dp = p.derivative_polynomial()

    assert dp.coefficients == (2.0, 6.0)


def test_polynomial_derivative_polynomial_constant():
    p = Polynomial([5])
    dp = p.derivative_polynomial()

    assert dp.coefficients == (0.0,)


def test_polynomial_derivative_evaluation():
    p = Polynomial([1, 2, 3])
    assert p.derivative(1) == 8


def test_polynomial_add():
    p1 = Polynomial([1, 2])
    p2 = Polynomial([3, 4])

    result = p1 + p2
    assert result.coefficients == (4.0, 6.0)


def test_polynomial_add_different_lengths():
    p1 = Polynomial([1])
    p2 = Polynomial([1, 2, 3])

    result = p1 + p2
    assert result.coefficients == (2.0, 2.0, 3.0)


def test_polynomial_sub():
    p1 = Polynomial([5, 5])
    p2 = Polynomial([2, 3])

    result = p1 - p2
    assert result.coefficients == (3.0, 2.0)


def test_polynomial_mul_scalar():
    p = Polynomial([1, 2])
    result = p * 2

    assert result.coefficients == (2.0, 4.0)


def test_polynomial_rmul_scalar():
    p = Polynomial([1, 2])
    result = 2 * p

    assert result.coefficients == (2.0, 4.0)


def test_polynomial_mul_polynomial():
    p1 = Polynomial([1, 1])
    p2 = Polynomial([1, 1])

    result = p1 * p2
    assert result.coefficients == (1.0, 2.0, 1.0)


def test_polynomial_equality_true():
    p1 = Polynomial([1, 2, 3])
    p2 = Polynomial([1, 2, 3])

    assert p1 == p2


def test_polynomial_equality_false():
    p1 = Polynomial([1, 2])
    p2 = Polynomial([1, 3])

    assert (p1 == p2) is False


def test_polynomial_equality_non_polynomial():
    p = Polynomial([1, 2])
    assert (p == 5) is False


def test_polynomial_str_basic():
    p = Polynomial([1, 2])
    result = str(p)

    assert "1.0" in result
    assert "2.0x" in result


def test_polynomial_str_zero():
    p = Polynomial([0, 0, 0])
    assert str(p) == "0"


def test_polynomial_description():
    p = Polynomial([1, 2])
    desc = p.description()

    assert "Polynomial" in desc

# ExpressionFunction tests

def test_expression_function_basic():
    f = ExpressionFunction("x + 1")
    assert f.evaluate_scalar(2) == 3


def test_expression_function_trig():
    f = ExpressionFunction("sin(x)")
    assert f.evaluate_scalar(0) == pytest.approx(0.0)


def test_expression_function_power():
    f = ExpressionFunction("x^2")
    assert f.evaluate_scalar(3) == 9


def test_expression_function_division_by_zero():
    f = ExpressionFunction("1/x")

    with pytest.raises(EvaluationError):
        f.evaluate_scalar(0)


def test_expression_function_description():
    f = ExpressionFunction("x + 1")
    assert "Expression" in f.description()


def test_expression_function_invalid_expression():
    with pytest.raises(Exception):
        ExpressionFunction("import os")