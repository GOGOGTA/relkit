from datetime import date

from relkit.changelog import render
from relkit.parser import Commit


def make_commit(sha, type_, description, scope=None, breaking=False):
    return Commit(
        sha=sha,
        type=type_,
        scope=scope,
        description=description,
        breaking=breaking,
        raw_subject=f"{type_}: {description}",
    )


def test_groups_by_type_in_priority_order():
    commits = [
        make_commit("1111111aaaa", "fix", "stop crash on empty input"),
        make_commit("2222222bbbb", "feat", "add JSON export"),
    ]
    out = render(commits, version="v1.0.0", when=date(2026, 6, 22))

    assert "## v1.0.0 (2026-06-22)" in out
    assert out.index("### Features") < out.index("### Bug Fixes")
    assert "add JSON export" in out
    assert "stop crash on empty input" in out


def test_breaking_changes_surface_first():
    commits = [
        make_commit("1111111aaaa", "feat", "new default behavior", breaking=True),
        make_commit("2222222bbbb", "fix", "minor fix"),
    ]
    out = render(commits, when=date(2026, 6, 22))

    assert out.index("BREAKING CHANGES") < out.index("### Features" if "### Features" in out else "### Bug Fixes")


def test_chore_excluded_by_default():
    commits = [make_commit("1111111aaaa", "chore", "bump deps")]
    out = render(commits, when=date(2026, 6, 22))
    assert "bump deps" not in out
    assert "No notable changes" in out


def test_include_all_shows_chore():
    commits = [make_commit("1111111aaaa", "chore", "bump deps")]
    out = render(commits, include_all=True, when=date(2026, 6, 22))
    assert "bump deps" in out
    assert "### Chores" in out


def test_scope_rendered_bold():
    commits = [make_commit("1111111aaaa", "feat", "add export", scope="cli")]
    out = render(commits, when=date(2026, 6, 22))
    assert "**cli:** add export" in out


def test_repo_url_links_commit():
    commits = [make_commit("1111111aaaa", "feat", "add export")]
    out = render(commits, repo_url="https://github.com/example/relkit", when=date(2026, 6, 22))
    assert "https://github.com/example/relkit/commit/1111111aaaa" in out
