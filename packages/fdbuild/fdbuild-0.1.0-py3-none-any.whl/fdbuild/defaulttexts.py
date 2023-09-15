# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later


def projectsettings():
    return """#
# Project settings file for FDbuild
#
# This file defines a FDBuild project in the directory it is
# located in. Its settings are applied to subprojects, but
# they can overwrite specific values in their own setting files,
# which then apply to all further sub-projects and modules in
# their directory hierarchy.
#
# To reset the setting values here, delete this file. The file
# will be regenerated the next time you run FDbuild.
#

# list subprojects - uninducible
# list only '/': all subdirectories
projects:
  - /

# environment variables to be set while working on this project
# envvars:
  # VAR_NAME:
    # value: VAR_VALUE
    # prepend: false # prepend instead of replace - optional (default: false)

source:
  plugin: git
  # url to pull source updates from - uninducible
  origin: https://gitlab.com/kwinft/kwinft.git

configure:
  plugin: cmake
  options:

build:
  plugin: ninja
  threads: max

install:
  path: /usr/local
  sudo: false
"""
