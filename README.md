# hadolint-get

## Overview

`hadolint-get` fetches a given [hadolint](https://github.com/hadolint/hadolint) version from the [official GitHub
releases page](https://github.com/hadolint/hadolint/releases) and executes it. It is intended to be used as a
[pre-commit framework](https://pre-commit.com/) hook so no manual `hadolint` installation is necessary.

Linux, macOS and Windows are supported.

## Usage as a pre-commit hook

Add

```yaml
- repo: https://github.com/IngoMeyer441/hadolint-get
  rev: 0.1.1
  hooks:
  - id: hadolint-get
  - args: ['--hadolint-version=2.6.0']
```

to your `.pre-commit-config.yaml`. The pre-commit framework will install `hadolint-get` which fetches `hadolint` version
2.6.0 on the next pre-commit hook run and executes it.

If you would like to pass arguments to the `hadolint` executable itself, separate them from `hadolint-get` options with
`--`, for example:

```yaml
  - args: ['--hadolint-version=2.6.0', '--', '--failure-threshold=error']
```

## Caching

`hadolint-get` caches fetched `hadolint` executables so they can be reused in later pre-commit runs. The caching
locations are:

- Linux: `${XDG_CACHE_HOME}/hadolint-get` if `${XDG_CACHE_HOME}` is set, otherwise `${HOME}/.cache/hadolint-get`
- macOS: `${HOME}/Library/Caches/hadolint-get`
- Windows: `%LOCALAPPDATA%\hadolint-get`

## Contributing

Please open [an issue on GitHub](https://github.com/IngoMeyer441/hadolint-get/issues/new) if you experience bugs or miss
features. Please consider to send a pull request if you can spend time on fixing the issue yourself. This project uses
[pre-commit](https://pre-commit.com) itself to ensure code quality and a consistent code style. Run

```bash
make git-hooks-install
```

to install all linters as Git hooks in your local clone of `hadolint-get`.
