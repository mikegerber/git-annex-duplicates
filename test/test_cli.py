import subprocess
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

import git_annex_duplicates


@pytest.fixture
def invoke_cli():
    runner = CliRunner()

    def invoke(args=None):
        return runner.invoke(
            git_annex_duplicates.main,
            args,
            prog_name="git-annex-duplicates",
        )

    return invoke


def mock_git_annex(monkeypatch, output):
    run = Mock(
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=output.encode(),
            stderr=b"",
        )
    )
    monkeypatch.setattr(git_annex_duplicates.subprocess, "run", run)
    return run


def test_help_lists_cli_options(invoke_cli):
    result = invoke_cli(["--help"])

    assert result.exit_code == 0
    assert "Usage: git-annex-duplicates [OPTIONS] [DIRECTORIES]..." in result.output
    assert "--exclude TEXT" in result.output
    assert "--across" in result.output


def test_default_directory_and_duplicate_output(invoke_cli, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    run = mock_git_annex(
        monkeypatch,
        "key-a:photos/first.jpg\n"
        "key-b:only-once.txt\n"
        "key-a:backup/first.jpg\n"
        "key-c:one.txt\n"
        "key-c:two.txt\n",
    )

    result = invoke_cli()

    assert result.exit_code == 0
    assert result.output == (
        "photos/first.jpg\n"
        "backup/first.jpg\n"
        "\n"
        "one.txt\n"
        "two.txt\n"
        "\n"
    )
    run.assert_called_once_with(
        [
            "git",
            "annex",
            "find",
            "--include",
            "*",
            "--format=${key}:${file}\n",
            tmp_path,
        ],
        capture_output=True,
        check=True,
    )


def test_directories_and_repeated_excludes_are_passed_to_git_annex(
    invoke_cli, monkeypatch, tmp_path
):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    run = mock_git_annex(monkeypatch, "")

    result = invoke_cli(
        [
            "--exclude",
            "*.iso",
            "--exclude",
            "archive/**",
            str(first),
            str(second),
        ],
    )

    assert result.exit_code == 0
    assert result.output == ""
    run.assert_called_once_with(
        [
            "git",
            "annex",
            "find",
            "--include",
            "*",
            "--format=${key}:${file}\n",
            first,
            second,
            "--exclude",
            "*.iso",
            "--exclude",
            "archive/**",
        ],
        capture_output=True,
        check=True,
    )


def test_across_only_reports_duplicates_in_different_directories(
    invoke_cli, monkeypatch, tmp_path
):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    monkeypatch.chdir(tmp_path)
    mock_git_annex(
        monkeypatch,
        "same-first:first/one.txt\n"
        "same-first:first/two.txt\n"
        "across:first/shared.txt\n"
        "across:second/shared.txt\n"
        "same-second:second/one.txt\n"
        "same-second:second/two.txt\n",
    )

    result = invoke_cli(["--across", str(first), str(second)])

    assert result.exit_code == 0
    assert result.output == "first/shared.txt\nsecond/shared.txt\n\n"


def test_across_requires_two_directories(invoke_cli, tmp_path):
    directory = tmp_path / "only"
    directory.mkdir()

    result = invoke_cli(["--across", str(directory)])

    assert result.exit_code == 2
    assert "Error: --across requires at least two directories" in result.output


def test_rejects_a_missing_directory(invoke_cli, tmp_path):
    missing = tmp_path / "missing"

    result = invoke_cli([str(missing)])

    assert result.exit_code == 2
    assert "Directory" in result.output
    assert "does not exist" in result.output
