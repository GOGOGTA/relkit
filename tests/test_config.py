import sys

import pytest

from relkit.config import load_config

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11), reason="config support requires the stdlib tomllib (3.11+)"
)


def test_returns_defaults_when_no_pyproject(tmp_path):
    config = load_config(str(tmp_path))

    assert config.repo_url is None
    assert config.include_all is False


def test_reads_tool_relkit_table(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.relkit]\nrepo-url = "https://github.com/example/demo"\ninclude-all = true\n'
    )

    config = load_config(str(tmp_path))

    assert config.repo_url == "https://github.com/example/demo"
    assert config.include_all is True


def test_ignores_unrelated_pyproject_without_relkit_table(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n')

    config = load_config(str(tmp_path))

    assert config.repo_url is None
    assert config.include_all is False


def test_tolerates_malformed_toml(tmp_path):
    (tmp_path / "pyproject.toml").write_text("this is not valid toml [[[")

    config = load_config(str(tmp_path))

    assert config.repo_url is None
    assert config.include_all is False
