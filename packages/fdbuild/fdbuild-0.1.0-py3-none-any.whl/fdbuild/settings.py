# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, yaml

from . import config as cfg


def parse_variable(s):
    len_s = len(s)
    var = ""
    cnt = 0
    for i in range(len_s):
        c = s[i]
        if c in ["{", "@"]:
            return [None, 0]
        if c == "}":
            break
        var = var + c
        cnt = cnt + 1

    return [var, cnt + 1]


class Settings:
    def __init__(self, path, parent_settings, data=None):
        self.path = path
        self.parent = parent_settings

        if not data is None:
            self.data = data
            return

        try:
            with open(path, "r") as file:
                # TODO: error handling
                self.data = yaml.safe_load(file)
        except FileNotFoundError:
            self.data = {}

    def lookup_variable(self, var, hierarchy_lookup):
        # settings variables can have different formats:
        # * $itm in same settings file at item 'itm'
        # * $cat1$cat2$itm - in same settings file at:
        #   cat1:
        #       cat:2
        #           itm:
        # * prj1/prj2$itm - in settings file of project prj1/prj2
        #   relative to own settings file at item 'itm'
        # * /prj1/prj2$itm - in settings file of project prj1/prj2
        #   originating from toplevel path
        #   item 'itm'

        if var[0] == "/":
            path = cfg.TOPLVL_PATH
            var = var[1:]
        else:
            path = self.path

        sections_tree = []

        def find_end_section(s, begin):
            for i, c in enumerate(s[begin:]):
                if c == "$":
                    return begin + i
            return -1

        def find_end_prj(s, begin):
            for i, c in enumerate(s[begin:]):
                if c in ["/", ":", "$"]:
                    return begin + i
            return -1

        i = 0
        while i < len(var):
            c = var[i]
            if c == "$":
                # in settings file
                sec_end = find_end_section(var, i + 1)
                if sec_end == -1:
                    # worked whole var
                    sections_tree.append(var[i + 1 :])
                    break

                sections_tree.append(var[i + 1 : sec_end])
                i = sec_end

            elif c == "/":
                # in project
                prj_end = find_end_prj(var, i + 1)
                if prj_end == -1:
                    # error - could not find next item
                    return
                prj = var[i + 1 : prj_end]
                path = os.path.join(path, prj)
                if not os.path.isdir(path):
                    # error - project folder does not exist
                    return
                i = prj_end

        settgs = Settings(path, None)
        if not settgs:
            return

        return settgs.read(sections_tree, hierarchy_lookup)

    def parse_string(self, s, hierarchy_lookup):
        i = 0
        ret = ""

        while i < len(s):
            if s[i - 1] != "@" and s[i] == "@" and s[i + 1] == "{":
                # variable
                var, cnt = parse_variable(s[i + 2 :])
                if var is None:
                    # error
                    return
                var_str = self.lookup_variable(var, hierarchy_lookup)
                if var_str is None:
                    # error
                    return

                # plus the two brackets { and }
                i = i + cnt + 2
                ret = ret + var_str

            else:
                ret = ret + s[i]
                i = i + 1

        return ret

    def unfold_sections(self, sections_tree):
        secs_len = len(sections_tree)

        data = dict(self.data)

        for i in range(0, secs_len):
            if i < secs_len:
                if not isinstance(data, dict):
                    # error - not a collection
                    return
            try:
                data = data[sections_tree[i]]
            except KeyError:
                return

        return data

    def get_adhoc_parent(self):
        if self.parent:
            return self.parent
        if self.path is None:
            return

        # this is the directory the settings file
        # self is in
        self_dir = os.path.dirname(self.path)

        if self_dir == cfg.TOPLVL_PATH:
            # do not read settings file above toplevel
            return None

        parent_dir = os.path.dirname(self_dir)

        return Settings(os.path.join(parent_dir, cfg.SETTGS_NAME), None)

    def read_merged(self, sections_tree, non_dict_key=""):
        """Read a dictionary with all its keys and the keys of including dictionaries being
        merged with the respective values from parent projects. The non_dict_key string can
        be set to inform the function about a special key in the returned dictionary that will
        hold a plain value in case one of the merged values is not a dictionary."""
        own_data = self.read(sections_tree, hierarchy_lookup=False)

        def read_parent():
            adhoc_parent = self.get_adhoc_parent()
            if adhoc_parent:
                return adhoc_parent.read_merged(sections_tree, non_dict_key)
            return {}

        if own_data is None:
            return read_parent()

        has_dict = isinstance(own_data, dict)

        if not has_dict and not non_dict_key:
            return {}

        ret_data = read_parent()

        if has_dict:
            for key, val in own_data.items():
                ret_data[key] = val
        else:
            ret_data[non_dict_key] = own_data

        return ret_data

    def command_line_override(self, sections_tree, data):
        if cfg.args.settings == self:
            return data

        cfg_data = cfg.args.settings.read(sections_tree, False)
        if cfg_data is None:
            return data

        def recurse_override(override, target):
            if not isinstance(target, dict):
                # Simple override of plain value.
                return override
            if not isinstance(override, dict):
                # Simple override with plain value.
                return override

            for key, val in override.items():
                if key in target:
                    target[key] = recurse_override(val, target[key])
                else:
                    target[key] = val

            return target

        return recurse_override(cfg_data, data)

    def read(self, sections_tree, hierarchy_lookup=True, parse_strings=True):
        data = self.unfold_sections(sections_tree)
        data = self.command_line_override(sections_tree, data)

        if data != None:
            if not isinstance(data, str) or not parse_strings:
                return data
            else:
                return self.parse_string(data, hierarchy_lookup)

        if hierarchy_lookup:
            adhoc_parent = self.get_adhoc_parent()
            if adhoc_parent:
                return adhoc_parent.read(sections_tree, True)
            else:
                return None

        return None

    def read_list(self, sections_tree, hierarchy_lookup=False):
        data = self.unfold_sections(sections_tree)
        data = self.command_line_override(sections_tree, data)

        if not data:
            if hierarchy_lookup:
                adhoc_parent = self.get_adhoc_parent()
                if adhoc_parent:
                    return adhoc_parent.read_list(sections_tree, True)
            return []

        if isinstance(data, str):
            s = self.parse_string(data, hierarchy_lookup)
            return [s]

        if not isinstance(data, list):
            # TODO: error?
            return []

        for i, s in enumerate(data):
            # currently only supports strings in lists
            if s:
                data[i] = self.parse_string(s, hierarchy_lookup)

        return data

    def read_configure_options(self):
        opts = self.read_list(["configure", "options"], True)

        if not isinstance(opts, list):
            return None

        for opt in opts:
            if not isinstance(opt, str):
                return None
        return opts

    def read_subprojects(self):
        return self.read_list(["projects"], hierarchy_lookup=False)

    def read_envvars(self, hierarchy_lookup=False):
        try:
            data = self.data["envvars"]
        except KeyError:
            return

        if not isinstance(data, dict):
            return None

        ret = {}

        for key, obj in data.items():

            def error_msg():
                print("Error: environment variable '%s' has faulty format." % key)

            if not isinstance(obj, dict):
                error_msg()
                # TODO: Abort?
                continue

            if "value" not in obj:
                error_msg()
                # TODO: Abort?
                continue

            prepend = False
            if "prepend" in obj:
                prepend = obj[
                    "prepend"
                ]  # TODO: Make this value retrievable with variables as well?
                if not isinstance(prepend, bool):
                    error_msg()
                    # TODO: Abort?
                    continue

            val_str = obj["value"]
            if not isinstance(val_str, str):
                return

            val = self.parse_string(val_str, hierarchy_lookup)

            ret[key] = {"value": val, "prepend": prepend}

        return ret

    def read_hook(self, phase, pre):
        rel = "pre" if pre else "post"

        # This also does an hierarchy lookup. Is this always what we want with hooks?
        data = self.read([phase, "hooks", rel])
        if not isinstance(data, str):
            return

        return self.parse_string(data, True)

    def read_plugin(self, cat):
        data = self.read(["plugins", cat])
        if not isinstance(data, str):
            return

        return self.parse_string(data, True)
