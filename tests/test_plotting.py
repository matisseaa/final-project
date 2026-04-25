import pytest
from pathlib import Path

from src.plotting import plot_function, plot_convergence, errorplot
from src.functions import Polynomial
from src.models import Interval, RootResult, IterationRecord

# plot_function tests

def test_plot_function_creates_file(tmp_path):
    p = Polynomial([0, 1])  # f(x) = x
    interval = Interval(0, 1)

    output = tmp_path / "plot.png"

    result = plot_function(p, interval, output)

    assert isinstance(result, Path)
    assert result.exists()


def test_plot_function_with_roots(tmp_path):
    p = Polynomial([-1, 0, 1])  # x^2 - 1
    interval = Interval(0, 2)

    output = tmp_path / "plot_roots.png"

    result = plot_function(p, interval, output, roots = [1.0])

    assert result.exists()

# plot_convergence tests

def test_plot_convergence_basic(tmp_path):
    records = [
        IterationRecord(iteration = 1, x = 1.0, fx = 0.1),
        IterationRecord(iteration = 2, x = 1.1, fx = 0.01),
    ]

    result = RootResult(
        solver_name = "test",
        root = 1.0,
        converged = True,
        iterations = 2,
        final_error = 0.01,
        time_taken = 0.1,
        history = records
    )

    output = tmp_path / "conv.png"

    path = plot_convergence([result], output)

    assert isinstance(path, Path)
    assert path.exists()


def test_plot_convergence_multiple_results(tmp_path):
    records1 = [
        IterationRecord(iteration = 1, x = 1.0, fx = 0.1),
        IterationRecord(iteration = 2, x = 1.1, fx = 0.01),
    ]

    records2 = [
        IterationRecord(iteration = 1, x = 2.0, fx = 0.2),
        IterationRecord(iteration = 2, x = 2.1, fx = 0.02),
    ]

    r1 = RootResult(
        solver_name = "method1",
        root = 1.0,
        converged = True,
        iterations = 2,
        final_error = 0.01,
        time_taken = 0.1,
        history = records1
    )

    r2 = RootResult(
        solver_name = "method2",
        root = 2.0,
        converged = True,
        iterations = 2,
        final_error = 0.02,
        time_taken = 0.1,
        history = records2
    )

    output = tmp_path / "multi.png"

    path = plot_convergence([r1, r2], output)

    assert path.exists()

# errorplot

def test_errorplot_alias(tmp_path):
    records = [
        IterationRecord(iteration = 1, x = 1.0, fx = 0.1),
        IterationRecord(iteration = 2, x = 1.1, fx = 0.01),
    ]

    result = RootResult(
        solver_name = "test",
        root = 1.0,
        converged = True,
        iterations = 2,
        final_error = 0.01,
        time_taken = 0.1,
        history = records
    )

    output = tmp_path / "errorplot.png"

    path = errorplot([result], output)

    assert path.exists()