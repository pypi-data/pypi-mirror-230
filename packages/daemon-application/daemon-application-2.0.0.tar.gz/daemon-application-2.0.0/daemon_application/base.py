#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import os
import errno
import time
import atexit
import signal
import logging
from io import open

import six
import psutil
from zenutils import sixutils

__all__ = [
    "get_sig",
    "make_basic_daemon",
    "process_kill",
    "load_pid",
    "write_pidfile",
    "get_process",
    "is_running",
    "clean_pid_file",
    "daemon_start",
    "daemon_stop",
    "get_child_processes",
    "process_kill_force",
]


_logger = logging.getLogger(__name__)


def get_sig(sig):
    if sig is None:
        return signal.SIGTERM
    if sixutils.PY2:
        if isinstance(sig, sixutils.STR_TYPE):
            sig = sig.encode()
        if isinstance(sig, sixutils.BYTES_TYPE):
            sig = getattr(signal, sig)
    if sixutils.PY3:
        if isinstance(sig, sixutils.BYTES_TYPE):
            sig = sig.decode()
        if isinstance(sig, sixutils.STR_TYPE):
            sig = getattr(signal, sig)
    return sig


def make_basic_daemon(workspace=None):
    """Make basic daemon."""
    workspace = workspace or os.getcwd()
    # first fork
    if os.fork():
        os._exit(0)
    # change env
    os.chdir(workspace)
    os.setsid()
    os.umask(0o22)
    # second fork
    if os.fork():
        os._exit(0)
    # reset stdin/stdout/stderr to /dev/null
    null = os.open("/dev/null", os.O_RDWR)
    try:
        for i in range(0, 3):
            try:
                os.dup2(null, i)
            except OSError as error:
                if error.errno != errno.EBADF:
                    raise
    finally:
        os.close(null)


def process_kill(pid, sig=None):
    """Send signal to process."""
    sig = get_sig(sig)
    os.kill(pid, sig)


def load_pid(pidfile):
    """read pid from pidfile."""
    pid = 0
    if pidfile and os.path.isfile(pidfile):
        with open(pidfile, "r", encoding="utf-8") as fobj:
            pid = int(fobj.readline().strip())
    if pid:
        if is_running(pid):
            return pid
    return 0


def write_pidfile(pidfile):
    """write current pid to pidfile."""
    pid = os.getpid()
    if pidfile:
        with open(pidfile, "w", encoding="utf-8") as fobj:
            fobj.write(sixutils.TEXT(str(pid)))
    return pid


def get_process(pid):
    """get process information from pid."""
    try:
        return psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None


def is_running(pid):
    """check if the process with given pid still running"""
    process = get_process(pid)
    if process and process.is_running() and process.status() != "zombie":
        return True
    else:
        return False


def clean_pid_file(pidfile):
    """clean pid file."""
    if pidfile and os.path.exists(pidfile):
        os.unlink(pidfile)


def daemon_start(main, pidfile, daemon=True, workspace=None):
    """Start application in background mode if required and available. If not then in front mode."""
    _logger.debug(
        "start daemon application pidfile={pidfile} daemon={daemon} workspace={workspace}.".format(
            pidfile=pidfile, daemon=daemon, workspace=workspace
        )
    )
    workspace = workspace or os.getcwd()
    os.chdir(workspace)
    daemon_flag = False
    if pidfile and daemon:
        old_pid = load_pid(pidfile)
        if old_pid:
            _logger.debug(
                "pidfile {pidfile} already exists, pid={pid}.".format(
                    pidfile=pidfile, pid=old_pid
                )
            )
        # if old service is running, just exit.
        if old_pid and is_running(old_pid):
            error_message = "Service is running in process: {pid}.".format(pid=old_pid)
            _logger.error(error_message)
            six.print_(error_message, file=os.sys.stderr)
            os.sys.exit(95)
        # clean old pid file.
        clean_pid_file(pidfile)
        # start as background mode if required and available.
        if daemon and os.name == "posix":
            make_basic_daemon()
            daemon_flag = True
    new_pid = os.getpid()  # must get the new pid after make_basic_daemon
    if daemon_flag:
        _logger.info(
            "Start application in DAEMON mode, pidfile={pidfile} pid={pid}".format(
                pidfile=pidfile, pid=new_pid
            )
        )
    else:
        _logger.info("Start application in FRONT mode, pid={pid}.".format(pid=new_pid))
    write_pidfile(pidfile)
    atexit.register(clean_pid_file, pidfile)
    main()
    return


def get_child_processes(pid):
    proc = get_process(pid)
    if not proc:
        return proc, []
    return proc, proc.children(recursive=True)


def process_kill_force(pid):
    proc, subprocs = get_child_processes(pid)
    for sub in subprocs:
        try:
            sub.terminate()
        except Exception:
            pass
        try:
            sub.kill()
        except Exception:
            pass
    try:
        proc.terminate()
    except Exception:
        pass
    try:
        proc.kill()
    except Exception:
        pass
    return proc, subprocs


def daemon_stop(pidfile, sig=None, stop_timeout=30, check_interval=0.1):
    """Stop application."""
    _logger.debug("stop daemon application pidfile={pidfile}.".format(pidfile=pidfile))
    pid = load_pid(pidfile)
    _logger.debug("load pid={pid}".format(pid=pid))
    if not pid:
        six.print_("Application is not running or crashed...", file=os.sys.stderr)
        return 0
    process_kill(pid, sig)
    stime = time.time()
    while True:
        if not is_running(pid):
            return pid
        if time.time() - stime > stop_timeout:  # wait timeout, do force kill
            break
        time.sleep(check_interval)
    process_kill_force(pid)
    if is_running(pid):
        six.print_("Application is still running...", file=os.sys.stderr)
    return pid
