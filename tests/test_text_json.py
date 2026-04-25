import pytest
from pathlib import Path

from src.text_json import (
    ensure_directory,
    load_json,
    save_json,
    save_rows_to_csv,
    save_text,
    build_function_from_spec
)
from src.exceptions import ConfigurationError
from src.functions import Polynomial, ExpressionFunction

# ensure_directory tests

def test_ensure_directory_creates(tmp_path):
    path = tmp_path / "new_dir"

    result = ensure_directory(path)

    assert result.exists()
    assert result.is_dir()


def test_ensure_directory_existing(tmp_path):
    path = tmp_path

    result = ensure_directory(path)

    assert result.exists()

# save_json and load_json tests

def test_save_and_load_json(tmp_path):
    data = {"a": 1, "b": 2}
    file_path = tmp_path / "test.json"

    save_json(data, file_path)
    loaded = load_json(file_path)

    assert loaded == data


def test_save_json_creates_file(tmp_path):
    data = {"x": 10}
    file_path = tmp_path / "file.json"

    result = save_json(data, file_path)

    assert result.exists()

# save_rows_to_csv tests

def test_save_rows_to_csv_basic(tmp_path):
    rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    file_path = tmp_path / "data.csv"

    result = save_rows_to_csv(rows, file_path)

    assert result.exists()


def test_save_rows_to_csv_empty(tmp_path):
    file_path = tmp_path / "empty.csv"

    result = save_rows_to_csv([], file_path)

    assert result.exists()

    content = file_path.read_text()
    assert "no rows available" in content

# save_text tests

def test_save_text_basic(tmp_path):
    file_path = tmp_path / "text.txt"

    result = save_text("hello world", file_path)

    assert result.exists()
    assert file_path.read_text() == "hello world"

# build_function_from_spec tests

def test_build_function_polynomial():
    spec = {"kind": "polynomial", "expression": "x^2 + 1"}

    func = build_function_from_spec(spec)

    assert isinstance(func, Polynomial)
    assert func.evaluate_scalar(2) == 5


def test_build_function_expression():
    spec = {"kind": "expression", "expression": "x + 1"}

    func = build_function_from_spec(spec)

    assert isinstance(func, ExpressionFunction)
    assert func.evaluate_scalar(2) == 3


def test_build_function_missing_expression():
    spec = {"kind": "polynomial"}

    with pytest.raises(ConfigurationError):
        build_function_from_spec(spec)


def test_build_function_invalid_kind():
    spec = {"kind": "unknown", "expression": "x + 1"}

    with pytest.raises(ConfigurationError):
        build_function_from_spec(spec)

# edge cases

def test_build_function_case_insensitive():
    spec = {"kind": "PoLyNoMiAl", "expression": "x^2"}

    func = build_function_from_spec(spec)

    assert isinstance(func, Polynomial)


def test_build_function_expression_string_number():
    spec = {"kind": "expression", "expression": "5"}

    func = build_function_from_spec(spec)

    assert func.evaluate_scalar(100) == 5