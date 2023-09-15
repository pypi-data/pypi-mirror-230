# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, shutil

from fdbuild import utils
from fdbuild.exceptions import WorkError


class Plugin:
    def __init__(self, step):
        self.step = step

    def work(self):
        src_path = self.step.stage.source_path()
        bld_path = self.step.stage.build_path()
        inst_path = self.step.stage.install_path()

        install_step = self.step.get_connected_step("install", 1)
        inst_host_suffixed = install_step.stage.host_suffix()

        opts = self.get_options_list()
        hosts = self.step.stage.read_hosts()

        clear = self.step.read_setting_from_connected("build", "clear", direction=1)
        if clear:
            try:
                shutil.rmtree(bld_path)
            except FileNotFoundError:
                pass

        for host in hosts:
            if inst_host_suffixed:
                host_inst_path = os.path.join(inst_path, host["suffix"])
            else:
                host_inst_path = inst_path

            bld_path_suffixed = os.path.join(bld_path, host["suffix"])

            cross_file = []
            if host["file"]:
                cross_file = ["--cross-file=" + host["file"]]

            cmd = (
                ["meson", "--prefix=" + host_inst_path]
                + cross_file
                + opts
                + [src_path, bld_path_suffixed]
            )

            old_pkgcfg_path = utils.read_and_set_pkgcfg_path(host)

            ret = utils.run_process(cmd, self.step.log)

            utils.reset_pkgcfg_path(old_pkgcfg_path)

            if ret != 0:
                raise WorkError(self.step.log)

    def get_options_list(self):
        cfg_opts = self.step.unit.settgs.read_configure_options()

        if not cfg_opts:
            cfg_opts = []
        else:
            for i in range(len(cfg_opts)):
                opt = cfg_opts[i]
                if not opt[:2] == "-D":
                    # add -D flag
                    cfg_opts[i] = "-D" + opt
        return cfg_opts
