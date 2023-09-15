# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, subprocess, time

from fdbuild import utils
from fdbuild.exceptions import WorkError


class Plugin:
    def __init__(self, step):
        self.step = step

        subpath = self.step.read_setting("path", default=self.step.stage.directory)
        self.src_path = self.step.unit.absolute_path(subpath)

        self.user = self.step.read_setting("user")
        self.password = self.step.read_setting("password")
        self.branch = self.step.read_setting("branch")

        # Every unit must have its own code base (or none), so don't
        # read other setting files for the code base origin value.
        self.origin = self.step.read_setting("origin", hierarchy_lookup=False)

    def has_git_repo(self):
        return os.path.isdir(os.path.join(self.src_path, ".git"))

    def get_address_with_login(self, remote_address):
        if not self.user:
            return remote_address

        protocol = "https://"
        login_address = protocol + self.user
        if self.password:
            login_address += ":" + self.password
        login_address += "@"
        if remote_address.startswith(protocol):
            remote_address = remote_address[len(protocol) :]
        return login_address + remote_address

    def git_clone(self, log):
        if self.has_git_repo():
            # already has repo
            return 0

        if not self.origin:
            # project has no git repo specified in
            # settings file (might have still a repo)
            return 0

        cmd = ["git", "clone", "--progress"]

        if self.branch:
            cmd.append("--branch=" + str(self.branch))

        depth = self.step.read_setting("depth")
        if depth:
            cmd.append("--depth=" + str(depth))

        cmd += [self.get_address_with_login(self.origin), self.src_path]

        tries = 0
        while 1:
            tries = tries + 1
            if utils.run_process(cmd, log, indepedent_indicator=False) == 0:
                break
            elif tries == 5:
                log.print("Cloning the repo failed 5 times.")
                raise WorkError(log)
            log.print("Cloning the repo failed (%s / 5). Trying again in 5 seconds.\n" % tries)
            time.sleep(5)

        return 1

    def current_branch_name(self, log):
        cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]

        name = ""

        def writeOutLine(line):
            nonlocal name
            name = line

        def writeErrLine(line):
            log.err(line)

        if utils.run_logged_process(cmd, writeOutLine, writeErrLine) != 0:
            raise WorkError(log)
        return name.strip("\n")

    def current_tracking_remote(self, log):
        cmd = ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]

        name = ""

        def writeOutLine(line):
            nonlocal name
            name = line

        def writeErrLine(line):
            log.err(line)

        if utils.run_logged_process(cmd, writeOutLine, writeErrLine) != 0:
            return

        if not name:
            return name

        return name.split("/")[0]

    def pull(self, log):
        if self.has_git_repo():
            back_dir = os.getcwd()
            os.chdir(self.src_path)

            remote = self.current_tracking_remote(log)
            if not remote:
                return

            def address_of_remote(remote):
                cmd = ["git", "remote", "get-url", remote]
                p1 = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                assert p1.returncode == 0
                return utils.decode_text(p1.stdout).strip("\n")

            remote_address = address_of_remote(remote)

            if self.origin and remote_address != self.get_address_with_login(self.origin):
                log.warning(
                    "Specified remote address in settings differs to '%s' that the current branch tracks. Omitting source update."
                    % remote
                )
                return 1

            current_branch = self.current_branch_name(log)
            if self.branch and self.branch != current_branch:
                log.warning(
                    "Specified branch in settings and current branch are different. Omitting source update."
                )
                return 1

            def writeOutLine(line):
                log.out(line)

            def writeErrLine(line):
                log.err(line)

            cmd = ["git", "pull"]
            ret = utils.run_process(cmd, log, indepedent_indicator=True)

            # Always go back in directory.
            os.chdir(back_dir)

            if ret != 0:
                raise WorkError(log)

    def work(self):
        log = self.step.log
        utils.make_dir(self.src_path)

        clone_ret = self.git_clone(log)
        if clone_ret == 1:
            # just cloned, no pull needed
            return

        return self.pull(log)
