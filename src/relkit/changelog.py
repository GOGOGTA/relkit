"""Render a list of parsed commits into a grouped Markdown changelog section."""

from __future__ import annotations

from datetime import date

from .parser import Commit

# Order controls section order in the rendered output.
_TYPE_LABELS: dict[str, str] = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "docs": "Documentation",
    "build": "Build System",
    "ci": "Continuous Integration",
    "test": "Tests",
    "chore": "Chores",
    "style": "Style",
    "revert": "Reverts",
}

# Types included by default even without --include-all.
_DEFAULT_TYPES = {"feat", "fix", "perf", "refactor", "docs"}


def _short_sha(sha: str) -> str:
    return sha[:7]


def _commit_link(commit: Commit, repo_url: str | None) -> str:
    short = _short_sha(commit.sha)
    if repo_url:
        return f"[`{short}`]({repo_url.rstrip('/')}/commit/{commit.sha})"
    return f"`{short}`"


def _format_line(commit: Commit, repo_url: str | None) -> str:
    scope = f"**{commit.scope}:** " if commit.scope else ""
    return f"- {scope}{commit.description} ({_commit_link(commit, repo_url)})"


def render(
    commits: list[Commit],
    version: str = "Unreleased",
    repo_url: str | None = None,
    include_all: bool = False,
    when: date | None = None,
) -> str:
    """Render commits into a Markdown changelog section.

    Breaking changes are always surfaced first, regardless of type.
    """
    when = when or date.today()
    header = f"## {version} ({when.isoformat()})" if version != "Unreleased" else f"## {version}"

    breaking = [c for c in commits if c.breaking]
    by_type: dict[str, list[Commit]] = {}
    for commit in commits:
        if commit.type not in _DEFAULT_TYPES and not include_all:
            continue
        by_type.setdefault(commit.type, []).append(commit)

    sections: list[str] = [header]

    if breaking:
        sections.append("\n### ⚠ BREAKING CHANGES\n")
        sections.extend(_format_line(c, repo_url) for c in breaking)

    for commit_type, label in _TYPE_LABELS.items():
        group = by_type.get(commit_type)
        if not group:
            continue
        sections.append(f"\n### {label}\n")
        sections.extend(_format_line(c, repo_url) for c in group)

    if not breaking and not by_type:
        sections.append("\n_No notable changes._")

    return "\n".join(sections).rstrip() + "\n"


def prepend_to_file(section: str, path: str) -> None:
    """Insert a newly rendered section at the top of an existing changelog file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ""

    with open(path, "w", encoding="utf-8") as f:
        f.write(section)
        if existing:
            f.write("\n" + existing)
