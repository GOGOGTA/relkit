# relkit

Generate clean, grouped changelogs from [Conventional Commits](https://www.conventionalcommits.org/) — zero runtime dependencies, one command.

Maintainers spend real time turning a pile of commits into something a release reads well. `relkit` automates that step: point it at a revision range and it groups commits into Features, Bug Fixes, Breaking Changes, and more, ready to paste into a release or prepend straight into `CHANGELOG.md`.

## Install

```bash
pip install relkit
```

Or run from source:

```bash
git clone https://github.com/GOGOGTA/relkit
cd relkit
pip install -e .
```

## Usage

Print a changelog since the last tag:

```bash
relkit changelog
```

Generate a changelog for a specific range and link commits back to GitHub:

```bash
relkit changelog --from v1.2.0 --to v1.3.0 --release v1.3.0 \
  --repo-url https://github.com/your-org/your-repo
```

Prepend the result straight into your changelog file instead of printing it:

```bash
relkit changelog --release v1.3.0 --write CHANGELOG.md
```

Include maintenance commits (`chore`, `ci`, `test`, `build`, `style`, `revert`) that are excluded by default:

```bash
relkit changelog --include-all
```

Only include commits with a given scope, e.g. commits like `feat(cli): ...`:

```bash
relkit changelog --scope cli
```

### Setting defaults in pyproject.toml

Stop retyping `--repo-url` every time by adding a `[tool.relkit]` table:

```toml
[tool.relkit]
repo-url = "https://github.com/your-org/your-repo"
include-all = false
```

CLI flags always take precedence over the config file. This requires Python 3.11+ (it
reads the table with the stdlib `tomllib`); on older interpreters it's silently ignored
rather than pulling in a TOML parser as a dependency — relkit stays zero-dependency on
every supported Python version.

### Linting commits in CI

Catch non-conventional commits before they pollute your changelog. Exits non-zero if anything in the range doesn't parse (merge commits are exempt):

```bash
relkit lint --from origin/main --to HEAD
```

### Using it as a GitHub Action

Other repos can run relkit directly in CI without managing a Python environment themselves:

```yaml
- uses: GOGOGTA/relkit@main
  id: changelog
  with:
    release: v1.3.0
    repo-url: https://github.com/your-org/your-repo
    write: CHANGELOG.md
```

The rendered Markdown is also available as `${{ steps.changelog.outputs.changelog }}` for posting to a release or PR comment.

### Example output

```markdown
## v1.3.0 (2026-06-22)

### ⚠ BREAKING CHANGES

- drop support for the v1 config format (`a1b2c3d`)

### Features

- **cli:** add JSON export (`4f5e6d7`)

### Bug Fixes

- stop crash on empty input (`9c8b7a6`)
```

## How it works

`relkit` shells out to `git log`, parses each commit subject against the Conventional Commits grammar (`type(scope)!: description`), and renders the matched commits into Markdown grouped by type. Commits that don't follow the convention are silently skipped — `relkit` only ever surfaces what it can confidently categorize.

## Why this exists

Most changelog tools either require a hosted service, a config file with a learning curve, or a Node toolchain. `relkit` is a single small Python package with no runtime dependencies, meant to be dropped into a release script or CI job in minutes.

## Development

```bash
pip install -e ".[dev]"
pytest
mypy src/relkit
```

## License

MIT — see [LICENSE](LICENSE).
