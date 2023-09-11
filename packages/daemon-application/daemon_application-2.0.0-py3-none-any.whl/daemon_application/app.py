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
from zenutils.sixutils import *

__all__ = [
    "DaemonApplication",
]

import os
import sys
import time
import signal
from pprint import pprint

import click
import yaml
from zenutils import dictutils
from zenutils import logutils

from .base import daemon_start
from .base import daemon_stop


class DaemonApplication(object):
    config_name = "config"
    config_suffix = "yml"
    default_appname = None

    # default_config = {}

    def main(self):
        """应用真实主函数。"""
        raise NotImplementedError()

    def get_default_config_filepaths(self, appname, name=None, suffix=None):
        """应用默认配置文件的搜索路径。"""
        name = name or self.config_name
        suffix = suffix or self.config_suffix
        filepaths = []
        filenames = (
            "./{0}-{1}.{2}".format(appname, name, suffix),
            "./conf/{0}-{1}.{2}".format(appname, name, suffix),
            "./etc/{0}-{1}.{2}".format(appname, name, suffix),
            "~/.{0}/{1}.{2}".format(appname, name, suffix),
            "~/{0}/{1}.{2}".format(appname, name, suffix),
            "./{0}.{1}".format(name, suffix),
            "./conf/{0}.{1}".format(name, suffix),
            "./etc/{0}.{1}".format(name, suffix),
            "~/{0}.{1}".format(name, suffix),
            "~/.{0}.{1}".format(name, suffix),
            "{0}.{1}".format(name, suffix),
        )
        for filename in filenames:
            filepath = os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))
            if not filepath in filepaths:
                filepaths.append(filepath)
        return filepaths

    def get_appname(self):
        """应用名称。"""
        appname = getattr(self, "default_appname", None)
        if appname is None:
            appname = os.path.splitext(os.path.basename(os.sys.argv[0]))[0]
        return appname

    def get_config_file_path(self, config_file_path, appname):
        """获取应用实际的配置文件路径。"""
        the_config_file_path = None
        for config_file_path in [config_file_path] + self.get_default_config_filepaths(
            appname
        ):
            if config_file_path and os.path.exists(config_file_path):
                the_config_file_path = config_file_path
                break
        return the_config_file_path

    def get_default_config(self):
        """应用默认配置项。"""
        config = {
            "pidfile": "app.pid",
            "stop-timeout": 30,
            "stop-signal": signal.SIGINT,
            "daemon": True,
            "workspace": os.getcwd(),
            "loglevel": "INFO",
            "logfile": "app.log",
            "logfmt": "default",
        }
        config.update(getattr(self, "default_config", {}))
        return config

    def load_config_from_config_file(self, config_file):
        """加载应用配置文件。"""
        if not config_file:
            return {}
        if not os.path.exists(config_file):
            return {}
        with open(config_file, "rb") as fobj:
            return yaml.safe_load(fobj)

    def update_config_item(self, config, item_name, item_value):
        """更新应用配置项内容。"""
        if not item_value is None:
            config[item_name] = item_value
        return config

    def fix_config_items(self, config):
        """完善必要的应用配置。"""
        if config.get("pidfile", None) is None:
            config["pidfile"] = self.appname + ".pid"

    def load_config(self, config, **kwargs):
        """加载应用配置。"""
        self.config = dictutils.Object({})
        self.appname = self.get_appname()
        self.config_file_path = self.get_config_file_path(config, self.appname)
        if self.config_file_path:
            print(
                "Start application with config file: {}".format(self.config_file_path),
                file=sys.stderr,
            )
        else:
            print("Start application without config file.", file=sys.stderr)
        dictutils.deep_merge(self.config, self.get_default_config())
        dictutils.deep_merge(
            self.config, self.load_config_from_config_file(self.config_file_path)
        )
        for key, value in kwargs.items():
            self.update_config_item(self.config, key.replace("_", "-"), value)
        self.config["config-file-path"] = self.config_file_path
        self.fix_config_items(self.config)

    def get_main_options(self):
        """应用命令行选项。"""
        option_pidfile = click.option("--pidfile", help="pidfile file path.")
        option_daemon = click.option(
            "--daemon/--no-daemon",
            is_flag=True,
            default=None,
            help="Run application in background or in foreground.",
        )
        option_workspace = click.option("--workspace", help="Set running folder")
        option_config = click.option(
            "-c",
            "--config",
            help="Config file path. Application will search config file if this option is missing. Use sub-command show-config-fileapaths to get the searching tactics.",
        )
        option_loglevel = click.option("--loglevel")
        option_logfile = click.option("--logfile")
        option_logfmt = click.option("--logfmt")
        return [
            option_config,
            option_daemon,
            option_workspace,
            option_pidfile,
            option_loglevel,
            option_logfile,
            option_logfmt,
        ]

    def get_controller(self):
        """创建应用click控制器。"""
        main_options = self.get_main_options()

        def _main(config, **kwargs):
            self.load_config(config, **kwargs)
            logutils.setup(**self.config)

        main = _main
        for option in main_options:
            main = option(main)
        main = click.group()(main)

        @main.command()
        def start():
            """Start daemon application."""
            pidfile = self.config["pidfile"]
            daemon = self.config["daemon"]
            workspace = self.config["workspace"]
            daemon_start(self.main, pidfile=pidfile, daemon=daemon, workspace=workspace)

        @main.command()
        def stop():
            """Stop daemon application."""
            pidfile = self.config["pidfile"]
            stop_signal = self.config["stop-signal"]
            stop_timeout = self.config["stop-timeout"]
            daemon_stop(pidfile, sig=stop_signal, stop_timeout=stop_timeout)

        @main.command()
        @click.option(
            "--sleep-seconds",
            type=int,
            default=0,
            help="Wait some seconds after old application stopped and before new application started.",
        )
        def restart(sleep_seconds):
            """Restart Daemon application."""
            pidfile = self.config["pidfile"]
            stop_signal = self.config["stop-signal"]
            stop_timeout = self.config["stop-timeout"]
            daemon_stop(pidfile, sig=stop_signal, stop_timeout=stop_timeout)
            if sleep_seconds:
                time.sleep(sleep_seconds)
            daemon = self.config["daemon"]
            workspace = self.config["workspace"]
            daemon_start(self.main, pidfile=pidfile, daemon=daemon, workspace=workspace)

        @main.command(name="show-config-filepaths")
        def show_config_filepaths():
            """Print out the config searching paths."""
            config_filepaths = self.get_default_config_filepaths(self.appname)
            print(
                "Application will search config file from following paths. It will load the first exists file as the config file."
            )
            for filepath in config_filepaths:
                print("    ", filepath)

        @main.command(name="show-configs")
        def show_configs():
            """Print out the final config items."""
            pprint(self.config)

        return main
