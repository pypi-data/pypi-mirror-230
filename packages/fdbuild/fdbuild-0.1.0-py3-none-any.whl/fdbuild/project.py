# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from . import (
    config as cfg,
    defaulttexts,
    log as logger,
    settings,
    utils,
)
from .work_unit import WorkUnit, Hooks, unit_finder
from .structurizer import Structurizer
from .exceptions import *
from .utils import tcolors


class Project(WorkUnit):
    def __init__(self, path, leader):
        self.path = path

        project_name = os.path.basename(path)
        if leader:
            ident = os.path.join(leader.ident, project_name)
            self.work_ident = os.path.join(leader.work_ident, project_name)
        else:
            ident = project_name

            if path == cfg.WORK_PATH:
                work_path_complete = True
                work_ident = ""
            else:
                work_path_complete = False
                work_ident = project_name

            cut_path = os.path.dirname(path)

            if path != cfg.TOPLVL_PATH:
                while True:
                    next_basename = os.path.basename(cut_path)
                    ident = next_basename + os.sep + ident
                    if cut_path == cfg.WORK_PATH:
                        work_path_complete = True
                    if not work_path_complete:
                        work_ident = next_basename + os.sep + work_ident
                    if cut_path == cfg.TOPLVL_PATH:
                        break
                    cut_path = os.path.dirname(cut_path)
            self.work_ident = work_ident

        super().__init__(ident, leader)

        self.projects = []
        self.has_own_work = False
        self.number = -1

        self.log_path = self.path + os.sep + "log"

    def get_header(self):
        nl = "\n"
        if self.number > 0 and cfg.PROJECTS_COUNT > 1:
            count_info = " (" + str(self.number) + "/" + str(cfg.PROJECTS_COUNT) + ")"
        else:
            count_info = ""
        line_mid_len = 9 + len(self.ident) + len(count_info)
        indent = " " + tcolors.BLUEBACK + "  "
        exdent = "  " + tcolors.ENDC + nl
        header = indent + " " * line_mid_len + exdent
        return (
            nl
            + header
            + indent
            + tcolors.BOLD
            + tcolors.BLUEBACK
            + "Project: "
            + self.ident
            + count_info
            + exdent
            + header
        )

    def get_steps_leader(self):
        if self.leader:
            return self.leader

        if self.path == cfg.TOPLVL_PATH:
            # Do not read steps above toplevel.
            return None

        parent_dir = os.path.dirname(self.path)

        parent_project = Project(parent_dir, None)
        parent_project.init_settings(None)
        parent_project.init_steps()
        return parent_project

    def init(self, parent_settings, args, return_on_structure=True):
        if not self.is_in_prjs_arg(args):
            return 0

        full_init = args.init
        settgs_path = os.path.join(self.path, cfg.SETTGS_NAME)

        def write_settings_default_text():
            try:
                with open(settgs_path, "w") as file:
                    file.write(defaulttexts.projectsettings())
            except IOError:
                print("Error when writing new settings file at: '%s'", settgs_path)
                utils.exit(1)

        ret_own = 0

        if not os.path.isdir(self.path):
            if not full_init:
                print(
                    "Error: directory for project '%s' is missing at:" % self.ident,
                    "'%s'" % self.path,
                    "and FDBuild was not launched with '--init.'",
                    sep="\n",
                )
                raise InitError()

            utils.make_dir(self.path)
            write_settings_default_text()
            print(
                "New project %s recognized." % self.ident,
                "Created directory '%s'" % self.path,
                "and at this location settings file '%s'." % cfg.SETTGS_NAME,
                sep="\n",
            )
            ret_own = 1

        if not os.path.isfile(settgs_path):
            if not full_init:
                print(
                    "Error: settings file for project '%s' is missing at:" % self.ident,
                    "'%s'" % self.path,
                    "and FDBuild was not launched with '--init.'",
                    "Aborting...",
                    sep="\n",
                )
                raise InitError()

            write_settings_default_text()
            print(
                "Settings file for project %s was missing." % self.ident,
                "Created settings file at %s." % settgs_path,
                sep="\n",
            )
            ret_own = 1

        #
        # init phase 1 complete
        # now read in own settings
        self.init_settings(parent_settings)

        try:
            self.init_steps()
        except InitError as error:
            if error.message:
                error.message = "Project " + self.ident + "\n  " + error.message
            raise error

        self.structurizer = Structurizer(self.settgs)
        # TODO: Allow to force a restructuring? That would mean to not try to initialize subunits first

        return self.init_subunits(args, ret_own)

    def init_settings(self, parent_settings):
        settgs_path = os.path.join(self.path, cfg.SETTGS_NAME)
        self.settgs = settings.Settings(settgs_path, parent_settings)
        if self.settgs.data is None:
            print("Error: settings file of project '%s' is empty." % self.ident, sep="\n")
            raise InitError()

    def init_subunits(self, args, ret):
        prjs_settgs = self.settgs.read_subprojects()

        if prjs_settgs:
            # Init of subprojects.
            ret = ret + self.init_subprojects(prjs_settgs, args)
        else:
            self.has_own_work = True

        return ret

    def is_in_prjs_arg(self, args):
        if self.path == cfg.WORK_PATH:
            # work path project - always work on that one
            return True

        if not args.projects:
            return True

        for p in args.projects:
            if ":" in p:
                p, m = p.split(":")
            if self.work_ident == p:
                return True
        return False

    def init_subprojects(self, prjs_settgs, args):
        full_init = args.init

        #
        # read in projects in settings file
        #
        if prjs_settgs:
            take_subdirs = False
            if prjs_settgs == ["/"]:
                # all subdirectories with syntactical correct names
                take_subdirs = True
                prjs_settgs = [f for f in os.listdir(self.path) if os.path.isdir(f)]

            errors = []
            utils.get_prjs_names(prjs_settgs, errors, [os.sep])

            if errors and not take_subdirs:
                print(
                    "Error: project names in settings file '%s'" % cfg.SETTGS_NAME,
                    "of project '%s' are bogus." % self.path,
                    sep="\n",
                ),
                for e in errors:
                    print("'%s' has unallowed sequence: '%s'" % (e[0], e[1]))
                raise InitError()
        else:
            prjs_settgs = []

        def get_normalized_relative_names(lst):
            ret = []
            for itm in lst:
                if itm[0] == "/":
                    itm = itm[1:]

                work_prj = os.path.basename(cfg.WORK_PATH)
                if itm[0] == ":":
                    itm_norm = work_prj
                else:
                    itm_norm = os.path.join(work_prj, itm)

                len_ident = len(self.ident)
                if itm_norm.startswith(self.ident) and len_ident < len(itm_norm):
                    itm_ident = itm_norm[len_ident + 1 :]
                    ret.append(itm_ident.split(os.sep, 1)[0])

            return ret

        if args.projects:
            prjs_arg = get_normalized_relative_names(args.projects)
        else:
            prjs_arg = []

        prjs_arg_new = []

        for pname in prjs_arg:
            if pname not in prjs_settgs:
                prjs_arg_new.append(pname)

        if prjs_arg_new:
            if full_init:
                if len(prjs_arg_new) > 1:
                    print("Warning: projects")
                    for p in prjs_arg_new:
                        print("- '%s'" % p)
                    print("not listed in settings file:")
                else:
                    print("Warning: project '%s' not listed in settings file" % (prjs_arg_new[0]))

                print(
                    "'%s'." % self.settgs.path,
                    "Though '--init' was requested, so we will try to create directories and settings files, "
                    "but afterwards stop.\n",
                    sep="\n",
                )
            else:
                for p in prjs_arg_new:
                    print(
                        "Error: project '%s' not listed in settings file '%s'."
                        % (p, self.settgs.path)
                    )

                print(
                    "\nRun FDBuild with '--init' to dynamically initialize project and subprojects.",
                    "To afterwards further work on them, go first in their respective directories",
                    sep="\n",
                )
                raise InitError()

        for p in prjs_arg_new:
            self.projects.append(Project(self.path + os.sep + p, self))

        for p in prjs_settgs:
            if prjs_arg and p not in prjs_arg:
                continue
            self.projects.append(Project(self.path + os.sep + p, self))

        has_init = len(prjs_arg_new) > 0
        for p in self.projects:
            ret_init = p.init(self.settgs, args)
            has_init = has_init or ret_init

        return has_init

    def update_subproject(self, p_old, p_new):
        for i, p in enumerate(self.projects):
            if p == p_old:
                self.projects[i] = p_new
                return

    def structurize(self, args, self_structure=True):
        # If there is no structurizer for this project, or it is not meant to be run at all
        # or is explicitly set to not self_structure try at least for subprojects and then return.
        if not self.structurizer.valid() or not self.valid(args) or not self_structure:
            for p in self.projects:
                p.structurize(args, True)
            return self

        self.set_envvars()
        print(self.get_header())

        work_project = self
        log = logger.StructureLog(self.log_path)
        log.head()

        hooks = Hooks("structure", self.settgs, log)
        hooks.pre()

        try:
            is_restructured = self.structurizer.start(log)
        except StructurizeError as error:
            # For now we on error just print out a warning and exit.
            log.failed()
            print(
                "Error on retrieving structure for project '%s' from plugin '%s': %s"
                % (self.ident, error.plugin_name, str(error))
            )
            utils.exit(1)

        log.success()
        if is_restructured:
            hooks.post()

            # Replace ourselve with new project...
            work_project = Project(self.path, self.leader)

            if self.leader:
                # ... by informing our leader.
                # TODO: We could make this maybe implicit by the return value of
                #       this function. But when we need to make sure in above loop that
                #       nothing breaks.
                self.leader.update_subproject(self, work_project)
                leader_settgs = self.leader.settgs
            else:
                leader_settgs = None

            # And follow through on the new project.
            try:
                if work_project.init(leader_settgs, args) > 0:
                    # Some subprojects needed full init.
                    # Exit so the user can customize setting files,
                    # then he shall run the script again.
                    utils.exit(0)
            except InitError as error:
                # TODO: handle?
                raise error

            try:
                # Now start structuring sub-projects (do not restructure the current one).
                work_project.structurize(args, False)
            except StructurizeError as error:
                # TODO: handle?
                raise error

        return work_project

    def count(self):
        direct_dependencies = self.get_direct_dependencies()
        for d in direct_dependencies:
            u = unit_finder(self, d)
            if u is None:
                # ignore dependencies that are not
                # to be built this invocation
                continue
            u.count()

        if self.number < 0 and self.has_own_work:
            cfg.PROJECTS_COUNT = cfg.PROJECTS_COUNT + 1
            self.number = cfg.PROJECTS_COUNT

        for p in self.projects:
            p.count()

    def absolute_path(self, subpath):
        if subpath and os.path.isabs(subpath):
            return subpath
        return os.path.join(self.path, subpath)

    def work_units(self, args):
        for p in self.projects:
            p.work(args)

    def work(self, args):
        if self.worked:
            return

        # If not meant to be run itself try at least for sub-units.
        if not self.valid(args):
            self.work_units(args)
            return

        self.worked = True

        direct_dependencies = self.get_direct_dependencies()
        has_direct_dependencies = bool(direct_dependencies)

        if has_direct_dependencies:
            self.work_depends(direct_dependencies, args)

        if not self.structurizer.valid() or has_direct_dependencies:
            self.set_envvars()
            if self.has_own_work:
                print(self.get_header())

        os.chdir(self.path)

        if self.has_own_work:
            super().work(args)

        self.work_units(args)
