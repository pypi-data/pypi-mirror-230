# SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from importlib.metadata import entry_points

from .exceptions import *


def get_plugin(name, group):
    try:
        entries = entry_points(group="fdbuild." + group)
    except TypeError:
        # Python < 3.10 fallback
        entries = entry_points()["fdbuild." + group]

    for entry in entries:
        if entry.name == name:
            return entry.load()

    raise InitError(None, "Plugin group '%s' does not provide '%s'." % (group, name))


def get_stage(name, step):
    assert step
    return get_plugin(name, "stages")(step)


def get_step(stage, name, step):
    return get_plugin(name, "steps")(step)


def create_structure(name, structurizer):
    return get_plugin(name, "structurizers")(structurizer)
