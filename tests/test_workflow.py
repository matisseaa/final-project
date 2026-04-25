import pytest
from numerical_workbench.workflow import (
    demo_config,
    create_object_interval,
    run_full_report
)
from numerical_workbench.models import Interval, ReportArtifacts

# demo_config tests

def test_demo_config_polynomial():
    config = demo_config("polynomial")

    assert "function" in config
    assert config["function"]["kind"] == "polynomial"


def test_demo_config_expression():
    config = demo_config("expression")

    assert config["function"]["kind"] == "expression"

# create_object_interval tests

def test_create_object_interval_basic():
    data = {"left": 0, "right": 2}

    interval = create_object_interval(data)

    assert isinstance(interval, Interval)
    assert interval.left == 0
    assert interval.right == 2


def test_create_object_interval_float_conversion():
    data = {"left": "1", "right": "3"}

    interval = create_object_interval(data)

    assert interval.left == 1.0
    assert interval.right == 3.0

# run_full_report tests

def test_run_full_report_basic(tmp_path):
    config = demo_config("polynomial")

    artifacts = run_full_report(
        config = config,
        output_directory = tmp_path
    )

    assert isinstance(artifacts, ReportArtifacts)
    assert artifacts.output_directory.exists()


def test_run_full_report_creates_files(tmp_path):
    config = demo_config("polynomial")

    artifacts = run_full_report(
        config = config,
        output_directory = tmp_path
    )

    # check that important files are created
    assert artifacts.summary_json.exists()
    assert artifacts.summary_markdown.exists()
    assert artifacts.function_plot.exists()
    assert artifacts.convergence_plot.exists()

    # method record
    assert isinstance(artifacts.history_files, dict)
    assert len(artifacts.history_files) > 0


def test_run_full_report_with_expression(tmp_path):
    config = demo_config("expression")

    artifacts = run_full_report(
        config = config,
        output_directory = tmp_path
    )

    assert artifacts.summary_json.exists()

# edge cases

def test_run_full_report_custom_output_dir(tmp_path):
    config = demo_config()

    custom_dir = tmp_path / "custom_output"

    artifacts = run_full_report(
        config = config,
        output_directory = custom_dir
    )

    assert custom_dir.exists()
    assert artifacts.output_directory == custom_dir


def test_run_full_report_without_config():
    # use config by default
    artifacts = run_full_report()

    assert isinstance(artifacts, ReportArtifacts)


def test_run_full_report_invalid_config(tmp_path):
    # missing "function"
    bad_config = {}

    with pytest.raises(Exception):
        run_full_report(
            config = bad_config,
            output_directory = tmp_path
        )