#!/usr/bin/env python

# SPDX-FileCopyrightText: 2021 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Initiates KDE structure and adapts it to KWinFT template usage.
"""

import os, shutil


def main():
    src_path = os.path.dirname(os.path.realpath(__file__))
    dst_path = os.getcwd()
    print("Copying 'meson-cross-file' from:\n  {}\nto:\n  {}".format(src_path, dst_path))
    shutil.copy(os.path.join(src_path, "meson-cross-file"), dst_path)


if __name__ == "__main__":
    main()
