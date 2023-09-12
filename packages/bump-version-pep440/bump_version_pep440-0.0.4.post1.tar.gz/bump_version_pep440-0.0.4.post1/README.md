# bump-version-pep440

[![Code Quality](https://github.com/azataiot/python-project-template/actions/workflows/code-quality.yml/badge.svg)](https://github.com/azataiot/python-project-template/actions/workflows/code-quality.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![latest release](https://img.shields.io/github/v/release/azataiot/bump-version-pep440)](https://github.com/azataiot/bump-version-pep440/releases)

**Introduction**: This project is heavily inspired by [bumpversion](https://github.com/peritus/bumpversion), yet this is
a different package with a different approach and design.

## Usage

### Quick Start

```bash
poetry add bump-version-pep440
```

### CLI Usage

```bash
❯ poetry run bv --help

 Usage: bv [OPTIONS] VERSION_TYPE

 Bump the version based on the provided version type and other parameters.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    version_type      TEXT  [default: None] [required]                                                                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --current-version     -c      TEXT  Current version to be used instead of reading from pyproject.toml. [default: None]                                                                                │
│ --new-version         -n      TEXT  New version to be set instead of incrementing the current version. [default: None]                                                                                │
│ --commit                            If set, a git commit will be created. [default: True]                                                                                                             │
│ --commit-message              TEXT  Custom commit message. [default: None]                                                                                                                            │
│ --dry-run                           If set, no actual changes will be made, only printed.                                                                                                             │
│ --tag                               If set, a git tag will be created. [default: True]                                                                                                                │
│ --tag-name                    TEXT  Custom tag name. [default: None]                                                                                                                                  │
│ --install-completion                Install completion for the current shell.                                                                                                                         │
│ --show-completion                   Show completion for the current shell, to copy it or customize the installation.                                                                                  │
│ --help                              Show this message and exit.                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Branching Strategy

- `main`: The main branch. This branch is protected and cannot be pushed directly. (PRs must be made to `dev` instead
  of `main`)
- `dev`: The development branch. This branch is protected and cannot be pushed directly. (PRs must be made to this
  branch)
- `feature/*`: The 'feature/*' branches are used to develop new features for the upcoming or a distant future release.
  These branches are branched off from 'dev' and must merge back into `dev`.
- `release/*`: The 'release/*' branches are used to prepare the next release. They allow for last-minute changes and
  minor bug fixes. These branches are branched off from 'dev' and must merge back into `main` and `dev`.
- `hotfix/*`: The 'hotfix/*' branches are used to develop fixes for the current release. These branches are branched off
  from `main` and must merge back into `main`.

## Contributing

Contributions are always welcome! Whether it's bug reports, feature requests, or pull requests, all contributions are
appreciated. For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under some License. For more details, see [LICENSE](LICENSE.md).

## Code of Conduct

We believe in fostering an inclusive and respectful community. For guidelines and reporting information,
see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Your security is paramount. If you discover any security-related issues, please follow the guidelines
in [SECURITY.md](SECURITY.md).

## Founding

For information about the project's founding and backers, see [FOUNDING](https://github.com/sponsors/azataiot).
