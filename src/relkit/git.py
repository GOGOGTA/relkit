"""Thin wrapper around `git log` used to collect commits for a changelog."""

from __future__ import annotations

import subprocess

from .parser import Commit, parse_commit

_FIELD_SEP = "\x1f"
_ENTRY_SEP = "\x1e"


class GitError(RuntimeError):
    pass


def _run_git(args: list[str], repo_path: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def latest_tag(repo_path: str = ".") -> str | None:
    """Return the most recent tag reachable from HEAD, or None if there isn't one."""
    try:
        return _run_git(["describe", "--tags", "--abbrev=0"], repo_path).strip() or None
    except GitError:
        return None


def get_commits(rev_range: str, repo_path: str = ".") -> list[Commit]:
    """Return parsed Conventional Commits in `rev_range` (oldest first)."""
    fmt = f"%H{_FIELD_SEP}%s{_FIELD_SEP}%b{_ENTRY_SEP}"
    output = _run_git(["log", rev_range, "--reverse", f"--format={fmt}"], repo_path)

    commits: list[Commit] = []
    for entry in output.split(_ENTRY_SEP):
        entry = entry.strip("\n")
        if not entry:
            continue
        sha, subject, body = entry.split(_FIELD_SEP)
        commit = parse_commit(sha, subject, body)
        if commit is not None:
            commits.append(commit)
    return commits
