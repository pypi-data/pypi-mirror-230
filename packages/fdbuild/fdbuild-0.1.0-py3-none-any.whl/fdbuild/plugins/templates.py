# SPDX-FileCopyrightText: 2022 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import os


def paths():
    return [os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")]
