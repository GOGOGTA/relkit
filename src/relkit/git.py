"""Thin wrapper around `git log` used to collect commits for a changelog."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from .parser import Commit, parse_commit

_FIELD_SEP = "\x1f"
_ENTRY_SEP = "\x1e"


class GitError(RuntimeError):
    pass


@dataclass(frozen=True)
class RawCommit:
    sha: str
    subject: str
    body: str

    @property
    def is_merge(self) -> bool:
        return self.subject.startswith("Merge ")


def _run_git(args: list[str], repo_path: str) -> str:
    if not os.path.isdir(repo_path):
        raise GitError(f"'{repo_path}' is not a directory")

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found — is git installed and on PATH?") from exc

    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def latest_tag(repo_path: str = ".") -> str | None:
    """Return the most recent tag reachable from HEAD, or None if there isn't one."""
    try:
        return _run_git(["describe", "--tags", "--abbrev=0"], repo_path).strip() or None
    except GitError:
        return None


def _iter_raw_commits(rev_range: str, repo_path: str) -> list[RawCommit]:
    fmt = f"%H{_FIELD_SEP}%s{_FIELD_SEP}%b{_ENTRY_SEP}"
    output = _run_git(["log", rev_range, "--reverse", f"--format={fmt}"], repo_path)

    commits: list[RawCommit] = []
    for entry in output.split(_ENTRY_SEP):
        entry = entry.strip("\n")
        if not entry:
            continue
        sha, subject, body = entry.split(_FIELD_SEP)
        commits.append(RawCommit(sha=sha, subject=subject, body=body))
    return commits


def get_raw_commits(rev_range: str, repo_path: str = ".") -> list[RawCommit]:
    """Return every commit in `rev_range` (oldest first), parsed or not."""
    return _iter_raw_commits(rev_range, repo_path)


def get_commits(rev_range: str, repo_path: str = ".") -> list[Commit]:
    """Return parsed Conventional Commits in `rev_range` (oldest first)."""
    commits: list[Commit] = []
    for raw in _iter_raw_commits(rev_range, repo_path):
        commit = parse_commit(raw.sha, raw.subject, raw.body)
        if commit is not None:
            commits.append(commit)
    return commits
