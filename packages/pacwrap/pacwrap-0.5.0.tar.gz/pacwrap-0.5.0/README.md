# pacwrap

[![Build Status](https://github.com/wtfo-guru/python-pacwrap/workflows/test/badge.svg?branch=main&event=push)](https://github.com/wtfo-guru/python-pacwrap/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/wtfo-guru/python-pacwrap/branch/main/graph/badge.svg)](https://codecov.io/gh/wtfo-guru/python-pacwrap)
[![Python Version](https://img.shields.io/pypi/pyversions/python-pacwrap.svg)](https://pypi.org/project/python-pacwrap/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

Provides single interface to several common Linux package managers.


## Features

- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Add yours!


## Installation

```bash
pip install python-pacwrap
```


## Usage

### pacwrap help

```bash
pacwrap --help
Usage: pacwrap [OPTIONS] COMMAND [ARGS]...

  Provides single interface to several common Linux package managers.

Options:
  -d, --debug                   increment debug level
  -o, --out TEXT                specify output file
  -q, --quiet / --no-quiet      specify quiet mode
  -r, --refresh / --no-refresh  specify refresh synchronized package
                                repository data
  -t, --test / --no-test        specify test mode
  -v, --verbose                 increment verbosity level
  -V, --version                 show version and exit
  -h, --help                    Show this message and exit.

Commands:
  file       Displays package if any that include the FILE.
  find       Searches repositories for PACKAGE.
  info       Display information about PACKAGE.
  install    Installs PACKAGE.
  list       Lists files in PACKAGE or installed packages when no PACKAGE...
  uninstall  Unistalls PACKAGE.
```

### pacwrap file help

```bash
pacwrap file --help
Usage: pacwrap file [OPTIONS] FILENAME

  Displays package if any that include the FILE.

Options:
  -h, --help  Show this message and exit.
```

### pacwrap find help

```bash
pacwrap find --help
Usage: pacwrap find [OPTIONS] PACKAGE

  Searches repositories for PACKAGE.

Options:
  --names-only / --no-names-only  specify search names only if packager
                                  supports it
  -h, --help                      Show this message and exit.
```

### pacwrap info help

```bash
pacwrap info --help
Usage: pacwrap info [OPTIONS] PACKAGE

  Display information about PACKAGE.

Options:
  -h, --help  Show this message and exit.
```

### pacwrap install help

```bash
pacwrap install --help
Usage: pacwrap install [OPTIONS] PACKAGE

  Installs PACKAGE.

Options:
  -h, --help  Show this message and exit.
```

### pacwrap list help

```bash
pacwrap list --help
Usage: pacwrap list [OPTIONS] [PACKAGE]

  Lists files in PACKAGE or installed packages when no PACKAGE specified.

Options:
  -h, --help  Show this message and exit.
```

### pacwrap uninstall help

```bash
pacwrap uninstall --help
Usage: pacwrap uninstall [OPTIONS] PACKAGE

  Unistalls PACKAGE.

Options:
  -h, --help  Show this message and exit.
```

## Documentation

- [Stable](https://python-pacwrap.readthedocs.io/en/stable)

- [Latest](https://python-pacwrap.readthedocs.io/en/latest)

## License

[MIT](https://github.com/wtfo-guru/python-pacwrap/blob/main/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [3d9ad64bcbf7afc6bee7f2c9ea8c923d579b119c](https://github.com/wemake-services/wemake-python-package/tree/3d9ad64bcbf7afc6bee7f2c9ea8c923d579b119c). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/3d9ad64bcbf7afc6bee7f2c9ea8c923d579b119c...main) since then.
