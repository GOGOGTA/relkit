"""Command-line entry point for relkit."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .changelog import prepend_to_file, render
from .git import GitError, get_commits, latest_tag


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
        "--write",
        dest="write_path",
        help="Prepend the rendered section to this file instead of printing it.",
    )

    return parser


def _run_changelog(args: argparse.Namespace) -> int:
    from_ref = args.from_ref or latest_tag(args.repo_path)
    rev_range = f"{from_ref}..{args.to_ref}" if from_ref else args.to_ref

    try:
        commits = get_commits(rev_range, args.repo_path)
    except GitError as exc:
        print(f"relkit: {exc}", file=sys.stderr)
        return 1

    section = render(
        commits,
        version=args.release,
        repo_url=args.repo_url,
        include_all=args.include_all,
    )

    if args.write_path:
        prepend_to_file(section, args.write_path)
        print(f"relkit: wrote changelog section to {args.write_path}")
    else:
        print(section)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "changelog":
        return _run_changelog(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
