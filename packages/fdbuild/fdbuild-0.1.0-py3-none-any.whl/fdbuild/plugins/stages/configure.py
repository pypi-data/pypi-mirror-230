# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from fdbuild import stage


class Plugin(stage.Stage):
    def __init__(self, step):
        super().__init__("configure", step)
        self.directory = self.identifier

        self.step.add_caller("source")
        self.step.add_dependent("build")

    @staticmethod
    def default_host():
        return {
            "host": "default",
            "bits": "default",
            "suffix": "",
            "file": "",
            "pkg-config": {"path": "", "prepend": True},
        }

    def read_hosts(self):
        hosts = self.step.read_setting("host")

        fallback_host = self.default_host()
        hosts_list = []
        if hosts:
            for hostkey, host in hosts.items():
                if isinstance(host, dict):
                    for bitkey, bit in host.items():
                        if isinstance(bit, dict):
                            if not bit["build"]:
                                continue
                            new_host = dict(fallback_host)
                            new_host["host"] = hostkey
                            new_host["bits"] = bitkey
                            new_host["suffix"] = hostkey + "_" + str(bitkey)

                            if "file" in bit:
                                new_host["file"] = bit["file"]

                            if "pkg-config" in bit:
                                new_host["pkg-config"] = dict(bit["pkg-config"])

                            hosts_list.append(new_host)
        if not hosts_list:
            return [fallback_host]

        return hosts_list

    def source_path(self):
        subpath = self.step.read_setting_from_connected("source", "path", "source", direction=-1)
        cfg_path = self.step.read_setting("path")
        if cfg_path:
            subpath = os.path.join(subpath, cfg_path)
        return self.step.unit.absolute_path(subpath)

    def build_path(self):
        subpath = self.step.read_setting_from_connected("build", "path", "build", direction=1)
        return self.step.unit.absolute_path(subpath)

    def install_path(self):
        subpath = self.step.read_setting_from_connected("install", "path", direction=1)
        path = self.step.unit.absolute_path(subpath)
        if not path:
            return "/usr"
        return path

    def build_backend(self):
        build_step = self.step.get_connected_step("build", 1)
        if not build_step:
            return ""
        build_backend = build_step.read_setting("plugin")
        if not build_backend:
            return ""
        return build_backend
