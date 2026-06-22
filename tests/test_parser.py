from relkit.parser import parse_commit


def test_parses_simple_feat():
    commit = parse_commit("abc123", "feat: add login flow")
    assert commit is not None
    assert commit.type == "feat"
    assert commit.scope is None
    assert commit.description == "add login flow"
    assert commit.breaking is False


def test_parses_scope():
    commit = parse_commit("abc123", "fix(parser): handle empty body")
    assert commit is not None
    assert commit.type == "fix"
    assert commit.scope == "parser"
    assert commit.description == "handle empty body"


def test_breaking_via_bang():
    commit = parse_commit("abc123", "feat(api)!: drop v1 endpoints")
    assert commit is not None
    assert commit.breaking is True


def test_breaking_via_footer():
    body = "Some details.\n\nBREAKING CHANGE: removes the old config format"
    commit = parse_commit("abc123", "refactor: simplify config loading", body)
    assert commit is not None
    assert commit.breaking is True


def test_non_conventional_commit_returns_none():
    assert parse_commit("abc123", "fixed a typo") is None


def test_type_is_lowercased():
    commit = parse_commit("abc123", "Feat: support windows paths")
    assert commit is not None
    assert commit.type == "feat"
