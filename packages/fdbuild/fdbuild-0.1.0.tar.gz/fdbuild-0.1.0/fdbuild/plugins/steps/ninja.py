# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from fdbuild import utils
from fdbuild.exceptions import WorkError


class Plugin:
    def __init__(self, step):
        self.step = step

        self.build_path = self.step.stage.build_path()

        self.hosts_queried = False
        self.hosts = []

    def query_hosts(self):
        if self.hosts_queried:
            return self.hosts
        self.hosts_queried = True

        configure_step = self.step.get_connected_step("configure", -1)
        if configure_step:
            self.hosts = configure_step.stage.read_hosts()
        else:
            self.hosts = [self.step.stage.default_host()]

    def get_progress_percentage(self, line):
        try:
            if line[0] != "[":
                return None
            line = line[1:]
            parts = line.split("]")
            parts = parts[0].split("/")
            dividend = int(parts[0])
            divisor = int(parts[1])
            return int(dividend / divisor * 100)
        except:
            return None

    def work(self):
        threads = self.step.stage.read_threads()
        back_dir = os.getcwd()

        self.query_hosts()

        for host in self.hosts:
            bld_path = os.path.join(self.build_path, host["suffix"])

            utils.make_dir(bld_path)
            os.chdir(bld_path)

            cmd = ["ninja"]
            if threads:
                cmd += ["-j " + str(threads)]

            def writeOutLine(line):
                percentage = self.get_progress_percentage(line)
                if percentage is not None:
                    self.step.log.progress(percentage)
                self.step.log.out(line)

            def writeErrLine(line):
                self.step.log.err(line)

            if utils.run_logged_process(cmd, writeOutLine, writeErrLine) != 0:
                raise WorkError(self.step.log)

        os.chdir(back_dir)

    def work_dependent(self, dependent):
        back_dir = os.getcwd()

        self.query_hosts()

        for host in self.hosts:
            bld_path = os.path.join(self.build_path, host["suffix"])
            os.chdir(bld_path)

            cmd = (
                ["sudo"]
                if self.step.read_setting_from_connected("install", "sudo", direction=1)
                else []
            )
            cmd += ["ninja", "install"]

            if utils.run_process(cmd, dependent.log) != 0:
                raise WorkError(dependent.log)

        os.chdir(back_dir)
