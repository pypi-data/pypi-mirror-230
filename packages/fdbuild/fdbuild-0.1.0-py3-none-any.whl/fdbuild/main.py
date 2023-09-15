# SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.metadata, os, sys

from . import (
    arguments,
    config as cfg,
    defaulttexts,
    project,
    settings,
    templater,
    utils,
)
from .exceptions import *
from .utils import tcolors


def setup_work_path():
    workpath = cfg.args.workpath if cfg.args.workpath else os.getcwd()
    workpath = os.path.abspath(workpath)

    if not os.path.isdir(workpath):
        print("Error: provided path to work on is not a directory.")
        utils.exit(1)

    def find_upper_project_step(path):
        if os.path.isfile(os.path.join(path, cfg.SETTGS_NAME)):
            return path

        parentpath = os.path.dirname(path)
        if parentpath == path:
            # root path - no upper project found
            return ""

        return find_upper_project_step(parentpath)

    # if init is specified the user wants to
    # init the workpath
    if not cfg.args.init and not cfg.args.init_with_template:
        upper_project_path = find_upper_project_step(workpath)

        if upper_project_path:
            workpath = upper_project_path

    cfg.WORK_PATH = workpath


def check_work_path_settings_file(init):
    workpath_cfg = os.path.join(cfg.WORK_PATH, cfg.SETTGS_NAME)
    if not os.path.isfile(workpath_cfg):
        if init:
            with open(workpath_cfg, "w") as file:
                file.write(defaulttexts.projectsettings())

            print(
                "FDBuild project has been initialized at: ",
                cfg.WORK_PATH,
                "--> Change values in settings file '%s' to your liking and rerun FDBuild."
                % cfg.SETTGS_NAME,
                sep="\n",
            )
            utils.exit(0)
        else:
            # no settings file and no init
            print(
                "Settings file '%s' is missing in work directory '%s'"
                % (cfg.SETTGS_NAME, cfg.WORK_PATH),
                "You have two alternatives, in order to associate this directory with FDBuild:",
                "1. initialize new top-level FDBuild directory in here by running",
                "   FDBuild with '--init' option,",
                "2. run FDBuild from some ancestor directory and adjust setting files,",
                "   such that this directory becomes a project or module.",
                sep="\n",
            )
            utils.exit(1)


def set_toplvl_from_arg(toplvl_arg):
    def is_super_dir(sup, sub):
        path = sub
        while True:
            if path == sup:
                return True

            parentdir = os.path.dirname(path)
            if parentdir == path:
                return False
            path = parentdir

    def not_has_settgs(sup, sub):
        if not sup:
            return
        path = sub
        while True:
            if not os.path.isfile(path + os.sep + cfg.SETTGS_NAME):
                return path
            if path == sup:
                return
            else:
                path = os.path.dirname(path)

    if toplvl_arg and not is_super_dir(toplvl_arg, cfg.WORK_PATH):
        print(
            "Error: provided top level path",
            "'" + toplvl_arg + "'",
            "is not a parent directory of work path",
            "'" + cfg.WORK_PATH,
            sep="\n",
        )
        utils.exit(1)

    error_dir = not_has_settgs(toplvl_arg, cfg.WORK_PATH)
    if error_dir:
        print(
            "Error: settings file '%s' missing in directory:" % cfg.SETTGS_NAME,
            "'%s'," % error_dir,
            "which needs one, since it lies between the provided work path:",
            "'%s'," % cfg.WORK_PATH,
            "and the provided top level path:",
            "'%s'." % toplvl_arg,
            sep="\n",
        )
        utils.exit(1)

    cfg.TOPLVL_PATH = toplvl_arg


def set_toplvl_automatic():
    path = os.path.dirname(cfg.WORK_PATH)
    path_old = cfg.WORK_PATH

    while True:
        # we stop when:
        # (1) we are at /,
        # (2) the next directory has no settings file,
        # (3) there is an error reading the next settings
        #     file,
        # (4) the next directory's settings file does not
        #     specify any projects,
        # (5) the next settings file does not name the sub-
        #     directory we were coming from as a project.
        if path == path_old:
            # (1) -> top-lvl project is in root
            cfg.TOPLVL_PATH = path
            return

        settgs_path = os.path.join(path, cfg.SETTGS_NAME)

        if not os.path.isfile(settgs_path):
            # (2) -> top-lvl project is the dir before
            cfg.TOPLVL_PATH = path_old
            return

        try:
            settgs = settings.Settings(settgs_path, None)
            prjs = settgs.read_subprojects()
            if not prjs:
                # (4) -> top-lvl project is the dir before
                cfg.TOPLVL_PATH = path_old
                return

            elif prjs != ["/"] and os.path.basename(path_old) not in prjs:
                # (5) -> top-lvl project is the dir before
                cfg.TOPLVL_PATH = path_old
                return
        except IOError:
            # (3) -> abort!
            print("Critical error when reading in settings file:", "'%s'" % settgs_path, sep="\n")
            utils.exit(1)

        path_old = path
        path = os.path.dirname(path)
        # TODO: make sure a parent directory doesn't have
        #       an unallowed name (src, build,...)

    print("Error: could not locate top-level settings file.")
    utils.exit(1)


def setup_toplvl_path(args):
    if args.toplevelpath:
        try:
            toplvl = os.path.abspath(args.toplevelpath)
        except:
            print("Error: provided top level path is not a real path.")
            utils.exit(1)
        set_toplvl_from_arg(toplvl)
    else:
        set_toplvl_automatic()


def handle_work_error(error):
    print("\n" + "The current work step failed!")

    def print_text(text, name, n):
        if cfg.args.verbose:
            return
        if not text:
            return
        lines = text.split("\n")

        if len(lines) <= n:
            print("Here is its %s:\n" % name)
            print(text)
            return

        print("Here are the last %s lines of its %s:\n" % (n, name))
        for line in lines[-n:]:
            print(line)

    print_text(error.stdout(), "standard output", 50)
    print_text(error.stderr(), "error output", 50)
    if error.log:
        print(tcolors.WARNING + "\nAll output was logged to: %s\n" % error.log.path + tcolors.ENDC)


def handle_init_error(error):
    if error.message:
        print("Initialization error: " + error.message)
    if error.log:
        print(tcolors.WARNING + "\nAll output was logged to: %s\n" % error.log.path + tcolors.ENDC)
    if not error.message:
        raise error


def handle_structurize_error(error):
    print("\n" + "Structurizing the project failed!")
    if error.log:
        print(tcolors.WARNING + "\nAll output was logged to: %s\n" % error.log.path + tcolors.ENDC)


def handle_init_on_structurize_error(error):
    print("\n" + "Reinitializing the project after structurizing failed!")
    if error.log:
        print(tcolors.WARNING + "\nAll output was logged to: %s\n" % error.log.path + tcolors.ENDC)


def handle_template_error(error):
    print("\n" + "Templating the project failed with: " + error.message)


## main ##
def main():
    try:
        cfg.args = arguments.Arguments()
    except (arguments.ProjectUndefined, arguments.ArgumentMisformed) as error:
        print(error.message)
        utils.exit(1)

    if cfg.args.version:
        print(importlib.metadata.version("fdbuild"))
        return

    # setup work path
    setup_work_path()

    # deploy template
    if cfg.args.init_with_template:
        cfg.WORK_PATH = os.path.join(cfg.WORK_PATH, cfg.args.init_with_template)
        setup_toplvl_path(cfg.args)
        try:
            templater.run(cfg.args)
            utils.exit(0)
        except TemplateError as error:
            handle_template_error(error)
            utils.exit(1)

    # check settings file
    check_work_path_settings_file(cfg.args.init)

    # setup top level path
    setup_toplvl_path(cfg.args)

    # Remember the resume-from setting. It is unset after structuring by the first project to be resumed and
    # so we need to reapply it in between.
    #
    # Note: All projects are initialized at the start, not only the ones which are resumed,
    #       i.e. it is not unset in the init call.
    resume_from = cfg.args.resume_from

    # Create the top-most work project. It will be an ancestor to all other projects.
    work_project = project.Project(cfg.WORK_PATH, None)

    try:
        if work_project.init(None, cfg.args) > 0:
            # Some subprojects needed full init.
            # Exit so the user can customize setting files,
            # then he shall run the script again.
            utils.exit(0)
    except InitError as error:
        handle_init_error(error)
        return 1

    if cfg.args.init:
        print(
            "Parameter '--init' was set, but no requested " "project needed initialization.",
            "Either change settings to include additional "
            "ressources or just run FDBuild without '--init'",
            "to work on available ones.",
            sep="\n",
        )
        return 1

    try:
        # The structurizing gives us either the same or a replacement project back.
        work_project = work_project.structurize(cfg.args)
    except StructurizeError as error:
        handle_structurize_error(error)
        return 1
    except InitError as error:
        handle_init_on_structurize_error(error)
        return 1

    if cfg.args.only_structure:
        print("\nExiting now because the --only-structure option was set.")
        return 0

    # Determines the overall projects counts and let each knows its position.
    work_project.count()

    cfg.args.resume_from = resume_from
    # start requested work
    try:
        work_project.work(cfg.args)
    except WorkError as error:
        handle_work_error(error)
        return 1

    return 0


## `fdbuild` entry point
def run():
    try:
        ret = main()
        utils.show_cursor()
        sys.exit(ret)
    except:
        utils.show_cursor()
        raise
