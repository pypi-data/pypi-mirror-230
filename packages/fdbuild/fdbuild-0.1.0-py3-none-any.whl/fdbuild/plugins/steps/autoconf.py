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
        bld_path_base = self.step.stage.build_path()
        inst_path_base = self.step.stage.install_path()

        install_step = self.step.get_connected_step("install", 1)
        inst_host_suffixed = install_step.stage.host_suffix()

        opts = self.step.unit.settgs.read_configure_options()
        hosts = self.step.stage.read_hosts()

        log = self.step.log

        bootstrap = None

        back_dir = os.getcwd()

        for host in hosts:
            if inst_host_suffixed:
                inst_path = os.path.join(inst_path_base, host["suffix"])
            else:
                inst_path = inst_path_base

            bld_path = os.path.join(bld_path_base, host["suffix"])
            utils.make_dir(bld_path)
            os.chdir(bld_path)

            has_makefile = os.path.isfile("Makefile")
            clear = self.step.read_setting_from_connected("build", "clear", direction=1)

            if has_makefile and not clear:
                continue

            if clear:
                os.chdir(back_dir)
                try:
                    shutil.rmtree(bld_path)
                except FileNotFoundError:
                    pass
                utils.make_dir(bld_path)
                os.chdir(bld_path)
            elif has_makefile:
                build_step = self.step.get_connected_step("build", 1)
                threads = build_step.stage.read_threads()
                if utils.run_process(["make clean", "-j" + str(threads)], log) != 0:
                    log.print("Can not run make clean.")

            if bootstrap is None:
                bootstrap = self.get_bootstrap(src_path)

                if bootstrap is None:
                    os.chdir(back_dir)
                    raise WorkError(
                        log, "Could not locate bootstrap file for autotools at '%s'" % src_path
                    )

            host_option = self.get_host_option(host)
            build_option = self.get_build_option(host)
            cfgcall = [bootstrap, "--prefix=" + inst_path] + host_option + build_option + opts

            old_pkgcfg_path = utils.read_and_set_pkgcfg_path(host)

            ret = utils.run_process(cfgcall, log, shell=True)

            utils.reset_pkgcfg_path(old_pkgcfg_path)

            if ret != 0:
                raise WorkError(log)

        os.chdir(back_dir)

    def get_bootstrap(self, source_path):
        bootstrap = os.path.join(source_path, "autogen.sh")

        if os.path.exists(bootstrap):
            return bootstrap

        bootstrap = os.path.join(source_path, "bootstrap")
        if os.path.exists(bootstrap):
            return bootstrap

        bootstrap = os.path.join(source_path, "configure")
        if os.path.exists(bootstrap):
            return bootstrap

        return None

    def get_host_option(self, host):
        if host["host"] == "default":
            return []

        # TODO: Sometimes/always(?) PKG_CONFIG_PATH needs to be set.
        if host["host"] == "x86":
            bits = host["bits"]
            if bits == 64:
                return ["--host=x86_64-linux-gnu", "CFLAGS=-m64", "CXXFLAGS=-m64", "LDFLAGS=-m64"]
            if bits == 32:
                return ["--host=i686-linux-gnu", "CFLAGS=-m32", "CXXFLAGS=-m32", "LDFLAGS=-m32"]

        return []

    def get_build_option(self, host):
        if host["host"] == "default":
            return []

        if host["host"] == "x86":
            bits = host["bits"]
            if bits == 64:
                return ["--build=x86_64-pc-linux-gnu"]
            if bits == 32:
                return ["--build=i686-linux-gnu"]
        return []
