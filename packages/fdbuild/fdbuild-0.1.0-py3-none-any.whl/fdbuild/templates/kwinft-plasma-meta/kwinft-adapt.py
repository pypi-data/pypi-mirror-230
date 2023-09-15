#!/usr/bin/env python

# SPDX-FileCopyrightText: 2021 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Initiates KDE structure and adapts it to KWinFT template usage.
"""

import fileinput, os, subprocess, yaml


def main():
    print("Switching to the kde subdirectory.")
    os.chdir("kde")

    print("Calling fdbuild --only-structure --noconfirm")
    ret = subprocess.call(["fdbuild", "--only-structure", "--noconfirm"])
    if ret != 0:
        return ret

    print("Disabling kde structurizer.")
    settgs = "fdbuild.yaml"
    with open(settgs, "r") as file:
        content = yaml.safe_load(file)
        content["structure"]["enabled"] = False

    with open(settgs, "w") as file:
        yaml.dump(content, file)

    print("Commenting out kscreen entry.")
    for line in fileinput.input(settgs, inplace=1):
        line = line.replace("- kscreen\n", "#- kscreen\n")
        print(line, end="")


if __name__ == "__main__":
    main()
