import pytest
from numerical_workbench.solvers import (
    BisectionSolver,
    NewtonSolver,
    SecantSolver,
    build_solver
)
from numerical_workbench.functions import Polynomial
from numerical_workbench.models import Interval
from numerical_workbench.exceptions import SolverError, ValidationError

# BisectionSolver tests

def test_bisection_basic():
    p = Polynomial([-1, 0, 1])  # x^2 - 1
    interval = Interval(0, 2)

    solver = BisectionSolver(limit = 1e-6, max_iterations = 100)
    result = solver.solve(p, interval = interval)

    assert result.converged is True
    assert result.root == pytest.approx(1, rel = 1e-4)


def test_bisection_no_sign_change():
    p = Polynomial([1, 0, 1])  # x^2 + 1 (no real roots)
    interval = Interval(0, 2)

    solver = BisectionSolver()

    with pytest.raises(SolverError):
        list(solver.iterate(p, interval = interval))


def test_bisection_endpoint_root():
    p = Polynomial([-1, 1])  # x - 1
    interval = Interval(1, 2)

    solver = BisectionSolver()
    result = solver.solve(p, interval = interval)

    assert result.root == pytest.approx(1)

# NewtonSolver tests

def test_newton_basic():
    p = Polynomial([-1, 0, 1])  # x^2 - 1

    solver = NewtonSolver(limit = 1e-6, max_iterations = 50)
    result = solver.solve(p, initial_guesses = (1.5,))

    assert result.converged is True
    assert result.root == pytest.approx(1, rel = 1e-4)


def test_newton_with_interval():
    p = Polynomial([-1, 0, 1])
    interval = Interval(0, 2)

    solver = NewtonSolver()
    result = solver.solve(p, interval = interval)

    assert result.converged is True


def test_newton_derivative_zero_error():
    p = Polynomial([0, 0, 1])  # x^2

    solver = NewtonSolver()

    with pytest.raises(SolverError):
        list(solver.iterate(p, initial_guesses = (0.0,)))


def test_newton_missing_inputs():
    p = Polynomial([1, 2])

    solver = NewtonSolver()

    with pytest.raises(SolverError):
        list(solver.iterate(p))

# SecantSolver tests

def test_secant_basic():
    p = Polynomial([-1, 0, 1])  # x^2 - 1

    solver = SecantSolver(limit = 1e-6, max_iterations = 50)
    result = solver.solve(p, initial_guesses = (0.5, 2.0))

    assert result.converged is True
    assert result.root == pytest.approx(1, rel = 1e-4)


def test_secant_with_interval():
    p = Polynomial([-1, 0, 1])
    interval = Interval(0, 2)

    solver = SecantSolver()
    result = solver.solve(p, interval = interval)

    assert result.converged is True


def test_secant_division_by_zero_error():
    p = Polynomial([1])  # constant --> f(x) is always the same

    solver = SecantSolver()

    with pytest.raises(SolverError):
        list(solver.iterate(p, initial_guesses = (1.0, 1.0)))


def test_secant_missing_inputs():
    p = Polynomial([1, 2])

    solver = SecantSolver()

    with pytest.raises(SolverError):
        list(solver.iterate(p))

# RootSolver base validation tests

def test_solver_invalid_limit():
    with pytest.raises(ValidationError):
        BisectionSolver(limit = 0)


def test_solver_invalid_iterations():
    with pytest.raises(ValidationError):
        BisectionSolver(max_iterations = 0)

# build_solver tests

def test_build_solver_bisection():
    solver = build_solver("bisection")
    assert isinstance(solver, BisectionSolver)


def test_build_solver_newton():
    solver = build_solver("newton")
    assert isinstance(solver, NewtonSolver)


def test_build_solver_secant():
    solver = build_solver("secant")
    assert isinstance(solver, SecantSolver)


def test_build_solver_invalid_name():
    with pytest.raises(ValidationError):
        build_solver("unknown_method")