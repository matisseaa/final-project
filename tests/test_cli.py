import pytest
import sys
from numerical_workbench.cli import turn_into_dictionary, main

# turn_into_dictionary tests

def test_turn_into_dictionary_basic():
    class Args:
        function_kind = "polynomial"
        expression = "x^2"

    args = Args()

    result = turn_into_dictionary(args)

    assert result["kind"] == "polynomial"
    assert result["expression"] == "x^2"

# CLI main tests

def test_cli_show_demo_config(capsys, monkeypatch):
    test_args = [
        "prog",
        "show-demo-config",
        "--kind",
        "polynomial"
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()

    assert "function" in captured.out


def test_cli_solve_root(capsys, monkeypatch):
    test_args = [
        "prog",
        "solve-root",
        "--function-kind", "polynomial",
        "--expression", "x^2 - 1",
        "--method", "bisection",
        "--interval", "0:2"
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()

    assert "root" in captured.out


def test_cli_integrate(capsys, monkeypatch):
    test_args = [
        "prog",
        "integrate",
        "--function-kind", "polynomial",
        "--expression", "x",
        "--interval", "0:1"
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()

    assert "trapezoidal" in captured.out
    assert "simpson" in captured.out


def test_cli_report(tmp_path, capsys, monkeypatch):
    test_args = [
        "prog",
        "report",
        "--output-dir", str(tmp_path)
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()

    assert "output_directory" in captured.out

# edge cases

def test_cli_invalid_command(monkeypatch):
    test_args = ["prog"]

    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit):
        main()


def test_cli_invalid_expression(capsys, monkeypatch):
    test_args = [
        "prog",
        "solve-root",
        "--function-kind", "expression",
        "--expression", "1/0",
        "--method", "bisection",
        "--interval", "0:2"
    ]

    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()

    assert "Error" in captured.out