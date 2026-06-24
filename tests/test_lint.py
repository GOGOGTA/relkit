import subprocess

from relkit.lint import lint


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


def test_lint_passes_when_all_commits_conventional(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")
    _commit(tmp_path, "fix: correct widget color")

    assert lint("HEAD", str(tmp_path)) == []


def test_lint_reports_non_conventional_commit(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")
    _commit(tmp_path, "oops forgot the type prefix")

    violations = lint("HEAD", str(tmp_path))

    assert len(violations) == 1
    assert violations[0].subject == "oops forgot the type prefix"


def test_lint_exempts_merge_commits(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: base commit")
    _run(["checkout", "-qb", "feature"], tmp_path)
    _commit(tmp_path, "feat: branch commit")
    _run(["checkout", "-q", "-"], tmp_path)
    _run(["merge", "--no-ff", "-q", "-m", "Merge branch 'feature'", "feature"], tmp_path)

    assert lint("HEAD", str(tmp_path)) == []
