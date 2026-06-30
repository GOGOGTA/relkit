import subprocess
import sys

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


def test_changelog_scope_filters_commits(tmp_path, capsys):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat(cli): add widget")
    _commit(tmp_path, "feat(api): add endpoint")

    exit_code = main(["changelog", "--repo", str(tmp_path), "--scope", "cli"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "add widget" in out
    assert "add endpoint" not in out


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


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="config support requires the stdlib tomllib (3.11+)"
)
def test_changelog_uses_repo_url_from_pyproject_config(tmp_path, capsys):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.relkit]\nrepo-url = "https://github.com/example/demo"\n'
    )

    exit_code = main(["changelog", "--repo", str(tmp_path)])

    assert exit_code == 0
    assert "https://github.com/example/demo/commit/" in capsys.readouterr().out
