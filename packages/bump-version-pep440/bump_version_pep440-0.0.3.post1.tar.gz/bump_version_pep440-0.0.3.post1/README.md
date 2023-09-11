# bump-version

[![Code Quality](https://github.com/azataiot/python-project-template/actions/workflows/code-quality.yml/badge.svg)](https://github.com/azataiot/python-project-template/actions/workflows/code-quality.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![latest release](https://img.shields.io/github/v/release/azataiot/bump-version)](https://github.com/azataiot/bump-version/releases)

**Introduction**: This project is heavily inspired by [bumpversion](https://github.com/peritus/bumpversion), yet this is
a different package with a different approach and design.

## Usage

### Quick Start /TODO


### CLI Usage /TODO

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
