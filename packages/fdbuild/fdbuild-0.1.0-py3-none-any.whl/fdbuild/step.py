# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from . import (
    config as cfg,
    log as logger,
    pluginfactory as pluginfac,
    stage,
    work_unit,
)
from .exceptions import *


class Step:
    def __init__(self, ident, unit):
        self.identifier = ident
        self.unit = unit

        # Calling step and to be called steps.
        self.callers = []
        self.dependents = []

        self.stage = None
        self.plugin = None

        self.log = logger.StepLog(self.unit.log_path, self.identifier)
        self.args = []

    def read_settings(self):
        self.settings = self.unit.settgs.read_merged([self.identifier], non_dict_key="enabled")

        # TODO: handle actual InitErrors differently to when a plugin just not exists.
        try:
            name = self.get_stage_name()
            self.stage = pluginfac.get_stage(name, self)
        except InitError:
            self.stage = stage.Stage(self.identifier, self)

    def init(self):
        self.read_settings()
        self.get_plugin()

    def get_plugin(self):
        if not self.settings or not "plugin" in self.settings:
            return
        val = self.settings["plugin"]

        if not isinstance(val, str):
            raise InitError(
                None, "Plugin identifier is not string for work step '%s'" % self.identifier
            )
        self.plugin = pluginfac.get_step(self.identifier, val, self)

    # TODO: This changes self.settings. Should be clear that it is supposed to be only called internally on init.
    def get_stage_name(self):
        """Get the stage name for this step. The stage name can be either implicitly defined by the
        yaml key, i.e. identifier of this step or explicitly at the stage key in the yaml settings
        of this step."""

        def confirm_name(name):
            if not isinstance(name, str):
                raise InitError(
                    None, "Stage can not be identified for work step '%s'", self.identifier
                )
            return name

        if self.settings is None:
            return confirm_name(self.identifier)

        if not isinstance(self.settings, dict):
            if isinstance(self.settings, (bool, str)):
                return self.confirm_name(self.identifier)
            # Only a boolean or string value is allowed for stage.
            raise InitError(
                None,
                "Settings for '%s' are neither a dictionary nor plain boolean or string.",
                self.identifier,
            )

        if "stage" in self.settings:
            stage = self.settings.pop("stage")
            return confirm_name(stage)

        return confirm_name(self.identifier)

    def check(self):
        if not self.plugin and not self.callers:
            raise InitError(None, "Step '%s' needs a plugin set." % self.identifier)

    def add_caller(self, identifier):
        caller_step = self.unit.get_step(identifier)
        if not caller_step:
            return

        if self not in caller_step.dependents:
            caller_step.dependents.append(self)
        self.callers.append(caller_step)

    def add_dependent(self, identifier):
        dependent_step = self.unit.get_step(identifier)
        if not dependent_step:
            return

        if self not in dependent_step.callers:
            dependent_step.callers.append(self)
        self.dependents.append(dependent_step)

    def get_connected_step_up(self, identifier):
        if self.identifier == identifier:
            return self
        assert self.callers
        for caller in self.callers:
            step = caller.get_connected_step_up(identifier)
            if step:
                return step

    def get_connected_step_down(self, identifier):
        if self.identifier == identifier:
            return self
        for step in self.dependents:
            final_step = step.get_connected_step_down(identifier)
            if final_step:
                return final_step

    def get_connected_step(self, identifier, direction=0):
        if self.identifier == identifier:
            return self

        assert direction != 0

        if direction == -1:
            return self.get_connected_step_up(identifier)

        if direction == 1:
            return self.get_connected_step_down(identifier)
        assert_msg = "Can not get connected step '%s' for step '%s'" % (identifier, self.identifier)
        assert False, assert_msg

    def read_setting(self, name, default=None, hierarchy_lookup=True):
        val = self.unit.settgs.read([self.identifier, name], hierarchy_lookup)
        if val is None:
            return default
        return val

    def read_setting_from_connected(
        self, identifier, name, default=None, direction=1, hierarchy_lookup=True
    ):
        step = self.get_connected_step(identifier, direction)
        if not step:
            return default
        return step.read_setting(name, default, hierarchy_lookup)

    def enabled(self):
        if "enabled" not in self.settings:
            return True
        return self.settings["enabled"]

    def disabled_by_command_line(self):
        if self.stage.identifier in cfg.args.no_steps:
            return False
        if cfg.args.only_steps and self.stage.identifier not in cfg.args.only_steps:
            return False
        return True

    def work(self):
        if not self.disabled_by_command_line():
            return
        if not self.enabled():
            self.log.skipped()
            return

        try:
            hooks = work_unit.Hooks(self.identifier, self.unit.settgs, self.log)
            hooks.pre()
            if self.do_work() == 1:
                self.log.skipped()
            else:
                self.log.success()
            hooks.post()
        except HookError as error:
            if not error.post:
                self.log.skipped()
            raise
        except WorkError as error:
            self.log.failed()
            if self.unit.settgs.read([self.identifier, "continue on error"]):
                # TODO: print some log to terminal as well?
                self.log.warning("There was an error but the step settings specified to move on.")
            else:
                raise

    def do_work(self):
        if self.plugin:
            return self.plugin.work()
        else:
            assert self.callers
            for caller in self.callers:
                # TODO: should we allow more than one caller to work?
                return caller.do_work_dependent(self)

    def do_work_dependent(self, dependent):
        if not self.disabled_by_command_line():
            return
        if not self.enabled():
            return
        assert self.plugin
        self.plugin.work_dependent(dependent)
