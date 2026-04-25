import pytest

from numerical_workbench.parsers import (
    compile_expression,
    parse_polynomial,
    parse_interval_spec
)
from numerical_workbench.exceptions import ParseError, EvaluationError
from numerical_workbench.functions import Polynomial
from numerical_workbench.models import Interval


# compile_expression tests

def test_compile_expression_basic():
    f = compile_expression("x + 1")
    assert f(2) == 3


def test_compile_expression_power():
    f = compile_expression("x^2")
    assert f(3) == 9


def test_compile_expression_trig():
    f = compile_expression("sin(x)")
    assert f(0) == pytest.approx(0.0)


def test_compile_expression_constant():
    f = compile_expression("5")
    assert f(10) == 5


def test_compile_expression_invalid_syntax():
    with pytest.raises(ParseError):
        compile_expression("x + ")


def test_compile_expression_invalid_name():
    with pytest.raises(ParseError):
        compile_expression("y + 1")


def test_compile_expression_invalid_function():
    with pytest.raises(ParseError):
        compile_expression("unknown(x)")


def test_compile_expression_malicious_code():
    with pytest.raises(ParseError):
        compile_expression("__import__('os').system('rm -rf /')")


def test_compile_expression_division_by_zero():
    f = compile_expression("1/x")

    with pytest.raises(EvaluationError):
        f(0)

# parse_polynomial tests

def test_parse_polynomial_basic():
    p = parse_polynomial("1 + 2x + 3x^2")

    assert isinstance(p, Polynomial)
    assert p.coefficients == (1.0, 2.0, 3.0)


def test_parse_polynomial_with_spaces():
    p = parse_polynomial(" 1 + 2x + 3x^2 ")

    assert p.coefficients == (1.0, 2.0, 3.0)


def test_parse_polynomial_negative_terms():
    p = parse_polynomial("1 - 2x + 3x^2")

    assert p.coefficients == (1.0, -2.0, 3.0)


def test_parse_polynomial_constant_only():
    p = parse_polynomial("5")

    assert p.coefficients == (5.0,)


def test_parse_polynomial_only_x():
    p = parse_polynomial("x")

    assert p.coefficients == (0.0, 1.0)


def test_parse_polynomial_high_degree():
    p = parse_polynomial("x^5")

    assert p.coefficients[5] == 1.0


def test_parse_polynomial_empty():
    with pytest.raises(ParseError):
        parse_polynomial("")


def test_parse_polynomial_invalid_exponent():
    with pytest.raises(ParseError):
        parse_polynomial("2x^a")


def test_parse_polynomial_wrong_format():
    with pytest.raises(ParseError):
        parse_polynomial("2x**2")

# parse_interval_spec tests

def test_parse_interval_basic():
    interval = parse_interval_spec("0:2")

    assert isinstance(interval, Interval)
    assert interval.left == 0
    assert interval.right == 2


def test_parse_interval_with_spaces():
    interval = parse_interval_spec("  -1 :  3 ")

    assert interval.left == -1
    assert interval.right == 3


def test_parse_interval_invalid_format():
    with pytest.raises(ParseError):
        parse_interval_spec("0-2")


def test_parse_interval_non_numeric():
    with pytest.raises(ParseError):
        parse_interval_spec("a:b")