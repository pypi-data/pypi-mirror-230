# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fdbuild import stage


class Plugin(stage.Stage):
    def __init__(self, step):
        super().__init__("install", step)
        self.directory = self.identifier

        self.step.add_caller("build")

    def host_suffix(self):
        """Returns host-suffix setting which specifies if the installation should go into a
        separate folder naming the host target."""
        return self.step.read_setting("host-suffix")

    def sudo(self):
        """Returns if the installation should be executed as root."""
        return self.step.read_setting("sudo")
