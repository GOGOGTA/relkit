# Contributing to relkit

Thanks for considering a contribution.

## Setup

```bash
git clone https://github.com/REPLACE_ME/relkit
cd relkit
pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep the package dependency-free at runtime; the standard library is enough for what relkit does.
- Commit messages in this repo follow [Conventional Commits](https://www.conventionalcommits.org/) — fittingly, relkit generates its own changelog from them.
- Add or update tests for any behavior change. `pytest` should pass before opening a PR.
- Keep PRs focused; unrelated cleanup can go in a separate PR.

## Reporting issues

Open a GitHub issue with the command you ran, the output you got, and what you expected instead.
