# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fdbuild import stage


class Plugin(stage.Stage):
    def __init__(self, step):
        super().__init__("source", step)
        self.directory = self.identifier
