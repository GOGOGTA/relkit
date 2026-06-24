import subprocess

import pytest

from relkit.cli import main


def _run(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(path):
    _run(["init", "-q"], path)
    _run(["config", "user.email", "test@example.com"], path)
    _run(["config", "user.name", "Test"], path)


def _commit(path, message):
    (path / "file.txt").write_text(message)
    _run(["add", "."], path)
    _run(["commit", "-q", "-m", message], path)


def test_changelog_exits_zero_and_prints(tmp_path, capsys):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")

    exit_code = main(["changelog", "--repo", str(tmp_path)])

    assert exit_code == 0
    assert "add widget" in capsys.readouterr().out


def test_lint_exits_zero_when_clean(tmp_path, capsys):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")

    exit_code = main(["lint", "--repo", str(tmp_path)])

    assert exit_code == 0
    assert "all commits follow" in capsys.readouterr().out


def test_lint_exits_one_when_violations_found(tmp_path, capsys):
    _init_repo(tmp_path)
    _commit(tmp_path, "not conventional")

    exit_code = main(["lint", "--repo", str(tmp_path)])

    assert exit_code == 1
    assert "not conventional" in capsys.readouterr().out


def test_changelog_errors_cleanly_on_invalid_repo(tmp_path, capsys):
    exit_code = main(["changelog", "--repo", str(tmp_path / "does-not-exist")])

    assert exit_code == 1
    assert "is not a directory" in capsys.readouterr().err


def test_missing_command_prints_help():
    with pytest.raises(SystemExit):
        main([])
