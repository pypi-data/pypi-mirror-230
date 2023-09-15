# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import multiprocessing

from fdbuild import stage
from fdbuild.plugins.stages import configure


class Plugin(stage.Stage):
    def __init__(self, step):
        super().__init__("build", step)
        self.directory = self.identifier

        self.step.add_caller("configure")
        self.step.add_dependent("install")

    def default_host(self):
        return configure.Plugin.default_host()

    def read_threads(self):
        """Returns integer number of threads if found in settings for building or if not defined None.
        Threads can be defined in settings as whole numbers or as percentage. Additionally settings
        can specify 'max' or 'unlimited' to always select the maximum number of cores."""
        threads = self.step.read_setting("threads")
        if not threads:
            return

        if isinstance(threads, int):
            return threads

        if not isinstance(threads, str):
            return

        threads.strip()
        cpu_count = multiprocessing.cpu_count()
        if threads.lower() in ["max", "unlimited"]:
            return cpu_count

        if threads[-1] == "%":
            number = threads[:-1]
            if number.isnumeric():
                number = int(number)
                if number > 0 and number / 100 < 1:
                    return max(int(cpu_count * number / 100), 1)

    def build_path(self):
        subpath = self.step.read_setting("path", default="build")
        return self.step.unit.absolute_path(subpath)
