# SPDX-FileCopyrightText: 2019 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, sys, time

from . import (
    config as cfg,
    utils,
)
from .utils import tcolors


class Log:
    def __init__(self, path, header):
        self.path = path
        self.header = header
        self.new_line = True
        self.write_started = False

        self.stdout = ""
        self.stderr = ""

        self.animate_state = 0
        self.animate_time = -1

        try:
            os.remove(self.path)
        except:
            pass

    def __del__(self):
        self.add_new_line()

    def write_file(self, text):
        utils.make_dir(os.path.dirname(self.path))
        with open(self.path + ".log", "a") as f:
            self.write_started = True
            f.write(text)

    def out(self, output):
        """Logs diagnostic output, normally stdout. We remember this and directly
        put it in the file so there is something in case of unhandled exception.
        Exception is when we run verbose. Then we output it directly to the console."""
        text = utils.decode_text(output)
        self.stdout += text
        self.write_file(text)
        if cfg.args.verbose:
            sys.stdout.write(text)

    def err(self, error):
        """Logs error messages, normally stderr. We only remember this and put
        it later at the end of the file so it is separated from diagnostic output.
        On the other side when we run verbose we output it directly to the console."""
        text = utils.decode_text(error)
        self.stderr += text
        if cfg.args.verbose:
            sys.stdout.write(text)

    def final_write(self):
        if self.stderr:
            self.write_file("\n\n### Error output ###\n\n" + self.stderr)
        self.add_new_line()

    def add_new_line(self):
        if not self.new_line:
            sys.stdout.write("")
        self.new_line = True

    def get_head(self):
        return "  " + self.header + ": "

    def head(self):
        self.new_line = False
        if cfg.args.verbose:
            sys.stdout.write(tcolors.OKBLUE + tcolors.BOLD)
        sys.stdout.write(self.get_head())
        if cfg.args.verbose:
            sys.stdout.write(tcolors.ENDC + "\n\n")
        else:
            utils.hide_cursor()
            sys.stdout.flush()

    def has_log(self):
        return self.stdout != "" or self.stderr != ""

    def animate(self):
        if cfg.args.verbose:
            return

        new_time = time.monotonic()
        if new_time - self.animate_time < 0.12:
            # Do not spin the animation too fast.
            return

        self.animate_time = new_time

        if self.animate_state == 4:
            self.animate_state = 0
        self.animate_state = self.animate_state + 1

        def get_sign(index):
            if index < 2:
                return "-"
            if index < 3:
                return "\\"
            if index < 4:
                return "|"
            return "/"

        sys.stdout.write("\r" + self.get_head() + get_sign(self.animate_state))

    def progress(self, n):
        if cfg.args.verbose:
            return
        sys.stdout.write("\r" + self.get_head() + str(n) + "%")
        sys.stdout.flush()

    def write_result(self, color, status):
        if cfg.args.verbose and self.has_log():
            sys.stdout.write("\n")

        sys.stdout.write("\r" + self.get_head() + color + status + tcolors.ENDC + "\n")
        if cfg.args.verbose:
            sys.stdout.write("\n")
        sys.stdout.flush()
        self.final_write()

    def success(self):
        self.write_result(tcolors.OKGREEN, "OK  ")

    def skipped(self):
        self.write_result(tcolors.WARNING, "SKIPPED")

    def failed(self):
        self.write_result(tcolors.FAIL, "FAILED")

    def print(self, line):
        """Logs simple text line. We remember this and directly
        put it in the file so there is something in case of unhandled exception.
        Exception is when we run verbose. Then we output it directly to the console."""
        line += "\n"
        self.stdout += line
        self.write_file(line)
        if cfg.args.verbose:
            sys.stdout.write(line)

    def warning(self, output):
        if not output:
            return
        ln = "\n"
        internal_heading = "### FDBuild warning:" + ln
        if self.write_started:
            internal_heading = ln + internal_heading
        self.write_file(internal_heading + output + ln + ln)


class StructureLog(Log):
    def __init__(self, path):
        super().__init__(os.path.join(path, "structure.log"), "Structurize")


class StepLog(Log):
    def __init__(self, path, stage):
        super().__init__(os.path.join(path, stage), stage.capitalize())


class HookLog(Log):
    def __init__(self, step_log, post):
        self.step_log = step_log
        if post:
            header = "└─ Post Hook"
            file_suffix = "-post"
        else:
            header = "┌─ Pre Hook"
            file_suffix = "-pre"
        super().__init__(self.step_log.path + file_suffix, header)
