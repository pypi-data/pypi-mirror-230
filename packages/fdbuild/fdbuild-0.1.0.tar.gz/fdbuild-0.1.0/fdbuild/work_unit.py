# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from . import (
    chainer,
    log as logger,
    utils,
)
from .exceptions import *
from .step import *


def unit_finder(tasker, path):
    """Find a unit object, currently only supports relative paths and projects"""
    if not path:
        return None

    path = path.split("/")
    cur = tasker

    while len(path):
        name = path.pop(0)
        if name == "..":
            nex = cur.leader
            if nex is None:
                return None
            cur = nex
        elif name != ".":
            nex = None
            for p in cur.projects:
                if p.ident.split("/").pop() == name:
                    nex = p
                    break
            if nex is None:
                return None
            cur = nex

    assert cur != tasker

    return cur


class Hooks:
    def __init__(self, stage, settings, step_log):
        self.stage = stage
        self.settings = settings
        self.step_log = step_log

    def run_cmd(self, cmd, log, post):
        ret = utils.run_process([cmd], log, shell=True)
        if ret != 0:
            log.failed()
            raise HookError(post, log)

    def pre(self):
        cmd = self.settings.read_hook(self.stage, True)
        if not cmd:
            return
        log = logger.HookLog(self.step_log, False)
        self.run_cmd(cmd, log, False)
        log.success()

    def post(self):
        cmd = self.settings.read_hook(self.stage, False)
        if not cmd:
            return
        log = logger.HookLog(self.step_log, True)
        self.run_cmd(cmd, log, True)
        log.success()


class WorkUnit:
    def __init__(self, ident, leader):
        self.ident = ident
        self.leader = leader

        self.settgs = None

        self.steps = []
        self.worked = False

        self.structure_plugin = None

    def init_steps(self):
        # Init phase 1: Get steps.
        if self.leader:
            leader = self.leader
        else:
            leader = self.get_steps_leader()

        if leader:
            for val in leader.steps:
                self.steps.append(Step(val.identifier, self))

        assert isinstance(self.settgs.data, dict)
        reserved_keys_used = ["projects", "structure", "depends", "template"]
        reserved_keys_unused = ["steps", "fdbuild"]

        for key, val in self.settgs.data.items():
            if key in reserved_keys_unused:
                raise InitError(None, "Key '%s' is reserved.", self.identifier)
            if key in reserved_keys_used:
                continue

            step = Step(key, self)
            found = False

            for i, step_i in enumerate(self.steps):
                if step_i.identifier == key:
                    self.steps[i] = step
                    found = True
                    break

            if not found:
                self.steps.append(step)

        # Init phase 2: Init settings and plugins.
        for step in self.steps:
            step.init()

        # Init phase 3: Order steps.
        step_chainer = chainer.Resolution()
        for step in self.steps:
            node = step_chainer.add_node(step)
            for depend in step.dependents:
                node.add_dependent(depend)

        reordered_chain = step_chainer.create_chain()
        reordered_steps = []
        for node in reordered_chain:
            reordered_steps.append(node.data)

        self.steps = reordered_steps

    def get_step(self, identifier):
        for step in self.steps:
            if step.identifier == identifier:
                return step

        # Step does not exist yet. Must be a caller/dependent without actual implementation.
        step = Step(identifier, self)
        self.steps.append(step)
        return step

    def resume(self, args):
        if not args.resume_from:
            # In this case all units are eligible to be run.
            return True

        is_ancestor = (
            args.resume_from.startswith(self.ident)
            and len(args.resume_from) > len(self.ident)
            and args.resume_from[len(self.ident)] in "/:"
        )

        if (
            self.ident == args.resume_from
            or self.ident.split("/")[-1] == args.resume_from
            or self.ident.split(":")[-1] == args.resume_from
        ):
            # We found the project.
            args.resume_from = None
            return True

    def valid(self, args):
        """Checks if the unit is supposed to be worked on."""
        if not self.resume(args):
            return False

        return True

    def get_direct_dependencies(self):
        return self.settgs.read_list(["depends"])

    def work_depends(self, depends, args):
        if not depends:
            return

        for d in depends:
            u = unit_finder(self, d)
            if u is None:
                # ignore dependencies that are not
                # to be built this invocation
                continue
            u.work(args)

    def set_envvars(self):
        dic = self.settgs.read_envvars()
        if dic:
            utils.set_env_vars(dic)

    def work(self, args):
        utils.hide_cursor()
        for step in self.steps:
            step.work()
