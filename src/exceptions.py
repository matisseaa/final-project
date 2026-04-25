from __future__ import annotations

class NumericalWorkbenchError(Exception):
    """base exception for the project."""


class ValidationError(NumericalWorkbenchError):
    """raised when user input or configuration values are invalid."""


class ParseError(NumericalWorkbenchError):
    """raised when text input cannot be parsed."""


class EvaluationError(NumericalWorkbenchError):
    """raised when a mathematical expression cannot be evaluated."""


class SolverError(NumericalWorkbenchError):
    """raised when a numerical solver fails."""


class ConfigurationError(NumericalWorkbenchError):
    """raised when a configuration file is incomplete or inconsistent."""
