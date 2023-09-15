# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, yaml

from . import (
    config as cfg,
    pluginfactory as pluginfac,
    settings,
    utils,
)
from .exceptions import *


class Node:
    def __init__(self, path, structure, post_hook):
        self.path = path
        self.structure = structure
        self.post_hook = post_hook

        self.settgs_path = os.path.join(self.path, cfg.SETTGS_NAME)
        self.settgs = None
        self.projects = []

        self.settgs_updates = []
        self.has_change = False

    def settgs_changed_level(self, keys, parent_settgs_data, update_data):
        cur_key = keys[-1]
        if cur_key not in parent_settgs_data:
            self.settgs_updates.append((keys, update_data))
            return

        settgs_data = parent_settgs_data[cur_key]

        if isinstance(settgs_data, dict) and isinstance(update_data, dict):
            for k, v in update_data.items():
                if k in settgs_data:
                    self.settgs_changed_level(keys + [k], settgs_data, v)
                else:
                    self.settgs_updates.append((keys + [k], v))

        elif isinstance(settgs_data, list) and isinstance(update_data, list):
            for v in update_data:
                if v not in settgs_data:
                    self.settgs_updates.append((keys, update_data))
                    break

        elif settgs_data != update_data:
            self.settgs_updates.append((keys, update_data))

    def settgs_create(self):
        try:
            for key, val in self.structure.items():
                if key in ["projects"]:
                    val = [next(iter(itm)) for itm in val]  # get list of keys
                self.settgs_updates.append(([key], val))
        except:
            # TODO: handle bugs from plugin
            raise

    def settgs_changed(self):
        for key, val in self.structure.items():
            if key in ["projects"]:
                # Get list of keys.
                val = [next(iter(itm)) for itm in val]

                # TODO: this could be wrong on positions of units being moved in the list.
                if key in self.settgs.data:
                    units = self.settgs.data[key]
                    if val == units:
                        continue

                self.settgs_updates.append(([key], val))

            else:
                self.settgs_changed_level([key], self.settgs.data, val)

    def check(self, units_new, units_changed):
        if not os.path.isfile(self.settgs_path):
            self.has_change = True
            self.settgs_create()
            units_new.append((self.path, "project"))
        else:
            self.settgs = settings.Settings(self.settgs_path, None)
            self.settgs_changed()

            if self.settgs_updates:
                self.has_change = True
                units_changed.append((self.path, "project"))

        def get_lst(name):
            try:
                return self.structure[name]
            except KeyError:
                return []

        prj_structure = get_lst("projects")

        for prj in prj_structure:
            assert isinstance(prj, list)
            project_tuple = next(iter(prj))

            prj_ident = prj[0]
            prj_data = prj[1]

            prj_node = Node(os.path.join(self.path, prj_ident), prj_data, self.post_hook)
            self.projects.append(prj_node)
            prj_node.check(units_new, units_changed)

    def dump_prj_settgs(self):
        try:
            with open(self.settgs_path, "r") as file:
                settgs_dic = yaml.safe_load(file)
        except FileNotFoundError:
            settgs_dic = {}

        for keys, data in self.settgs_updates:
            if keys in [["projects"]]:
                # just overwrite
                settgs_dic[keys[0]] = data
                continue

            dic = settgs_dic

            parent_keys = keys[:-1]
            target_key = keys[-1]

            for k in parent_keys:
                dic = dic[k]

            if target_key in dic and isinstance(dic[target_key], list) and isinstance(data, list):
                # merge lists
                for v in data:
                    if v not in dic[target_key]:
                        dic[target_key].append(v)
            else:
                dic[target_key] = data

        try:
            with open(self.settgs_path, "w") as file:
                yaml.dump(settgs_dic, file, default_flow_style=False)
        except IOError:
            print("Error when writing changed structure to settings file\n'%s'", self.settgs_path)
            utils.exit(1)

    def dump_settgs(self, path, dic):
        try:
            with open(path, "r") as file:
                dump_dic = yaml.safe_load(file)
        except FileNotFoundError:
            dump_dic = {}

        def set_recursive(in_dic, parent_out_dic, key):
            if key not in parent_out_dic:
                parent_out_dic[key] = in_dic
                return
            out_dic = parent_out_dic[key]

            if isinstance(in_dic, dict) and isinstance(out_dic, dict):
                for k, v in in_dic.items():
                    set_recursive(v, out_dic, k)
            else:
                parent_out_dic[key] = in_dic

        for key, val in dic.items():
            if key in ["projects"]:
                # only take the key
                units_lst = [next(iter(u)) for u in val]
                val = units_lst

            set_recursive(val, dump_dic, key)

        try:
            with open(path, "w") as file:
                yaml.dump(dump_dic, file, default_flow_style=False)
        except IOError:
            print("Error when writing changed structure to settings file\n'%s'", self.settgs_path)
            utils.exit(1)

    def commit(self):
        utils.make_dir(self.path)
        if self.has_change:
            self.dump_prj_settgs()

        if self.post_hook:
            self.post_hook(self.path, self.structure)

        for prj in self.projects:
            prj.commit()


class Structurizer:
    def __init__(self, settgs):
        # No hierarchy lookup for structure plugin allowed.
        self.plugin_name = settgs.read(["structure", "plugin"], False)
        self.enabled = settgs.read(["structure", "enabled"], False)
        if self.enabled is None:
            self.enabled = True

        # The structure is always put at the position of its settings file.
        self.root_path = os.path.dirname(settgs.path)

        # TODO: only for the plugin at the moment to read structure category. Can this
        #       be made more specific?
        self.settgs = settgs

        if self.plugin_name:
            # No plugin found, no structure to be set.
            self.structure_plugin = pluginfac.create_structure(self.plugin_name, self)
        else:
            self.structure_plugin = None

    def path(self):
        return self.root_path

    def valid(self):
        return self.structure_plugin is not None and self.enabled

    def start(self, log):
        self.log = log

        def ask_to_continue():
            cntn = set(["y", "yes", ""])
            abrt = set(["n", "no"])
            question = "Continue? [Y/n] "

            if cfg.args.noconfirm:
                print(question + "y (--noconfirm)")
                return True

            utils.show_cursor()

            while True:
                c = input(question).lower()
                if c in cntn:
                    return True
                elif c in abrt:
                    return False
                else:
                    print("\nPlease type 'y' or 'n':")

        if self.check():
            # Changes will happen - ask for user allowance.
            if not ask_to_continue():
                # User decision - no error.
                # TODO: make this not directly exit but let's move on with the current structure?
                utils.exit(0)

            self.commit()

            print("")
            if cfg.args.only_structure:
                print(
                    "Project restructured. You can continue with potential sub-structures or exit now."
                )
            else:
                print(
                    "Project restructured. You can continue with potential sub-structures and following work steps or exit now."
                )
            print("")

            if not ask_to_continue():
                # User decision - no error.
                utils.exit(0)

            print("")
            return True

        # Nothing to do - still run the structurizer for eventual post-hooks.
        self.commit()

        return False

    def check(self):
        """Check if structure changes will be performed"""
        structure = self.structure_plugin.structure(self.log)
        if not isinstance(structure, dict):
            # Critical error. Structure plugin did not provide a structure map.
            raise StructurizeError(self.plugin_name)

        post_hook = None
        if hasattr(self.structure_plugin, "project_post_hook"):
            post_hook = self.structure_plugin.project_post_hook

        self.root_node = Node(self.root_path, structure, post_hook)

        units_new = []
        units_changed = []

        self.root_node.check(units_new, units_changed)

        if len(units_new):
            print("\nThe following units are new and will be created:")
            for u in units_new:
                print(u[1] + ": " + u[0])

        if len(units_changed):
            print("\nThe settings files of the following units will be changed:")
            for u in units_changed:
                print(u[1] + ": " + u[0])
            print("\n")

        return len(units_new) or len(units_changed)

    def commit(self):
        """Commit structure changes"""
        assert isinstance(self.root_node, Node)
        self.root_node.commit()
