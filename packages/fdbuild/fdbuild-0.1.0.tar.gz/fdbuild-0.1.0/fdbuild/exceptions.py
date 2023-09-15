# SPDX-FileCopyrightText: 2019 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later


class InitError(Exception):
    """Raised on a generic error when initializing the units"""

    def __init__(self, log=None, msg=None):
        super(InitError, self).__init__(msg)

        self.message = msg
        self.log = log


class TemplateError(Exception):
    """Raised on a generic error when creating templating a project"""

    def __init__(self, log=None, msg=None):
        super(TemplateError, self).__init__(msg)

        self.message = msg
        self.log = log


class WorkError(Exception):
    """Raised on a generic error when working"""

    def __init__(self, log=None, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "A work error occured"
        super(WorkError, self).__init__(msg)

        self.log = log

    def stdout(self):
        return self.log.stdout if self.log else ""

    def stderr(self):
        return self.log.stderr if self.log else ""


class StructurizeError(Exception):
    """Raised on a generic error when creating the structure"""

    def __init__(self, plugin_name="unknown", log=None, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "A structure error occured"
        super(StructurizeError, self).__init__(msg)

        self.plugin_name = plugin_name
        self.log = log


class HookError(WorkError):
    """Raised when executing a hook failed"""

    def __init__(self, post, log=None, msg=None):
        self.post = post
        super().__init__(log, msg)
