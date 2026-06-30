"""End-to-end test driving relkit against a real, throwaway git repo."""

import subprocess

from relkit.git import get_commits, latest_tag


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


def test_get_commits_filters_non_conventional(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: add widget")
    _commit(tmp_path, "not a conventional commit")
    _commit(tmp_path, "fix: correct widget color")

    commits = get_commits("HEAD", str(tmp_path))

    assert [c.description for c in commits] == ["add widget", "correct widget color"]


def test_latest_tag_returns_none_when_untagged(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: initial commit")

    assert latest_tag(str(tmp_path)) is None


def test_get_commits_survives_field_separator_in_body(tmp_path):
    _init_repo(tmp_path)
    _run(
        ["commit", "--allow-empty", "-q", "-m", "feat: tricky\n\nbody has a literal \x1f in it"],
        tmp_path,
    )

    commits = get_commits("HEAD", str(tmp_path))

    assert len(commits) == 1
    assert commits[0].description == "tricky"


def test_latest_tag_found_after_tagging(tmp_path):
    _init_repo(tmp_path)
    _commit(tmp_path, "feat: initial commit")
    _run(["tag", "v1.0.0"], tmp_path)
    _commit(tmp_path, "fix: a bugfix after the tag")

    assert latest_tag(str(tmp_path)) == "v1.0.0"

    commits = get_commits("v1.0.0..HEAD", str(tmp_path))
    assert [c.description for c in commits] == ["a bugfix after the tag"]
