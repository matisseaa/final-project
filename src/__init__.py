from .methods_of_approx import central_difference, simpson_rule, trapezoidal_rule
from .functions import ExpressionFunction, MathFunction, Polynomial
from .models import Interval, IterationRecord, ReportArtifacts, RootResult
from .solvers import BisectionSolver, NewtonSolver, SecantSolver, build_solver
from .workflow import demo_config, run_full_report

__all__ = [
    "BisectionSolver",
    "ExpressionFunction",
    "Interval",
    "IterationRecord",
    "MathFunction",
    "NewtonSolver",
    "Polynomial",
    "ReportArtifacts",
    "RootResult",
    "SecantSolver",
    "build_solver",
    "central_difference",
    "demo_config",
    "run_full_report",
    "simpson_rule",
    "trapezoidal_rule",
]

__version__ = "0.1.0"