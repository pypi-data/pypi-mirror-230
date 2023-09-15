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

        build_backend = self.step.stage.build_backend()
        opts = self.get_options_list()

        back_dir = os.getcwd()

        clear = self.step.read_setting_from_connected("build", "clear", direction=1)
        if clear:
            try:
                shutil.rmtree(bld_path)
            except FileNotFoundError:
                pass

        utils.make_dir(bld_path)
        os.chdir(bld_path)

        if build_backend == "ninja":
            has_makefile = os.path.isfile("build.ninja")
            ninja_opt = ["-GNinja"]
        else:
            has_makefile = os.path.isfile("Makefile")
            ninja_opt = []

        # If 'clear' is true there can't be any build files.
        assert not (clear and has_makefile)

        # Note: Independent of 'clear' and 'has_makefile' we continue.
        #       CMake is able to do that on the fly.
        cmd = ["cmake", "-DCMAKE_INSTALL_PREFIX=" + inst_path] + ninja_opt + opts + [src_path]
        ret = utils.run_process(cmd, self.step.log)

        os.chdir(back_dir)

        if ret != 0:
            raise WorkError(self.step.log)

    def get_options_list(self):
        cfg_opts = self.step.read_setting("options")
        if not cfg_opts:
            return []
        if not isinstance(cfg_opts, list):
            raise WorkError(msg="CMake options not defined as list.")
        else:
            for i in range(len(cfg_opts)):
                opt = cfg_opts[i]
                if not isinstance(opt, str):
                    raise WorkError(msg="CMake option not a string.")
                if not opt[:2] == "-D":
                    # add -D flag
                    cfg_opts[i] = "-D" + opt
        return cfg_opts
