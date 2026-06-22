# relkit

Generate clean, grouped changelogs from [Conventional Commits](https://www.conventionalcommits.org/) — zero runtime dependencies, one command.

Maintainers spend real time turning a pile of commits into something a release reads well. `relkit` automates that step: point it at a revision range and it groups commits into Features, Bug Fixes, Breaking Changes, and more, ready to paste into a release or prepend straight into `CHANGELOG.md`.

## Install

```bash
pip install relkit
```

Or run from source:

```bash
git clone https://github.com/REPLACE_ME/relkit
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
```

## License

MIT — see [LICENSE](LICENSE).
