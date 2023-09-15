# SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse, yaml

from . import utils
from .settings import Settings


class ProjectUndefined(Exception):
    def __init__(self, err):
        self.message = "Error: projects from command line have erroneous format."
        for e in err:
            self.message += "\n'%s' with faulty part '%s'." % (e[0], e[1])
        super().__init__(self.message)


class ArgumentMisformed(Exception):
    def __init__(self, option, argument, extra_msg=""):
        self.option = option
        self.message = "Option '" + option + "' has misformed argument: '" + argument + "'."
        if extra_msg:
            self.message += " " + extra_msg
        super().__init__(self.message)


class Arguments:
    def __init__(self):
        parser = argparse.ArgumentParser(description="FDBuild - create projects and work with them")

        parser.add_argument(
            "projects",
            nargs="*",
            default=[],
            help="projects to work on relative to workpath, when specified all dependencies will be ignored,\
                                    for example: prj1/prj2",
        )
        parser.add_argument(
            "-w", "--work-path", help="directory to work on (default: current working directory)"
        )
        parser.add_argument(
            "-t",
            "--top-level-path",
            help="top level path up to consider settings from (default: no limit)",
        )
        parser.add_argument(
            "-r",
            "--resume-from",
            help="start work at unit and continue work on other units from this point",
        )
        parser.add_argument("--init", action="store_true", help="initialise as top-level directory")
        parser.add_argument(
            "--init-with-template", help="initialise a project with a pre-defined template"
        )
        parser.add_argument("--no", help="steps to omit, list multiple with comma")
        parser.add_argument("--only", help="steps to only do, list multiple with comma")
        parser.add_argument(
            "--only-structure",
            action="store_true",
            help="only structurize the project and abort afterwards",
        )

        parser.add_argument(
            "--set", help="enforce setting (example: --set build:clear:true", dest="set0"
        )
        parser.add_argument("--set1", help="enforce another setting")
        parser.add_argument("--set2", help="enforce another setting")
        parser.add_argument("--set3", help="enforce another setting")

        parser.add_argument(
            "--noconfirm",
            action="store_true",
            help="do not ask for confirmations, proceed with default action",
        )
        parser.add_argument("--verbose", action="store_true", help="show full log in output")
        parser.add_argument(
            "--version", action="store_true", help="output version information and exit"
        )

        args = parser.parse_args()

        self.get_projects_arg(args)
        self.get_only_steps_args(args)
        self.get_no_steps_args(args)

        self.get_settings_args(args)

        self.resume_from = args.resume_from

        self.workpath = args.work_path
        self.toplevelpath = args.top_level_path

        self.init = args.init
        self.init_with_template = args.init_with_template

        self.verbose = args.verbose
        self.noconfirm = args.noconfirm
        self.version = args.version

        self.only_structure = args.only_structure

    def get_settings_args(self, args):
        settings_data = {}

        def process_next_setting_arg(i, args):
            if i == 0:
                arg = args.set0
                opt_name = "--set"
            elif i == 1:
                arg = args.set1
                opt_name = "--set1"
            elif i == 2:
                arg = args.set2
                opt_name = "--set2"
            elif i == 3:
                arg = args.set3
                opt_name = "--set3"
            else:
                assert False

            if arg is None:
                return

            arg_list = arg.split(":")
            if len(arg_list) < 2:
                raise ArgumentMisformed(opt_name, arg)

            indent = 1
            yaml_input = arg_list[0] + ":"

            if len(arg_list) > 2:
                for key in arg_list[1:-1]:
                    yaml_input += "\n" + indent * "  " + key + ":"
                    indent += 1

            if indent != len(arg_list) - 1:
                # Misformed input.
                raise ArgumentMisformed(opt_name, arg)

            yaml_input += " " + arg_list[-1]

            try:
                dic = yaml.safe_load(yaml_input)
            except:
                raise ArgumentMisformed(opt_name, arg)

            settings = settings_data

            while True:
                key = list(dic)[0]
                dic = dic[key]

                val_is_dict = isinstance(dic, dict)

                if key not in settings:
                    settings[key] = dic
                elif not val_is_dict and settings[key] != dic:
                    raise ArgumentMisformed(opt_name, arg, "Key-value pair already set.")

                if not val_is_dict:
                    break

                settings = settings[key]

        for i in range(4):
            process_next_setting_arg(i, args)

        self.settings = Settings(None, None, data=settings_data)

    def get_projects_arg(self, args):
        self.projects = args.projects
        if not self.projects:
            return

        prjs = []
        mdls = []

        for itm in self.projects:
            itms = itm.split(":", 1)

            if itms[0]:
                prjs.append(itms[0])

            if len(itms) == 2 and itms[1]:
                mdls.append(itms[1])

        err = []
        if not utils.get_prjs_names(prjs, err) or not utils.get_mdls_names(mdls, err):
            raise ProjectUndefined(err)

    def get_only_steps_args(self, args):
        only_steps = args.only
        self.only_steps = []
        if not only_steps:
            return

        self.only_steps = only_steps.split(",")

    def get_no_steps_args(self, args):
        no_steps = args.no
        self.no_steps = []
        if not no_steps:
            return

        self.no_steps = no_steps.split(",")
