[![pipeline status](https://internal.gitlab.server/ShellLogger/ShellLogger/badges/master/pipeline.svg)](https://internal.gitlab.server/ShellLogger/ShellLogger/pipelines)
[![coverage report](https://internal.gitlab.server/ShellLogger/ShellLogger/badges/master/coverage.svg)](http://shelllogger.internal.gitlab.pages/ShellLogger/htmlcov)
[![documentation](https://img.shields.io/badge/docs-latest-green.svg)](http://shelllogger.internal.gitlab.pages/ShellLogger)

# ShellLogger

The `shelllogger` Python module allows you to interact with the shell, while
logging various metadata, statistics, and trace information.  Any time you're
tempted to write your own wrapper around things like `subprocess.Popen()` or
`subprocess.run()`, consider using `shelllogger.ShellLogger.log()` instead.  If
you're familiar with [the Unix script
command](https://man7.org/linux/man-pages/man1/script.1.html), this is similar
in principle, but with substantially more functionality.  If you're familiar
with [Python's logging module](https://docs.python.org/3/library/logging.html),
the motivation is similar, but this intends to capture what's happening *in the
shell* rather than in Python itself.

## Installation

To get up and running with `ShellLogger`, do the following:
```bash
git clone git@internal.gitlab.server:ShellLogger/ShellLogger
cd ShellLogger
python3 -m pip install .
```

> **Note:**  You may want to install the package in a separate Python
> environment, using either
> [conda](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html)
> or [venv](https://docs.python.org/3/tutorial/venv.html).

## Usage

Once the package is installed, you can simply
```python
from shelllogger import ShellLogger
sl = ShellLogger("Title of Log File")
sl.log("Execute my first command in the shell.", "echo 'Hello World'")
```

For more detailed usage and API information, please see [our
documentation](http://shelllogger.internal.gitlab.pages/ShellLogger).

## Adding `ShellLogger` as a Requirement for your Package

If you'll be developing a package that will use `ShellLogger`, we recommend
adding this to your `requirements.txt` file
```
shelllogger @ git+https://internal.gitlab.server/ShellLogger/ShellLogger@master#egg=shelllogger
```

replacing `master` with whatever git reference you like, and then using `pip
install -r requirements.txt` to handle installing it.

## Where to Get Help

If you're having trouble with `ShellLogger`, or just want to ask a question,
head on over to [our issue
board](https://internal.gitlab.server/ShellLogger/ShellLogger/-/issues).  If a
quick search doesn't yield what you're looking for, feel free to file a
~"Type :: Question" issue.

## Contributing

If you're interested in contributing to the development of `ShellLogger`, we'd
love to have your help :grinning:  Check out our [contributing
guidelines](https://internal.gitlab.server/ShellLogger/ShellLogger/-/blob/master/CONTRIBUTING.md)
for how to get started.  [Past
contributors](https://internal.gitlab.server/ShellLogger/ShellLogger/-/graphs/master)
include:
* @josbrau
* @mswan
* @dcollin
* @jmgate

## License

License information will be added after `ShellLogger` makes it through Sandia's
open-sourcing process.

## Credits

Special thanks to the EMPIRE project for investing in the initial development
of this tool, and [the GMS
project](https://internal.corporate.wiki/display/gmswiki/Geophysical+Monitoring+System+Wiki)
for serving as a second user and contributing to its clean-up.
