# SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os, shutil, subprocess, sys, yaml
from importlib.metadata import entry_points

from . import (
    config as cfg,
    settings,
)
from .exceptions import TemplateError

templates_paths = []
used_templates = []


def dump_to_file(path, data):
    try:
        with open(path, "w") as file:
            yaml.dump(data, file, default_flow_style=False)
    except IOError:
        raise TemplateError(msg="Error when dumping to file at '%s'." % path)


def get_template_in_path(name, templates_path):
    path = os.path.join(templates_path, name + ".yaml")

    if not os.path.isfile(path):
        # Try directory instead.
        path = os.path.join(templates_path, name, "template.yaml")
    if not os.path.isfile(path):
        raise FileNotFoundError

    try:
        with open(path, "r") as file:
            content = yaml.safe_load(file)
            if not content:
                raise TemplateError(msg="Template file '%s' without content." % path)
            return content
    except IOError:
        raise TemplateError(msg="Error on reading template at '%s'." % path)


def get_template(name):
    for path in templates_paths:
        try:
            return (get_template_in_path(name, path), path)
        except FileNotFoundError:
            continue

    raise TemplateError(msg="Could not locate template '%s'." % name)


def dump_prj_settgs(path, data):
    if len(data) == 0:
        data = None
    dump_to_file(os.path.join(path, cfg.SETTGS_NAME), data)


def dump_mdl_settgs(path, ident, data):
    file_name = cfg.SETTGS_NAME_PREFIX + "_".join(ident.split("/")) + cfg.SETTGS_NAME_POSTFIX
    dump_to_file(os.path.join(path, file_name), data)


def process_project_string(prj_str, parent, names_out, templates_out, scripts_out):
    splitted = prj_str.split()
    if not splitted:
        raise TemplateError(msg="Project string is empty at project: %s" % parent)

    method = splitted.pop(0)

    if len(splitted) != 1:
        raise TemplateError(
            msg="Project string with mal-formed argument '%s' at project: %s" % (splitted, parent)
        )

    arg = splitted[0]

    if method == "template":
        if arg in used_templates:
            # Skip templates which have been applied already once.
            return
        names_out.append(arg)
        templates_out.append(arg)
        used_templates.append(arg)
    elif method == "script":
        scripts_out.append(arg)
    else:
        raise TemplateError(
            msg="Project string specificier '%s' malformed at project: %s" % (method, parent)
        )


def insert_data_field(tree, data_in, data_out, parent_settings):
    key = tree[-1]
    data = data_in[key]
    if isinstance(data, dict):
        # Again a dictionary.
        data_out[key] = dict(data)
        for key2 in data:
            insert_data_field(tree + [key2], data_in[key], data_out[key], parent_settings)
        if len(data_out[key]) == 0:
            del data_out[key]
    else:
        # Final data leaf. Check if this is already in settings.
        if parent_settings and parent_settings.read(tree, parse_strings=False) == data_in[key]:
            del data_out[key]
        else:
            data_out[key] = data_in[key]


def merge_dicts(dic1, dic2):
    """Merges dictionary dic2 into dictionary dic1 without overriding values."""
    for key, value in dic2.items():
        if key not in dic1:
            dic1[key] = value

        elif isinstance(value, dict):
            assert isinstance(dic1[key], dict)
            merge_dicts(dic1[key], value)

        elif isinstance(value, list):
            assert isinstance(dic1[key], list)
            if key == "projects":
                merge_projects_settings(dic1[key], value)
            else:
                for element in reversed(value):
                    if element not in dic1[key]:
                        dic1[key].insert(0, element)


def read_pre_template(template):
    data_in, data_path = get_template(template)
    data_out = {}

    for key in data_in:
        if key in ["projects", "template"]:
            continue
        insert_data_field([key], data_in, data_out, None)

    if "template" in data_in:
        pre_template_data = read_pre_template(data_in["template"])
        merge_dicts(data_out, pre_template_data)

    return data_out


def print_template_head(ident):
    level_count = len(ident.split(os.sep)) - 1
    gap = 3 * " "
    prefix = gap
    if level_count > 0:
        prefix = level_count * gap + "└─ "
    print(prefix + os.path.split(ident)[1])


def process_project(ident, parent_settings, data_in, data_path):
    print_template_head(ident)

    path = os.path.join(os.path.dirname(cfg.WORK_PATH), ident)
    os.mkdir(path)

    pre_template_data = {}
    prjs_in = None
    data_out = {}
    prjs = []
    templates = []
    scripts = []

    if not parent_settings:
        parent_settings = settings.Settings(
            os.path.join(path, cfg.SETTGS_NAME), None, {}
        ).get_adhoc_parent()

    if "template" in data_in:
        pre_template_data = read_pre_template(data_in["template"])
        merge_dicts(data_in, pre_template_data)

    for key in data_in:
        if key == "template":
            continue
        if key == "projects":
            prjs_in = data_in[key]
        else:
            insert_data_field([key], data_in, data_out, parent_settings)

    settgs = settings.Settings(os.path.join(path, cfg.SETTGS_NAME), parent_settings, data_out)

    if prjs_in:
        names = []
        for p in prjs_in:
            if isinstance(p, dict):
                names.append(next(iter(p)))
                prjs.append(p)
            elif isinstance(p, str):
                process_project_string(p, ident, names, templates, scripts)
            else:
                raise TemplateError(msg="Could not read project string at project: %s" % ident)
        if names:
            data_out["projects"] = names

    dump_prj_settgs(path, data_out)

    for p in prjs:
        assert isinstance(p, dict)
        for name, data in p.items():
            process_project(os.path.join(ident, name), settgs, data, data_path)

    for template in templates:
        tmpl, tmpl_path = get_template(template)
        process_project(os.path.join(ident, template), settgs, tmpl, tmpl_path)

    back_dir = os.getcwd()
    os.chdir(path)
    for script in scripts:
        path = os.path.join(data_path, os.path.split(ident)[1], script + ".py")
        print("\n--- Executing script: %s" % script)
        if not os.path.isfile(path):
            raise TemplateError(msg="Script file does not exist at {}".format(path))
        ret = subprocess.call([sys.executable, path])
        if ret != 0:
            raise TemplateError(msg="Script failed with error: {}".format(ret))
        print("--- Script executed.\n")
    os.chdir(back_dir)


def run(args):
    assert args.init_with_template

    try:
        entries = entry_points(group="fdbuild.templates")
    except TypeError:
        # Python < 3.10 fallback
        entries = entry_points()["fdbuild.templates"]

    global templates_paths
    for entry in entries:
        templates_paths += entry.load()()

    tmpl_name = args.init_with_template
    tmpl, tmpl_path = get_template(tmpl_name)

    try:
        print("Templating project...")
        process_project(tmpl_name, None, tmpl, tmpl_path)
        print("Template succesfully deployed to '%s'." % cfg.WORK_PATH)
    except FileExistsError:
        raise TemplateError(
            msg="Can not create destination folder.\n"
            "'{}' already exists.\n"
            "Templates can only be deployed to new directories.".format(cfg.WORK_PATH)
        )
    except:
        shutil.rmtree(cfg.WORK_PATH)
        raise
