## v0.2.0 (2026-06-24)

### Features

- **cli:** add lint command to validate Conventional Commits in CI ([`0ab84fe`](https://github.com/GOGOGTA/relkit/commit/0ab84febd5656eae4669a7fe722ac4cd45f715f7))
- add composite GitHub Action so other repos can run relkit in CI without a Python setup step ([`61f9c06`](https://github.com/GOGOGTA/relkit/commit/61f9c06c565814aeff0470d667ef7ce671940c3d))

### Bug Fixes

- **git:** explicit UTF-8 decoding and clear errors for missing git or invalid repo paths ([`0d8ed90`](https://github.com/GOGOGTA/relkit/commit/0d8ed90d0ec52f4208f0f68b38dfd479a91330b1))

### Documentation

- document lint command and GitHub Action usage ([`103707c`](https://github.com/GOGOGTA/relkit/commit/103707c743723a7822bf3188c10813dd4da22ba1))

## v0.1.0 (2026-06-22)

### Features

- initial release: `relkit changelog` generates grouped Markdown changelogs from Conventional Commits, with optional GitHub commit links and in-place `CHANGELOG.md` updates.
