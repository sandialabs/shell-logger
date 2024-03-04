"""
The unit test suite for the ``shell_logger`` package.
"""

# © 2024 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from inspect import stack
import json
import os
from pathlib import Path
import pytest
import re
from shell_logger import ShellLogger, ShellLoggerDecoder
try:
    import psutil
except ModuleNotFoundError:
    psutil = None


@pytest.fixture(autouse=True)
def use_tmpdir(monkeypatch: MonkeyPatch, tmpdir: Path) -> None:
    """
    **@pytest.fixture(autouse=True)**

    Automatically use a temporary directory as the current working
    directory for all tests.

    Parameters:
        monkeypatch:  The ``MonkeyPatch`` fixture.
        tmpdir:  The temporary directory to use.
    """
    monkeypatch.chdir(tmpdir)


@pytest.fixture()
def shell_logger() -> ShellLogger:
    """
    **@pytest.fixture()**

    This fixture creates a :class:`ShellLogger` object with some sample
    data to be used in tests.  It first creates a sample
    :class:`ShellLogger` object.  Then it logs a command (whose
    ``stdout`` is ``'Hello world'`` and ``stderr`` is ``'Hello world
    error'``).  Next, it adds a child :class:`ShellLogger` object and
    prints something using that child logger.

    Returns:
        The parent :class:`ShellLogger` object described above.
    """

    # Initialize a parent `ShellLogger`.
    parent = ShellLogger('Parent', Path.cwd())

    # Run the command.
    #                      `stdout`        ;               `stderr`
    cmd = (
        "sleep 1; echo 'Hello world out'; sleep 1; echo 'Hello world error' "
        "1>&2"
    )
    measure = ["cpu", "memory", "disk"]
    kwargs = {"measure": measure, "return_info": True, "interval": 0.1}
    if os.uname().sysname == "Linux":
        kwargs.update({
            "trace": "ltrace",
            "expression": "setlocale",
            "summary": True
        })
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested."
        )
    parent.log("test cmd", cmd, Path.cwd(), **kwargs)
    parent.print("This is a message")

    # Add a child and run some commands.
    child = parent.add_child("Child")
    child.print("Hello world child")
    child.log("Test out HTML characters", "echo '<hello> &\"'\"'\"")
    child.log("ls", "ls")
    child.print("Hello again child")

    # Add more to the parent and return the object.
    parent.print("This is another message")
    return parent


def test_initialization_creates_stream_dir() -> None:
    """
    Verify the initialization of a parent :class:`ShellLogger` object
    creates a temporary directory
    (``log_dir/%Y-%m-%d_%H%M%S``<random string>) if not already created.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    timestamp = logger.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f")
    assert len(list(Path.cwd().glob(f"{timestamp}_*"))) == 1


def test_initialization_creates_html_file() -> None:
    """
    Verify the initialization of a parent :class:`ShellLogger` object
    creates a starting HTML file in the :attr:`log_dir`.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    timestamp = logger.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f")
    streamm_dir = next(Path.cwd().glob(f"{timestamp}_*"))
    assert (streamm_dir / f'{stack()[0][3]}.html').exists()


def test_log_method_creates_tmp_stdout_stderr_files(
    shell_logger: ShellLogger
) -> None:
    """
    Verify that logging a command will create files in the
    :class:`ShellLogger` object's :attr:`stream_dir` corresponding to
    the ``stdout`` and ``stderr`` of the command.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """

    # Get the paths for the `stdout`/`stderr` files.
    cmd_id = shell_logger.log_book[0]['cmd_id']
    cmd_ts = shell_logger.log_book[0]['timestamp']
    stdout_file = shell_logger.stream_dir / f"{cmd_ts}_{cmd_id}_stdout"
    stderr_file = shell_logger.stream_dir / f"{cmd_ts}_{cmd_id}_stderr"
    assert stdout_file.exists()
    assert stderr_file.exists()
    print(f"{stdout_file}")
    print(f"{stderr_file}")

    # Make sure the information written to these files is correct.
    with open(stdout_file, 'r') as out, open(stderr_file, 'r') as err:
        out_txt = out.readline()
        err_txt = err.readline()
        assert 'Hello world out' in out_txt
        assert 'Hello world error' in err_txt


@pytest.mark.parametrize('return_info', [True, False])
def test_log_method_return_info_works_correctly(return_info: bool) -> None:
    """
    **@pytest.mark.parametrize('return_info', [True, False])**

    Verify that when ``return_info=True``, we receive a dictionary that
    contains the ``stdout`` and ``stderr`` of the command, as well as
    the ``return_code``, and when ``return_info=False``, we receive the
    ``return_code``, but ``stdout`` and ``stderr`` are ``None``.

    Parameters:
        return_info:  Whether or not to return the
            ``stdout``/``stderr``.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())

    #           `stdout`         ;      `stderr`
    cmd = "echo 'Hello world out'; echo 'Hello world error' 1>&2"
    result = logger.log("test cmd", cmd, Path.cwd(), return_info=return_info)
    if return_info:
        assert "Hello world out" in result['stdout']
        assert "Hello world error" in result['stderr']
        assert result['return_code'] == 0
    else:
        assert result['stdout'] is None
        assert result['stderr'] is None
        assert result['return_code'] == 0


@pytest.mark.parametrize('live_stdout', [True, False])
@pytest.mark.parametrize('live_stderr', [True, False])
def test_log_method_live_stdout_stderr_works_correctly(
    capsys: CaptureFixture,
    live_stdout: bool,
    live_stderr: bool
) -> None:
    """
    Verify that the ``live_stdout`` and ``live_stdout`` flags work as
    expected for the :func:`log` method.

    Parameters:
        capsys: A fixture to capture ``stdout``/``stderr``.
        live_stdout:  Whether or not to capture ``stdout`` while running
            the :func:`log` command.
        live_stderr:  Whether or not to capture ``stderr`` while running
            the :func:`log` command.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = "echo 'Hello world out'; echo 'Hello world error' 1>&2"
    logger.log("test cmd", cmd, Path.cwd(), live_stdout, live_stderr)
    out, err = capsys.readouterr()
    if live_stdout:
        assert re.search(r"^Hello world out(\r)?\n", out) is not None
    else:
        assert re.search(r"^Hello world out(\r)?\n", out) is None
    if live_stderr:
        assert re.search(r"^Hello world error(\r)?\n", err) is not None
    else:
        assert re.search(r"^Hello world error(\r)?\n", err) is None


def test_child_logger_duration_displayed_correctly_in_html(
    shell_logger: ShellLogger
) -> None:
    """
    Verify that the overview of child loggers in the HTML file displays
    the correct child :class:`ShellLogger` duration, not the entire
    log's duration.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """
    child2 = shell_logger.add_child("Child 2")
    child2.log("Wait 0.005s", "sleep 0.005")
    child3 = shell_logger.add_child("Child 3")
    child3.log("Wait 0.006s", "sleep 0.006")
    shell_logger.finalize()
    with open(shell_logger.html_file, 'r') as hf:
        html_text = hf.read()
    assert child2.duration is not None
    assert f"Duration: {child2.duration}" in html_text
    assert child3.duration is not None
    assert f"Duration: {child3.duration}" in html_text


def test_finalize_creates_json_with_correct_information(
    shell_logger: ShellLogger
) -> None:
    """
    Verify that the :func:`finalize` method creates a JSON file with the
    proper data.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """
    shell_logger.finalize()

    # Load from JSON.
    json_file = shell_logger.stream_dir / "Parent.json"
    assert json_file.exists()
    with open(json_file, 'r') as jf:
        loaded_logger = json.load(jf, cls=ShellLoggerDecoder)

    # Parent `ShellLogger`.
    assert shell_logger.log_dir == loaded_logger.log_dir
    assert shell_logger.stream_dir == loaded_logger.stream_dir
    assert shell_logger.html_file == loaded_logger.html_file
    assert shell_logger.indent == loaded_logger.indent
    assert shell_logger.name == loaded_logger.name
    assert shell_logger.init_time == loaded_logger.init_time
    assert shell_logger.done_time == loaded_logger.done_time
    assert shell_logger.log_book[0] == loaded_logger.log_book[0]

    # Child `ShellLogger`.
    child = shell_logger.log_book[2]
    loaded_child = loaded_logger.log_book[2]
    assert child.log_dir == loaded_child.log_dir
    assert child.stream_dir == loaded_child.stream_dir
    assert child.html_file == loaded_child.html_file
    assert child.indent == loaded_child.indent
    assert child.name == loaded_child.name
    assert child.init_time == loaded_child.init_time
    assert child.done_time == loaded_child.done_time
    assert child.log_book[0] == loaded_child.log_book[0]


def test_finalize_creates_html_with_correct_information(
    shell_logger: ShellLogger
) -> None:
    """
    Verify that the :func:`finalize` method creates an HTML file with
    the proper data.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """
    shell_logger.finalize()

    # Load the HTML file.
    html_file = shell_logger.stream_dir / "Parent.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        html_text = hf.read()

    # Ensure the command information is present.
    assert ">test cmd</" in html_text
    assert f"Duration: {shell_logger.log_book[0]['duration']}" in html_text
    assert f"Time:</span> {shell_logger.log_book[0]['timestamp']}" in html_text
    assert (
        "Command:</span> <pre><code>sleep 1; echo 'Hello world out'; sleep 1; "
        "echo 'Hello world error' 1&gt;&amp;2"
    ) in html_text
    assert f"CWD:</span> {Path.cwd()}" in html_text
    assert "Return Code:</span> 0" in html_text

    # Check to see that the print statement information is there.
    assert "Hello world child" in html_text
    if os.uname().sysname == "Linux":
        assert "trace</" in html_text
        assert "setlocale" in html_text
    else:
        print(
            f"Warning:  uname is not 'Linux':  {os.uname()}; trace not tested."
        )
    assert "getenv" not in html_text
    assert 'class="card-title">Memory Usage' in html_text
    assert "<canvas" in html_text
    assert "</canvas>" in html_text
    assert 'class="card-title">CPU Usage' in html_text
    assert 'class="card-title">Used Space on /' in html_text
    assert "Environment</" in html_text
    assert "PATH=" in html_text
    assert "Hostname:</span>" in html_text
    assert "User:</span>" in html_text
    assert "Group:</span>" in html_text
    assert "Shell:</span>" in html_text
    assert "umask:</span>" in html_text
    assert "ulimit</" in html_text

    # Check the child `ShellLogger`.
    assert "Child</" in html_text


def test_log_dir_html_symlinks_to_stream_dir_html(
    shell_logger: ShellLogger
) -> None:
    """
    Verify that the :func:`finalize` method symlinks
    ``log_dir/html_file`` to ``streamm_dir/html_file``.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """
    shell_logger.finalize()

    # Load the HTML file.
    html_file = shell_logger.stream_dir / "Parent.html"
    html_symlink = shell_logger.log_dir / "Parent.html"
    assert html_file.exists()
    assert html_symlink.exists()
    assert html_symlink.resolve() == html_file


def test_json_file_can_reproduce_html_file(
    shell_logger: ShellLogger
) -> None:  # yapf: disable
    """
    Verify that a JSON file can properly recreate the original HTML file
    created when :func:`finalize` is called.

    Parameters:
        shell_logger:  A pre-populated :class:`ShellLogger` object.
    """
    shell_logger.finalize()

    # Load the original HTML file's contents.
    html_file = shell_logger.log_dir / "Parent.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        original_html = hf.read()

    # Delete the HTML file.
    html_file.unlink()

    # Load the JSON data.
    json_file = shell_logger.stream_dir / "Parent.json"
    assert json_file.exists()
    with open(json_file, 'r') as jf:
        loaded_logger = json.load(jf, cls=ShellLoggerDecoder)

    # Finalize the loaded `ShellLogger` object.
    loaded_logger.finalize()

    # Load the new HTML file's contents and compare.
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        new_html = hf.read()
    print(f"New Read: {html_file.resolve()}")
    assert original_html == new_html


def test_under_stress() -> None:
    """
    Test that all is well when handling lots of output.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = (
        "dd if=/dev/urandom bs=1024 count=262144 | "
        "LC_ALL=C tr -c '[:print:]' '*' ; sleep 1"
    )
    msg = "Get 256 MB of stdout from /dev/urandom"
    logger.log(msg, cmd)
    assert logger.log_book[0]["returncode"] == 0


def test_heredoc() -> None:
    """
    Ensure that heredocs in the command to be executed don't break
    things.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = "bash << EOF\necho hello\nEOF"
    msg = "Test out a heredoc"
    result = logger.log(msg, cmd)
    assert result["return_code"] == 0


def test_devnull_stdin() -> None:
    """
    Ensure ``stdin`` is redirected to ``/dev/null`` by default.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = "cat"
    msg = "Make sure stdin is redirected to /dev/null by default"
    result = logger.log(msg, cmd)
    assert result["return_code"] == 0


def test_syntax_error() -> None:
    """
    Ensure syntax errors are handled appropriately.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = "echo (this is a syntax error"
    msg = "Test out a syntax error"
    with pytest.raises(RuntimeError) as excinfo:
        logger.log(msg, cmd)
    assert "There was a problem running the command" in excinfo.value.args[0]


@pytest.mark.skipif(psutil is None, reason="`psutil` is unavailable")
def test_logger_does_not_store_stdout_string_by_default() -> None:
    """
    Ensure we don't hold a commands ``stdout`` in memory by default.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    cmd = (
        "dd if=/dev/urandom bs=1024 count=262144 | "
        "LC_ALL=C tr -c '[:print:]' '*' ; sleep 1"
    )
    msg = "Get 256 MB of stdout from /dev/urandom"
    logger.log(msg, cmd)
    mem_usage = psutil.Process().memory_info().rss
    bytes_in_128_mb = 134_217_728
    assert mem_usage < bytes_in_128_mb
    logger.log(msg, cmd, return_info=True)
    mem_usage = psutil.Process().memory_info().rss
    assert mem_usage > bytes_in_128_mb


@pytest.mark.skipif(
    os.uname().sysname == "Darwin",
    reason="`ltrace` doesn't exist for Darwin"
)
def test_logger_does_not_store_trace_string_by_default() -> None:
    """
    Ensure we don't keep trace output in memory by default.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    logger.log("echo hello", "echo hello", Path.cwd(), trace="ltrace")
    assert logger.log_book[0]["trace"] is None
    logger.log(
        "echo hello",
        "echo hello",
        Path.cwd(),
        return_info=True,
        trace="ltrace"
    )
    assert logger.log_book[1]["trace"] is not None


def test_stdout() -> None:
    """
    Ensure printing to ``stdout`` works.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    assert logger._run(":").stdout == ""
    assert logger._run("echo hello").stdout == "hello\n"


def test_returncode_no_op() -> None:
    """
    Ensure the return code for the `:` command is 0.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    assert logger._run(":").returncode == 0


def test_args() -> None:
    """
    Ensure we accurately capture the command that was run.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    assert logger._run("echo hello").args == "echo hello"


def test_stderr() -> None:
    """
    Ensure we accurately capture ``stderr``.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    command = "echo hello 1>&2"
    assert logger._run(command).stderr == "hello\n"
    assert logger._run(command).stdout == ""


def test_timing() -> None:
    """
    Ensure we accurately capture the wall clock time of a command.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    command = "sleep 1"
    if os.name == "posix":
        command = "sleep 1"
    else:
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger._run(command)
    assert result.wall >= 1000
    assert result.wall < 2000
    assert result.finish >= result.start


def test_auxiliary_data() -> None:
    """
    Ensure we accurately capture all the auxiliary data when executing a
    command.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    result = logger._run("pwd")
    assert result.pwd == result.stdout.strip()
    result = logger._run(":")
    assert "PATH=" in result.environment
    assert logger._run("hostname").stdout.strip() == result.hostname
    assert logger._run("whoami").stdout.strip() == result.user
    if os.name == "posix":
        assert len(result.umask) == 3 or len(result.umask) == 4
        assert logger._run("id -gn").stdout.strip() == result.group
        assert logger._run("printenv SHELL").stdout.strip() == result.shell
        assert logger._run("ulimit -a").stdout == result.ulimit
    else:
        print(
            f"Warning: os.name is not 'posix': {os.name}; umask, group, "
            "shell, and ulimit not tested."
        )


def test_working_directory() -> None:
    """
    Ensure we accurately capture the working directory when executing a
    command.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    command = "pwd"
    directory = "/tmp"
    if os.name != "posix":
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger._run(command, pwd=directory)
    assert result.stdout.strip() == directory
    assert result.pwd == directory


def test_trace() -> None:
    """
    Ensure we accurately capture trace output.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger._run("echo letter", trace="ltrace")
        assert 'getenv("POSIXLY_CORRECT")' in result.trace
        echo_location = logger._run("which echo").stdout.strip()
        result = logger._run("echo hello", trace="strace")
        assert f'execve("{echo_location}' in result.trace
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace not "
            "tested."
        )


def test_trace_expression() -> None:
    """
    Ensure specifying a trace expression works correctly.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger._run("echo hello", trace="ltrace", expression='getenv')
        assert 'getenv("POSIXLY_CORRECT")' in result.trace
        assert result.trace.count('\n') == 2
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; ltrace expression "
            "not tested."
        )


def test_trace_summary() -> None:
    """
    Ensure requesting a trace summary works correctly.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger._run("echo hello", trace="ltrace", summary=True)
        assert 'getenv("POSIXLY_CORRECT")' not in result.trace
        assert "getenv" in result.trace
        echo_location = logger._run("which echo").stdout.strip()
        result = logger._run("echo hello", trace="strace", summary=True)
        assert f'execve("{echo_location}' not in result.trace
        assert "execve" in result.trace
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace "
            "summary not tested."
        )


def test_trace_expression_and_summary() -> None:
    """
    Ensure specifying a trace expression and requesting a summary works
    correctly.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        echo_location = logger._run("which echo").stdout.strip()
        result = logger._run(
            "echo hello",
            trace="strace",
            expression="execve",
            summary=True
        )
        assert f'execve("{echo_location}' not in result.trace
        assert "execve" in result.trace
        assert "getenv" not in result.trace
        result = logger._run(
            "echo hello",
            trace="ltrace",
            expression="getenv",
            summary=True
        )
        assert 'getenv("POSIXLY_CORRECT")' not in result.trace
        assert "getenv" in result.trace
        assert "strcmp" not in result.trace
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace "
            "expression+summary not tested."
        )


def test_stats() -> None:
    """
    Ensure capturing CPU, memory, and disk statistics works correctly.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    measure = ["cpu", "memory", "disk"]
    result = logger._run("sleep 2", measure=measure, interval=0.1)
    assert len(result.stats["memory"]) > 1
    assert len(result.stats["memory"]) < 30
    assert len(result.stats["cpu"]) > 1
    assert len(result.stats["cpu"]) < 30
    if os.name == "posix":
        assert len(result.stats["disk"]["/"]) > 1
        assert len(result.stats["disk"]["/"]) < 30
    else:
        print(
            f"Warning: os.name is not 'posix': {os.name}; disk usage not "
            "fully tested."
        )


def test_trace_and_stats() -> None:
    """
    Ensure both tracing a command and capturing multiple statistics work
    together.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        measure = ["cpu", "memory", "disk"]
        result = logger._run(
            "sleep 1",
            measure=measure,
            interval=0.1,
            trace="ltrace",
            expression="setlocale",
            summary=True
        )
        assert "setlocale" in result.trace
        assert "sleep" not in result.trace
        assert len(result.stats["memory"]) > 5
        assert len(result.stats["memory"]) < 50
        assert len(result.stats["cpu"]) > 5
        assert len(result.stats["cpu"]) < 50
        assert len(result.stats["disk"]["/"]) > 5
        assert len(result.stats["disk"]["/"]) < 50
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested."
        )


def test_trace_and_stat() -> None:
    """
    Ensure both tracing a command and capturing a single statistic work
    together.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger._run(
            "sleep 1",
            measure=["cpu"],
            interval=0.1,
            trace="ltrace",
            expression="setlocale",
            summary=True
        )
        assert "setlocale" in result.trace
        assert "sleep" not in result.trace
        assert result.stats.get("memory") is None
        assert result.stats.get("disk") is None
        assert result.stats.get("cpu") is not None
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested."
        )


@pytest.mark.skipif(
    os.uname().sysname == "Darwin",
    reason="`ltrace`/`strace` don't exist for Darwin"
)
@pytest.mark.skip(reason="Not sure it's worth it to fix this or not")
def test_set_env_trace() -> None:
    """
    Ensure setting an environment variable while tracing a command
    works.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    result = logger._run("TEST_ENV=abdc env | grep TEST_ENV", trace="ltrace")
    assert "TEST_ENV=abdc" in result.stdout
    result = logger._run("TEST_ENV=abdc env | grep TEST_ENV", trace="strace")
    assert "TEST_ENV=abdc" in result.stdout


def test_log_book_trace_and_stats() -> None:
    """
    Ensure trace and statistics are accurately captured in the log book.
    """
    if os.uname().sysname == "Linux":
        logger = ShellLogger(stack()[0][3], Path.cwd())
        measure = ["cpu", "memory", "disk"]
        logger.log(
            "Sleep",
            "sleep 1",
            return_info=True,
            measure=measure,
            interval=0.1,
            trace="ltrace",
            expression="setlocale",
            summary=True
        )
        assert "setlocale" in logger.log_book[0]["trace"]
        assert "sleep" not in logger.log_book[0]["trace"]
        assert len(logger.log_book[0]["stats"]["memory"]) > 5
        assert len(logger.log_book[0]["stats"]["memory"]) < 50
        assert len(logger.log_book[0]["stats"]["cpu"]) > 5
        assert len(logger.log_book[0]["stats"]["cpu"]) < 50
        assert len(logger.log_book[0]["stats"]["disk"]["/"]) > 5
        assert len(logger.log_book[0]["stats"]["disk"]["/"]) < 50
    else:
        print(
            f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested."
        )


def test_change_pwd() -> None:
    """
    Ensure changing directories affects subsequent calls.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    pwd_command = "pwd"
    directory1 = "/"
    directory2 = "/tmp"
    if os.name != "posix":
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    logger._run(f"cd {directory1}")
    result = logger._run(pwd_command)
    assert result.stdout.strip() == directory1
    assert result.pwd == directory1
    logger._run(f"cd {directory2}")
    result = logger._run(pwd_command)
    assert result.stdout.strip() == directory2
    assert result.pwd == directory2


def test_returncode() -> None:
    """
    Ensure we get the expected return code when a command fails.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    command = "false"
    expected_returncode = 1
    if os.name != "posix":
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger._run(command)
    assert result.returncode == expected_returncode


def test_sgr_gets_converted_to_html() -> None:
    """
    Ensure Select Graphic Rendition (SGR) codes get accurately
    translated to valid HTML/CSS.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    logger.print("\x1B[31mHello\x1B[0m")
    logger.print("\x1B[31;43m\x1B[4mthere\x1B[0m")
    logger.print("\x1B[38;5;196m\x1B[48;5;232m\x1B[4mmr.\x1B[0m logger")
    logger.print(
        "\x1B[38;2;96;140;240m\x1B[48;2;240;140;10mmrs.\x1B[0m logger"
    )
    logger.finalize()

    # Load the HTML file and make sure it checks out.
    html_file = logger.stream_dir / f"{logger.name}.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        html_text = hf.read()
    assert "\x1B" not in html_text
    assert ">Hello</span>" in html_text
    assert ">there</span>" in html_text
    assert ">mr.</span></span></span> logger" in html_text
    assert "color: rgb(255, 0, 0)" in html_text
    assert "background-color: rgb(" in html_text
    assert ">mrs.</span></span> logger" in html_text
    assert "color: rgb(96, 140, 240)" in html_text
    assert "background-color: rgb(240, 140, 10)" in html_text


def test_html_print(capsys: CaptureFixture) -> None:
    """
    Ensure the :func:`print` method prints to both the HTML log and the
    console, but the :func:`html_print` method only prints to the log
    file.

    Parameters:
        capsys:  A fixture for capturing the ``stdout``.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    logger.html_print(
        "The quick brown fox jumps over the lazy dog.",
        msg_title="Brown Fox"
    )
    logger.print("The quick orange zebra jumps over the lazy dog.")
    out, err = capsys.readouterr()
    logger.finalize()

    # Load the HTML file and make sure it checks out.
    html_file = logger.stream_dir / f"{logger.name}.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        html_text = hf.read()
    assert "brown fox" not in out
    assert "brown fox" not in err
    assert "Brown Fox" not in out
    assert "Brown Fox" not in err
    assert "brown fox" in html_text
    assert "Brown Fox" in html_text
    assert "orange zebra" not in err
    assert "orange zebra" in out
    assert "orange zebra" in html_text


def test_append_mode() -> None:
    """
    Ensure we're able to append to a previously generated log file.
    """
    logger1 = ShellLogger(stack()[0][3] + "_1", Path.cwd())
    logger1.log("Print HELLO to stdout", "echo HELLO")
    logger1.print("Printed once to stdout")
    logger1.html_print("Printed ONCE to STDOUT")
    logger1.finalize()

    logger2 = ShellLogger.append(logger1.html_file)
    logger2.log("Print THERE to stdout", "echo THERE")
    logger2.print("Printed twice to stdout")
    logger2.html_print("Printed TWICE to STDOUT")
    logger2.finalize()

    logger3 = ShellLogger.append(logger2.log_dir)
    logger3.log("Print LOGGER to stdout", "echo LOGGER")
    logger3.print("Printed thrice to stdout")
    logger3.html_print("Printed THRICE to STDOUT")
    logger3.finalize()

    logger4 = ShellLogger.append(logger3.stream_dir)
    logger4.log("Print !!! to stdout", "echo '!!!'")
    logger4.print("Printed finally to stdout")
    logger4.html_print("Printed FINALLY to STDOUT")
    logger4.finalize()

    logger5 = ShellLogger.append(logger4.stream_dir / f"{logger4.name}.json")
    logger5.log("Print 111 to stdout", "echo '111'")
    logger5.print("Printed for real to stdout")
    logger5.html_print("Printed FOR REAL to STDOUT")
    logger5.finalize()

    # Load the HTML file and ensure it checks out.
    html_file = logger1.stream_dir / f"{logger1.name}.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        html_text = hf.read()
    assert "once" in html_text
    assert "ONCE" in html_text
    assert "HELLO" in html_text
    assert "twice" in html_text
    assert "TWICE" in html_text
    assert "THERE" in html_text
    assert "thrice" in html_text
    assert "THRICE" in html_text
    assert "LOGGER" in html_text
    assert "finally" in html_text
    assert "FINALLY" in html_text
    assert "!!!" in html_text
    assert "for real" in html_text
    assert "FOR REAL" in html_text
    assert "111" in html_text


def test_invalid_decodings() -> None:
    """
    Ensure we appropriately handle invalid bytes when decoding output.
    """
    logger = ShellLogger(stack()[0][3], Path.cwd())
    result = logger.log(
        "Print invalid start byte for bytes decode()",
        "printf '\\xFDHello\\n'",
        return_info=True
    )
    assert result["stdout"] == "Hello\n"
