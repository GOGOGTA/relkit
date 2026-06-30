"""Command-line entry point for relkit."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .changelog import prepend_to_file, render
from .config import load_config
from .git import GitError, get_commits, latest_tag
from .lint import lint


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="relkit",
        description="Generate grouped changelogs from Conventional Commits.",
    )
    parser.add_argument("--version", action="version", version=f"relkit {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    changelog_cmd = subparsers.add_parser(
        "changelog", help="Render a changelog section from git history."
    )
    changelog_cmd.add_argument(
        "--from",
        dest="from_ref",
        help="Start of the revision range (default: latest tag, or repo root if none).",
    )
    changelog_cmd.add_argument(
        "--to", dest="to_ref", default="HEAD", help="End of the revision range (default: HEAD)."
    )
    changelog_cmd.add_argument(
        "--release", dest="release", default="Unreleased", help="Heading label, e.g. v1.2.0."
    )
    changelog_cmd.add_argument(
        "--repo", dest="repo_path", default=".", help="Path to the git repository."
    )
    changelog_cmd.add_argument(
        "--repo-url", dest="repo_url", help="Repo URL used to link commits, e.g. a GitHub URL."
    )
    changelog_cmd.add_argument(
        "--include-all",
        action="store_true",
        help="Include chore/ci/test/build/style/revert commits too.",
    )
    changelog_cmd.add_argument(
        "--scope",
        dest="scope",
        help="Only include commits with this scope, e.g. --scope cli for 'feat(cli): ...'.",
    )
    changelog_cmd.add_argument(
        "--write",
        dest="write_path",
        help="Prepend the rendered section to this file instead of printing it.",
    )

    lint_cmd = subparsers.add_parser(
        "lint", help="Check that commits in a range follow Conventional Commits."
    )
    lint_cmd.add_argument(
        "--from",
        dest="from_ref",
        help="Start of the revision range (default: latest tag, or repo root if none).",
    )
    lint_cmd.add_argument(
        "--to", dest="to_ref", default="HEAD", help="End of the revision range (default: HEAD)."
    )
    lint_cmd.add_argument(
        "--repo", dest="repo_path", default=".", help="Path to the git repository."
    )

    return parser


def _run_changelog(args: argparse.Namespace) -> int:
    config = load_config(args.repo_path)
    from_ref = args.from_ref or latest_tag(args.repo_path)
    rev_range = f"{from_ref}..{args.to_ref}" if from_ref else args.to_ref

    try:
        commits = get_commits(rev_range, args.repo_path)
    except GitError as exc:
        print(f"relkit: {exc}", file=sys.stderr)
        return 1

    if args.scope:
        commits = [c for c in commits if c.scope == args.scope]

    section = render(
        commits,
        version=args.release,
        repo_url=args.repo_url or config.repo_url,
        include_all=args.include_all or config.include_all,
    )

    if args.write_path:
        prepend_to_file(section, args.write_path)
        print(f"relkit: wrote changelog section to {args.write_path}")
    else:
        print(section)

    return 0


def _run_lint(args: argparse.Namespace) -> int:
    from_ref = args.from_ref or latest_tag(args.repo_path)
    rev_range = f"{from_ref}..{args.to_ref}" if from_ref else args.to_ref

    try:
        violations = lint(rev_range, args.repo_path)
    except GitError as exc:
        print(f"relkit: {exc}", file=sys.stderr)
        return 1

    if not violations:
        print("relkit: all commits follow Conventional Commits.")
        return 0

    print(f"relkit: {len(violations)} commit(s) don't follow Conventional Commits:\n")
    for violation in violations:
        print(f"  {violation.sha[:7]}  {violation.subject}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "changelog":
        return _run_changelog(args)
    if args.command == "lint":
        return _run_lint(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
