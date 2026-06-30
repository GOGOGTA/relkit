"""Read relkit defaults from a [tool.relkit] table in pyproject.toml, when available.

Config support relies on `tomllib`, which is stdlib-only from Python 3.11 onward. On
older interpreters this quietly becomes a no-op rather than adding a TOML dependency —
relkit has zero runtime dependencies on every supported Python version, no exceptions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None  # type: ignore[assignment]


@dataclass(frozen=True)
class Config:
    repo_url: str | None = None
    include_all: bool = False


def load_config(repo_path: str = ".") -> Config:
    """Read [tool.relkit] from `repo_path`/pyproject.toml, if present and parseable."""
    if tomllib is None:
        return Config()

    path = os.path.join(repo_path, "pyproject.toml")
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return Config()

    table = data.get("tool", {}).get("relkit", {})
    return Config(
        repo_url=table.get("repo-url"),
        include_all=bool(table.get("include-all", False)),
    )
