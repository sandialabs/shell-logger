from inspect import stack
import json
import os
import psutil
import pytest
import re
import sys
import time
from multiprocessing import Process
from pathlib import Path
build_script_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, build_script_dir / "logger")
from logger import Logger, LoggerDecoder


def test_initialization_creates_strm_dir():
    """
    Verify the initialization of a parent :class:`Logger` object creates a
    temporary directory (``log_dir/%Y-%m-%d_%H%M%S``<random string>) if not
    already created.
    """

    logger = Logger(stack()[0][3], Path.cwd())
    timestamp = logger.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f")
    assert len(list(Path.cwd().glob(f"{timestamp}_*"))) == 1


def test_initialization_creates_html_file():
    """
    Verify the initialization of a parent :class:`Logger` object creates a
    starting HTML file in the :attr:`log_dir`.
    """

    logger = Logger(stack()[0][3], Path.cwd())
    timestamp = logger.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f")
    strm_dir = next(Path.cwd().glob(f"{timestamp}_*"))
    assert (strm_dir / f'{stack()[0][3]}.html').exists()


def test_log_method_creates_tmp_stdout_stderr_files(logger):
    """
    Verify that logging a command will create files in the :class:`Logger`
    object's :attr:`strm_dir` corresponding to the ``stdout`` and ``stderr`` of
    the command.
    """

    # Get the paths for the stdout/stderr files.
    cmd_id = logger.log_book[0]['cmd_id']
    cmd_ts = logger.log_book[0]['timestamp']
    stdout_file = logger.strm_dir / f"{cmd_ts}_{cmd_id}_stdout"
    stderr_file = logger.strm_dir / f"{cmd_ts}_{cmd_id}_stderr"

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
def test_log_method_return_info_works_correctly(return_info):
    """
    **@pytest.mark.parametrize('return_info', [True, False])**

    Verify that when ``return_info=True``, we receive a dictionary that
    contains the ``stdout`` and ``stderr`` of the command, as well as the
    ``return_code``, and when ``return_info=False``, we receive the
    ``return_code``, but ``stdout`` and ``stderr`` are ``None``.
    """

    logger = Logger(stack()[0][3], Path.cwd())

    #            stdout          ;        stderr
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
def test_log_method_live_stdout_stderr_works_correctly(capsys, live_stdout,
                                                       live_stderr):
    """
    Verify that the ``live_stdout`` and ``live_stdout`` flags work as expected
    for the :func:`log` method.
    """

    logger = Logger(stack()[0][3], Path.cwd())

    #            stdout          ;        stderr
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


def test_child_logger_duration_displayed_correctly_in_HTML(logger):
    """
    Verify that the overview of child loggers in the HTML file displays the
    correct child logger duration, not the entire log's duration.
    """

    child2 = logger.add_child("Child 2")
    child2.log("Wait 0.005s", ["sleep", "0.005"])

    child3 = logger.add_child("Child 3")
    child3.log("Wait 0.006s", ["sleep", "0.006"])

    logger.finalize()

    with open(logger.html_file, 'r') as hf:
        html_text = hf.read()

    assert child2.duration is not None
    assert f"<br>Duration: {child2.duration}\n" in html_text

    assert child3.duration is not None
    assert f"<br>Duration: {child3.duration}\n" in html_text


def test_finalize_creates_JSON_with_correct_information(logger):
    """
    Verify that the :func:`finalize` method creates a JSON file with the proper
    data.
    """

    logger.finalize()

    # Load from JSON.
    json_file = logger.strm_dir / "Parent.json"
    assert json_file.exists()
    with open(json_file, 'r') as jf:
        loaded_logger = json.load(jf, cls=LoggerDecoder)

    # Parent Logger
    assert logger.log_dir == loaded_logger.log_dir
    assert logger.strm_dir == loaded_logger.strm_dir
    assert logger.html_file == loaded_logger.html_file
    assert logger.indent == loaded_logger.indent
    assert logger.name == loaded_logger.name
    assert logger.init_time == loaded_logger.init_time
    assert logger.done_time == loaded_logger.done_time
    assert logger.log_book[0] == loaded_logger.log_book[0]

    # Child Logger
    child = logger.log_book[2]
    loaded_child = loaded_logger.log_book[2]
    assert child.log_dir == loaded_child.log_dir
    assert child.strm_dir == loaded_child.strm_dir
    assert child.html_file == loaded_child.html_file
    assert child.indent == loaded_child.indent
    assert child.name == loaded_child.name
    assert child.init_time == loaded_child.init_time
    assert child.done_time == loaded_child.done_time
    assert child.log_book[0] == loaded_child.log_book[0]


def test_finalize_creates_HTML_with_correct_information(logger):
    """
    Verify that the :func:`finalize` method creates an HTML file with the
    proper data.
    """

    logger.finalize()

    # Load the HTML file.
    html_file = logger.strm_dir / "Parent.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        html_text = hf.read()

    # Command info.
    assert ">test cmd</" in html_text
    assert f"Duration: {logger.log_book[0]['duration']}" in html_text
    assert f"Time:</b> {logger.log_book[0]['timestamp']}" in html_text
    assert "Command:</b> <code>echo 'Hello world out'; "\
        "echo 'Hello world error' 1&gt;&amp;2" in html_text
    assert f"CWD:</b> {Path.cwd()}" in html_text
    assert "Return Code:</b> 0" in html_text

    # Print statement.
    assert "Hello world child" in html_text
    assert "trace</" in html_text
    assert "setlocale" in html_text
    assert "getenv" not in html_text
    assert 'class="card-title">Memory Usage' in html_text
    assert "<canvas" in html_text
    assert "</canvas>" in html_text
    assert 'class="card-title">CPU Usage' in html_text
    assert 'class="card-title">Used Space on /' in html_text
    assert "Environment</" in html_text
    assert "PATH=" in html_text
    assert "Hostname:" in html_text
    assert "User:" in html_text
    assert "Group:" in html_text
    assert "Shell:" in html_text
    assert "umask:" in html_text
    assert "ulimit</" in html_text

    # Child Logger
    assert "Child</" in html_text


def test_log_dir_HTML_symlinks_to_strm_dir_HTML(logger):
    """
    Verify that the :func:`finalize` method symlinks log_dir/html_file to
    strm_dir/html_file.
    """

    logger.finalize()

    # Load the HTML file.
    html_file = logger.strm_dir / "Parent.html"
    html_symlink = logger.log_dir / "Parent.html"
    assert html_file.exists()
    assert html_symlink.exists()

    assert html_symlink.resolve() == html_file


def test_JSON_file_can_reproduce_HTML_file(logger):
    """
    Verify that a JSON file can properly recreate the original HTML file
    created when :func:`finalize` is called.
    """

    logger.finalize()

    # Load the original HTML file's contents.
    html_file = logger.log_dir / "Parent.html"
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        original_html = hf.read()

    # Delete the HTML file.
    html_file.unlink()

    # Load the JSON data.
    json_file = logger.strm_dir / "Parent.json"
    assert json_file.exists()
    with open(json_file, 'r') as jf:
        loaded_logger = json.load(jf, cls=LoggerDecoder)

    # Call finalize on the loaded Logger object.
    loaded_logger.finalize()

    # Load the new HTML file's contents and compare.
    assert html_file.exists()
    with open(html_file, 'r') as hf:
        new_html = hf.read()
    print(f"New Read: {html_file.resolve()}") #^#^#^#^#

    assert original_html == new_html


def test_under_stress():
    logger = Logger(stack()[0][3], Path.cwd())
    cmd = ("dd if=/dev/urandom bs=1024 count=262144 | "
           "LC_ALL=C tr -c '[:print:]' '*' ; sleep 1")
    msg = "Get 256 MB of stdout from /dev/urandom"
    logger.log(msg, cmd)
    assert logger.log_book[0]["returncode"] == 0


def test_heredoc():
    logger = Logger(stack()[0][3], Path.cwd())
    cmd = "bash << EOF\necho hello\nEOF"
    msg = "Test out a heredoc"

    p = Process(target=logger.log, args=(msg, cmd))
    p.start()
    p.join(1)
    assert not p.is_alive()


def test_devnull_stdin():
    logger = Logger(stack()[0][3], Path.cwd())
    cmd = "cat"
    msg = "Make sure stdin is redirected to /dev/null by default"

    p = Process(target=logger.log, args=(msg, cmd))
    p.start()
    p.join(1)
    assert not p.is_alive()


def test_syntax_error():
    logger = Logger(stack()[0][3], Path.cwd())
    cmd = "echo (this is a syntax error"
    msg = "Test out a syntax error"

    p = Process(target=logger.log, args=(msg, cmd))
    p.start()
    p.join(1)
    assert not p.is_alive()


def test_logger_does_not_store_stdout_string_by_default():
    logger = Logger(stack()[0][3], Path.cwd())
    cmd = ("dd if=/dev/urandom bs=1024 count=262144 | "
           "LC_ALL=C tr -c '[:print:]' '*' ; sleep 1")
    msg = "Get 256 MB of stdout from /dev/urandom"

    p = Process(target=logger.log, args=(msg, cmd))
    p.start()
    time.sleep(1)
    psutil_process = psutil.Process(p.pid)
    mem_usage = psutil_process.memory_info().rss
    p.join()
    # 134217728 bytes = 128 MB
    assert mem_usage < 134217728

    p = Process(target=logger.log, args=(msg, cmd, None, False, False, True))
    p.start()
    time.sleep(1)
    psutil_process = psutil.Process(p.pid)
    mem_usage = psutil_process.memory_info().rss
    p.join()
    # 134217728 bytes = 128 MB
    assert mem_usage > 134217728

def test_logger_does_not_store_trace_string_by_default():
    logger = Logger(stack()[0][3], Path.cwd())

    logger.log("echo hello",
               "echo hello",
               Path.cwd(),
               trace="ltrace")
    assert logger.log_book[0]["trace"] is None

    logger.log("echo hello",
               "echo hello",
               Path.cwd(),
               return_info=True,
               trace="ltrace")
    assert logger.log_book[1]["trace"] is not None

def test_stdout():
    logger = Logger(stack()[0][3], Path.cwd())
    assert logger.run(":").stdout == ""
    assert logger.run("echo hello").stdout == "hello\n"

def test_returncode():
    logger = Logger(stack()[0][3], Path.cwd())
    assert logger.run(":").returncode == 0

def test_args():
    logger = Logger(stack()[0][3], Path.cwd())
    assert logger.run("echo hello").args == "echo hello"

def test_stderr():
    logger = Logger(stack()[0][3], Path.cwd())
    command = "echo hello 1>&2"
    assert logger.run(command).stderr == "hello\n"
    assert logger.run(command).stdout == ""

def test_timing():
    logger = Logger(stack()[0][3], Path.cwd())
    command = "sleep 1"
    if os.name == "posix":
        command = "sleep 1"
    elif os.name == "nt":
        command = "timeout /nobreak /t 1"
    else:
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger.run(command)
    assert result.wall >= 1000
    assert result.wall < 2000
    assert result.finish >= result.start

def test_auxiliaryData():
    logger = Logger(stack()[0][3], Path.cwd())
    result = logger.run("pwd")
    assert result.pwd == result.stdout.strip()
    result = logger.run(":")
    assert "PATH=" in result.environment
    assert logger.run("hostname").stdout.strip() == result.hostname
    assert logger.run("whoami").stdout.strip() == result.user
    if os.name == "posix":
        assert len(result.umask) == 3 or len(result.umask) == 4
        assert logger.run("id -gn").stdout.strip() == result.group
        assert logger.run("printenv SHELL").stdout.strip() == result.shell
        assert logger.run("ulimit -a").stdout == result.ulimit
    else:
        print(f"Warning: os.name is not 'posix': {os.name}; umask, "
               "group, shell, and ulimit not tested.")

def test_workingDirectory():
    logger = Logger(stack()[0][3], Path.cwd())
    command = "pwd"
    directory = "/tmp"
    if os.name == "posix":
        command = "pwd"
        directory = "/tmp"
    elif os.name == "nt":
        command = "cd"
        directory = "C:\\Users"
    else:
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger.run(command, pwd=directory)
    assert result.stdout.strip() == directory
    assert result.pwd == directory

def test_trace():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger.run("echo letter", trace="ltrace")
        assert 'getenv("POSIXLY_CORRECT")' in result.trace
        echoLocation = logger.run("which echo").stdout.strip()
        result = logger.run("echo hello", trace="strace")
        assert f'execve("{echoLocation}' in result.trace
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace "
               "not tested.")

def test_traceExpression():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger.run("echo hello",
                         trace="ltrace",
                         expression='getenv')
        assert 'getenv("POSIXLY_CORRECT")' in result.trace
        assert result.trace.count('\n') == 2
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; ltrace "
               "expression not tested.")

def test_traceSummary():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger.run("echo hello", trace="ltrace", summary=True)
        assert 'getenv("POSIXLY_CORRECT")' not in result.trace
        assert "getenv" in result.trace
        echoLocation = logger.run("which echo").stdout.strip()
        result = logger.run("echo hello", trace="strace", summary=True)
        assert f'execve("{echoLocation}' not in result.trace
        assert "execve" in result.trace
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace "
               "summary not tested.")

def test_traceExpressionAndSummary():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        echoLocation = logger.run("which echo").stdout.strip()
        result = logger.run("echo hello",
                         trace="strace",
                         expression="execve",
                         summary=True)
        assert f'execve("{echoLocation}' not in result.trace
        assert "execve" in result.trace
        assert "getenv" not in result.trace
        result = logger.run("echo hello",
                         trace="ltrace",
                         expression="getenv",
                         summary=True)
        assert 'getenv("POSIXLY_CORRECT")' not in result.trace
        assert "getenv" in result.trace
        assert "strcmp" not in result.trace
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; strace/ltrace "
               "expression+summary not tested.")

def test_stats():
    logger = Logger(stack()[0][3], Path.cwd())
    result = logger.run("sleep 1", measure=["cpu", "memory", "disk"], interval=0.1)
    assert len(result.stats["memory"]) > 8
    assert len(result.stats["memory"]) < 30
    assert len(result.stats["cpu"]) > 8
    assert len(result.stats["cpu"]) < 30
    if os.name == "posix":
        assert len(result.stats["disk"]["/"]) > 8
        assert len(result.stats["disk"]["/"]) < 30
    else:
        print(f"Warning: os.name is not 'posix': {os.name}; disk usage not fully tested.")

def test_traceAndStats():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger.run("sleep 1",
                            measure=["cpu", "memory", "disk"],
                            interval=0.1,
                            trace="ltrace",
                            expression="setlocale",
                            summary=True)
        assert "setlocale" in result.trace
        assert "sleep" not in result.trace
        assert len(result.stats["memory"]) > 8
        assert len(result.stats["memory"]) < 30
        assert len(result.stats["cpu"]) > 8
        assert len(result.stats["cpu"]) < 30
        assert len(result.stats["disk"]["/"]) > 8
        assert len(result.stats["disk"]["/"]) < 30
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested.")

def test_traceAndStat():
    logger = Logger(stack()[0][3], Path.cwd())
    if os.uname().sysname == "Linux":
        result = logger.run("sleep 1",
                            measure=["cpu"],
                            interval=0.1,
                            trace="ltrace",
                            expression="setlocale",
                            summary=True)
        assert "setlocale" in result.trace
        assert "sleep" not in result.trace
        assert result.stats.get("memory") is None
        assert result.stats.get("disk") is None
        assert result.stats.get("cpu") is not None
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested.")

@pytest.mark.skip(reason="Not sure it's worth it to fix this or not")
def test_set_env_trace():
    logger = Logger(stack()[0][3], Path.cwd())
    result = logger.run("TEST_ENV=abdc env | grep TEST_ENV", trace="ltrace")
    assert "TEST_ENV=abdc" in result.stdout
    result = logger.run("TEST_ENV=abdc env | grep TEST_ENV", trace="strace")
    assert "TEST_ENV=abdc" in result.stdout

def test_log_book_traceAndStats():
    if os.uname().sysname == "Linux":
        logger = Logger(stack()[0][3], Path.cwd())
        result = logger.log("Sleep",
                            "sleep 1",
                            return_info=True,
                            measure=["cpu", "memory", "disk"],
                            interval=0.1,
                            trace="ltrace",
                            expression="setlocale",
                            summary=True)
        assert "setlocale" in logger.log_book[0]["trace"]
        assert "sleep" not in logger.log_book[0]["trace"]
        assert len(logger.log_book[0]["stats"]["memory"]) > 8
        assert len(logger.log_book[0]["stats"]["memory"]) < 30
        assert len(logger.log_book[0]["stats"]["cpu"]) > 8
        assert len(logger.log_book[0]["stats"]["cpu"]) < 30
        assert len(logger.log_book[0]["stats"]["disk"]["/"]) > 8
        assert len(logger.log_book[0]["stats"]["disk"]["/"]) < 30
    else:
        print(f"Warning: uname is not 'Linux': {os.uname()}; ltrace not tested.")

def test_change_pwd():
    logger = Logger(stack()[0][3], Path.cwd())
    pwd_command = "pwd"
    directory1 = "/"
    directory2 = "/tmp"
    if os.name == "posix":
        pwd_command = "pwd"
        directory1 = "/"
        directory2 = "/tmp"
    elif os.name == "nt":
        pwd_command = "cd"
        directory1 = "C:\\"
        directory2 = "C:\\Users"
    else:
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger.run(f"cd {directory1}")
    result = logger.run(pwd_command)
    assert result.stdout.strip() == directory1
    assert result.pwd == directory1
    result = logger.run(f"cd {directory2}")
    result = logger.run(pwd_command)
    assert result.stdout.strip() == directory2
    assert result.pwd == directory2

def test_returncode():
    logger = Logger(stack()[0][3], Path.cwd())
    command = "false"
    expected_returncode = 1
    if os.name == "posix":
        command = "false"
        expected_returncode = 1
    elif os.name == "nt":
        command = "type nul | findstr NOPE"
        expected_returncode = 1
    else:
        print(f"Warning: os.name is unrecognized: {os.name}; test may fail.")
    result = logger.run(command)
    assert result.returncode == expected_returncode

def test_SGR_gets_converted_to_HTML(logger):
    logger = Logger(stack()[0][3], Path.cwd())
    logger.print("\x1B[31mHello\x1B[0m")
    logger.print("\x1B[31;43m\x1B[4mthere\x1B[0m")
    logger.print("\x1B[38;5;196m\x1B[48;5;232m\x1B[4mmr.\x1B[0m logger")
    logger.print("\x1B[38;2;96;140;240m\x1B[48;2;240;140;10mmrs.\x1B[0m logger")
    logger.finalize()

    # Load the HTML file.
    html_file = logger.strm_dir / f"{logger.name}.html"
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

def test_html_print(capsys):
    logger = Logger(stack()[0][3], Path.cwd())
    logger.html_print("The quick brown fox jumps over the lazy dog.",
                      msg_title="Brown Fox")
    logger.print("The quick orange zebra jumps over the lazy dog.")
    out, err = capsys.readouterr()
    logger.finalize()

    # Load the HTML file.
    html_file = logger.strm_dir / f"{logger.name}.html"
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

def test_append_mode():
    logger1 = Logger(stack()[0][3] + "_1", Path.cwd())
    logger1.log("Print HELLO to stdout", "echo HELLO")
    logger1.print("Printed once to stdout")
    logger1.html_print("Printed ONCE to STDOUT")
    logger1.finalize()

    logger2 = Logger.append(logger1.html_file)
    logger2.log("Print THERE to stdout", "echo THERE")
    logger2.print("Printed twice to stdout")
    logger2.html_print("Printed TWICE to STDOUT")
    logger2.finalize()

    logger3 = Logger.append(logger2.log_dir)
    logger3.log("Print LOGGER to stdout", "echo LOGGER")
    logger3.print("Printed thrice to stdout")
    logger3.html_print("Printed THRICE to STDOUT")
    logger3.finalize()

    logger4 = Logger.append(logger3.strm_dir)
    logger4.log("Print !!! to stdout", "echo '!!!'")
    logger4.print("Printed finally to stdout")
    logger4.html_print("Printed FINALLY to STDOUT")
    logger4.finalize()

    logger5 = Logger.append(logger4.strm_dir / f"{logger4.name}.json")
    logger5.log("Print 111 to stdout", "echo '111'")
    logger5.print("Printed for real to stdout")
    logger5.html_print("Printed FOR REAL to STDOUT")
    logger5.finalize()

    # Load the HTML file.
    html_file = logger1.strm_dir / f"{logger1.name}.html"
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

