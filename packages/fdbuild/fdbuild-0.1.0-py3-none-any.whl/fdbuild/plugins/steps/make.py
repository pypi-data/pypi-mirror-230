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
            line.strip()
            if line[0] != "[":
                return None
            line = line[1:]
            part = line.split("%")[0]
            part.strip()
            return int(part)
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

            cmd = ["make"]
            if threads:
                cmd += ["-j" + str(threads)]

            if utils.run_process(cmd, self.step.log, self.get_progress_percentage) != 0:
                raise WorkError(self.step.log)

        os.chdir(back_dir)

    def work_dependent(self, dependent):
        back_dir = os.getcwd()

        threads = self.step.stage.read_threads()
        self.query_hosts()

        for host in self.hosts:
            bld_path = os.path.join(self.build_path, host["suffix"])
            os.chdir(bld_path)

            cmd = (
                ["sudo"]
                if self.step.read_setting_from_connected("install", "sudo", direction=1)
                else []
            )
            cmd += ["make", "install"]

            if threads:
                cmd += ["-j" + str(threads)]

            if utils.run_process(cmd, dependent.log, self.get_progress_percentage) != 0:
                raise WorkError(dependent.log)

        os.chdir(back_dir)
