> **WARNING:**  *This package is still in the process of being open sourced.
> Until that work is done and this banner is removed, don't expect anything
> documented here to be accurate.*

![Lines of code](https://sloc.xyz/github/sandialabs/shell-logger/?category=code)
[![codecov](https://codecov.io/gh/sandialabs/shell-logger/branch/master/graph/badge.svg?token=FmDStZ6FVR)](https://codecov.io/gh/sandialabs/shell-logger)
[![CodeFactor](https://www.codefactor.io/repository/github/sandialabs/shell-logger/badge/master)](https://www.codefactor.io/repository/github/sandialabs/shell-logger/overview/master)
[![CodeQL](https://github.com/sandialabs/shell-logger/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/sandialabs/shell-logger/actions/workflows/github-code-scanning/codeql)
[![Conda Version](https://img.shields.io/conda/v/conda-forge/shell-logger?label=conda-forge)](https://anaconda.org/conda-forge/shell-logger)
![Conda Downloads](https://img.shields.io/conda/d/conda-forge/shell-logger?label=conda-forge%20downloads)
[![Continuous Integration](https://github.com/sandialabs/shell-logger/actions/workflows/continuous-integration.yml/badge.svg)](https://github.com/sandialabs/shell-logger/actions/workflows/continuous-integration.yml)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![GitHub contributors](https://img.shields.io/github/contributors/sandialabs/shell-logger.svg)](https://github.com/sandialabs/shell-logger/graphs/contributors)
[![Documentation Status](https://readthedocs.org/projects/shell-logger/badge/?version=latest)](https://shell-logger.readthedocs.io/en/latest/?badge=latest)
[![License](https://anaconda.org/conda-forge/shell-logger/badges/license.svg)](LICENSE.md)
[![Merged PRs](https://img.shields.io/github/issues-pr-closed-raw/sandialabs/shell-logger.svg?label=merged+PRs)](https://github.com/sandialabs/shell-logger/pulls?q=is:pr+is:merged)
[![OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/projects/8863/badge)](https://bestpractices.coreinfrastructure.org/projects/8863)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/sandialabs/shell-logger/badge)](https://securityscorecards.dev/viewer/?uri=github.com/sandialabs/shell-logger)
![Platforms](https://anaconda.org/conda-forge/shell-logger/badges/platforms.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci Status](https://results.pre-commit.ci/badge/github/sandialabs/shell-logger/master.svg)](https://results.pre-commit.ci/latest/github/sandialabs/shell-logger/master)
[![PyPI - Version](https://img.shields.io/pypi/v/shell-logger?label=PyPI)](https://pypi.org/project/shell-logger/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/shell-logger?label=PyPI%20downloads)
![Python Version](https://img.shields.io/badge/Python-3.8|3.9|3.10|3.11|3.12-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# shell-logger

The `shell-logger` Python package allows you to interact with the shell, while
logging various metadata, statistics, and trace information.  Any time you're
tempted to write your own wrapper around things like `subprocess.Popen()` or
`subprocess.run()`, consider using `shell_logger.ShellLogger.log()` instead.
If you're familiar with [the Unix script command][script], this is similar in
principle, but with substantially more functionality.  If you're familiar with
[Python's logging module][logging], the motivation is similar, but this intends
to capture what's happening *in the shell* rather than in Python itself.

[script]:  https://man7.org/linux/man-pages/man1/script.1.html
[logging]:  https://docs.python.org/3/library/logging.html

## Installation

To get up and running with `shell-logger`, simply:
```bash
python3 -m pip install shell-logger
```

## Usage

Once the package is installed, you can simply
```python
from shell_logger import ShellLogger
sl = ShellLogger("Title of Log File")
sl.log("Execute my first command in the shell.", "echo 'Hello World'")
```

For more detailed usage and API information, please see
[our documentation][readthedocs].

[readthedocs]:  https://shell-logger.readthedocs.io

## Where to Get Help

If you're having trouble with `shell-logger`, or just want to ask a question,
head on over to [our issue board][issues].  If a quick search doesn't yield
what you're looking for, feel free to file an issue.

[issues]:  https://github.com/sandialabs/shell-logger/issues

## Contributing

If you're interested in contributing to the development of `shell-logger`, we'd
love to have your help :grinning:  Check out our
[contributing guidelines](CONTRIBUTING.md) for how to get started.
[Past contributors][contributors] include:
* [@bbraunj](https://github.com/bbraunj)
* [@sswan](https://github.com/sswan)
* [@dc-snl](https://github.com/dc-snl)
* [@jmgate](https://github.com/jmgate)
* [@mvlopri](https://github.com/mvlopri)

[contributors]:  https://github.com/sandialabs/shell-logger/graphs/contributors

## License

See [LICENSE.md](LICENSE.md).

## Credits

Special thanks to the EMPIRE project for investing in the initial development
of this tool, and [the GMS project][gms] for serving as a second user and
contributing to its clean-up.

[gms]: https://github.com/SNL-GMS/GMS-PI25
