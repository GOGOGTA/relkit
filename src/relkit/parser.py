"""Parsing of Conventional Commits (https://www.conventionalcommits.org/)."""

from __future__ import annotations

import re
from dataclasses import dataclass

_SUBJECT_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$"
)
_BREAKING_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE)


@dataclass(frozen=True)
class Commit:
    sha: str
    type: str
    scope: str | None
    description: str
    breaking: bool
    raw_subject: str


def parse_commit(sha: str, subject: str, body: str = "") -> Commit | None:
    """Parse a single commit subject/body pair into a Commit, or None if it
    doesn't follow the Conventional Commits format.
    """
    match = _SUBJECT_RE.match(subject.strip())
    if not match:
        return None

    breaking = bool(match.group("breaking")) or bool(_BREAKING_FOOTER_RE.search(body))

    return Commit(
        sha=sha,
        type=match.group("type").lower(),
        scope=match.group("scope"),
        description=match.group("description").strip(),
        breaking=breaking,
        raw_subject=subject.strip(),
    )
