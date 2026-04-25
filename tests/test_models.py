import pytest
from pathlib import Path

from src.models import Interval, IterationRecord, RootResult, ReportArtifacts
from src.exceptions import ValidationError

# Interval tests

def test_interval_valid():
    interval = Interval(0, 2)
    assert interval.left == 0
    assert interval.right == 2


def test_interval_invalid():
    with pytest.raises(ValidationError):
        Interval(2, 1)


def test_interval_equal_bounds_error():
    with pytest.raises(ValidationError):
        Interval(1, 1)


def test_interval_width():
    interval = Interval(1, 4)
    assert interval.width() == 3


def test_interval_midpoint():
    interval = Interval(0, 2)
    assert interval.midpoint() == 1


def test_interval_contains():
    interval = Interval(0, 2)
    assert interval.contains(1) is True
    assert interval.contains(0) is True
    assert interval.contains(2) is True
    assert interval.contains(3) is False


def test_interval_negative_values():
    interval = Interval(-5, -1)
    assert interval.width() == 4
    assert interval.contains(-3)


def test_interval_as_tuple():
    interval = Interval(1, 5)
    assert interval.as_tuple() == (1, 5)

# IterationRecord tests

def test_iteration_record_to_row():
    record = IterationRecord(
        iteration = 1,
        x = 2.0,
        fx = 0.5,
        error = 0.1,
        text = "test",
        extrainfo = {"extra": 42}
    )

    row = record.to_row()

    assert row["iteration"] == 1
    assert row["x"] == 2.0
    assert row["fx"] == 0.5
    assert row["error"] == 0.1
    assert row["text"] == "test"
    assert row["extra"] == 42


def test_iteration_record_no_extrainfo():
    record = IterationRecord(1, 0.0, 0.0)
    row = record.to_row()

    assert "iteration" in row
    assert "x" in row
    assert "fx" in row
    assert "error" in row
    assert "text" in row

# RootResult tests

def test_root_result_elapsed_seconds():
    result = RootResult(
        solver_name = "test",
        root = 1.0,
        converged = True,
        iterations = 5,
        final_error = 0.001,
        time_taken = 0.5,
        history = []
    )

    assert result.elapsed_seconds == 0.5


def test_root_result_history_rows():
    record = IterationRecord(1, 1.0, 0.0)
    result = RootResult(
        solver_name = "test",
        root = 1.0,
        converged = True,
        iterations = 1,
        final_error = 0.0,
        time_taken = 0.1,
        history = [record]
    )

    rows = result.history_rows()

    assert isinstance(rows, list)
    assert rows[0]["iteration"] == 1


def test_root_result_empty_history_rows():
    result = RootResult(
        solver_name = "test",
        root = 0.0,
        converged = False,
        iterations = 0,
        final_error = 1.0,
        time_taken = 0.0,
        history = []
    )

    assert result.history_rows() == []


def test_root_result_to_dict():
    result = RootResult(
        solver_name = "test",
        root = 2.0,
        converged = False,
        iterations = 10,
        final_error = 0.1,
        time_taken = 1.0,
        history = []
    )

    data = result.to_dict()

    assert data["solver_name"] == "test"
    assert data["root"] == 2.0
    assert data["converged"] is False
    assert data["iterations"] == 10
    assert data["final_error"] == 0.1

# ReportArtifacts tests

def test_report_artifacts_summary_report_property(tmp_path):
    artifacts = ReportArtifacts(
        output_directory = tmp_path,
        summary_markdown = tmp_path / "summary.md",
        summary_json = tmp_path / "summary.json",
        function_plot = tmp_path / "plot.png",
        convergence_plot = tmp_path / "conv.png",
        history_files = {}
    )

    assert artifacts.summary_report == artifacts.summary_markdown


def test_report_artifacts_paths_are_paths(tmp_path):
    artifacts = ReportArtifacts(
        output_directory = tmp_path,
        summary_markdown = tmp_path / "a.md",
        summary_json = tmp_path / "b.json",
        function_plot = tmp_path / "c.png",
        convergence_plot = tmp_path / "d.png",
        history_files = {}
    )

    assert isinstance(artifacts.output_directory, Path)