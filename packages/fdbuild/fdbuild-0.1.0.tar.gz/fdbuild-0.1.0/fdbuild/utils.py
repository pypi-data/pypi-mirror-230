# SPDX-FileCopyrightText: 2018 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import errno, os, sys, time, threading

from subprocess import call, Popen, PIPE
from select import select


class tcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLUEBACK = "\033[44m"


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def set_env_var(var, val, prepend):
    if not val:
        # No value to set.
        if not prepend:
            # In this case remove the variable from the environment.
            try:
                os.environ.pop(var)
            except KeyError:
                pass
        return

    if prepend:
        try:
            cur_val = os.environ[var]
            os.environ[var] = val + ":" + cur_val
            return
        except KeyError:
            # Variable not in environment. Just fall back to setting it directly.
            pass

    # Not to prepend or variable not yet in environment.
    os.environ[var] = val


def set_env_vars(dictionary):
    for key, obj in dictionary.items():
        set_env_var(key, obj["value"], obj["prepend"])


def read_and_set_env_var(var, val, prepend):
    try:
        old_value = os.environ[var]
    except KeyError:
        old_value = ""

    set_env_var(var, val, prepend)
    return old_value


def read_and_set_pkgcfg_path(dic):
    var_name = "PKG_CONFIG_PATH"
    old_val = os.environ[var_name] if var_name in os.environ else ""

    if "pkg-config" not in dic:
        return old_val

    pkgcfg = dic["pkg-config"]
    if "path" not in pkgcfg:
        return old_val

    return read_and_set_env_var(
        var_name, pkgcfg["path"], pkgcfg["prepend"] if "prepend" in pkgcfg else True
    )


def reset_pkgcfg_path(value):
    read_and_set_pkgcfg_path({"pkg-config": {"path": value, "prepend": False}})


def sudo_make_dir(path):
    try:
        call(["sudo", "mkdir -p " + path])
    except OSError as exc:
        print(
            "Error 'sudo mkdir -p "
            + path
            + "': "
            + os.strerror(exc.errno)
            + " ("
            + str(exc.errno)
            + ")"
        )
        raise


def make_dir(path, retry_with_sudo=False):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        print(
            "Error creating " + path + ": " + os.strerror(exc.errno) + " (" + str(exc.errno) + ")"
        )

        if exc.errno == errno.EACCES:
            if retry_with_sudo:
                sudo_make_dir(path)
            pass
        else:
            raise


def create_symlink(src, lnk):
    if src == lnk:
        # lnk equals src --> no need to link
        return

    try:
        os.symlink(src, lnk)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.islink(lnk) and os.readlink(lnk) == src:
            if os.path.islink(lnk) and os.readlink(lnk) == src:
                # symlink exists already and points to correct src
                pass
            else:
                raise
        else:
            raise


def decode_text(output):
    try:
        data = output.decode()
    except (UnicodeDecodeError, AttributeError):
        # Try as string.
        data = output

    return data if isinstance(data, str) else ""


def run_process(command, log, get_percentage=None, indepedent_indicator=False, shell=False):
    had_percentage = False

    def write_out_line_with_percentage(line):
        nonlocal had_percentage
        percentage = get_percentage(line)
        # TODO: This is a phony check. We might have some lines being None but overall still
        #       receiving percentages. We need to change this once we can rely on the configure step
        #       internally setting the build step.
        if percentage is None and not had_percentage:
            log.animate()
        elif percentage:
            had_percentage = True
            log.progress(percentage)
        write_out_line(line)

    def write_out_line(line):
        log.animate()
        log.out(line)

    def write_err_line(line):
        nonlocal had_percentage
        if not had_percentage:
            log.animate()
        log.err(line)

    if get_percentage:
        out_fct = write_out_line_with_percentage
    else:
        out_fct = write_out_line

    def run():
        return run_logged_process(command, out_fct, write_err_line, shell)

    if indepedent_indicator and not get_percentage:
        cnt = True

        def threaded_animate():
            while cnt:
                log.animate()
                time.sleep(0.1)

        thread = threading.Thread(target=threaded_animate)
        thread.start()
        ret = run()
        cnt = False
        thread.join()
        return ret

    return run()


#
# Below allows to read in stdout and stderr at the same time
# in parallel to the process execution with separate targets
# for stdout and stderr.
# Credit: https://stackoverflow.com/questions/31926470#31953436
def run_logged_process(command, writeOutputLine, writeErrorLine, shell=False):
    """Reads in stdout and stderr at the same time in parallel to the process execution
    with separate targets for stdout and stderr.
    Credit: https://stackoverflow.com/questions/31926470#31953436
    """
    cmd = ["stdbuf", "-oL", "-e0"] + command
    if shell:
        cmd = " ".join(cmd)

    with Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell) as p1:
        out_line_buffer = ""
        err_line_buffer = ""

        def write(data, writer):
            if data == None:
                if writer[1]:
                    writer[0](writer[1] + "\n")
                return

            text = decode_text(data)
            while "\n" in text:
                splitted = text.split("\n", 1)

                writer[0](writer[1] + splitted[0] + "\n")
                writer[1] = ""

                if len(splitted) > 1:
                    text = splitted[1]
                else:
                    text = ""

            writer[1] += text

        readable = {
            p1.stdout.fileno(): [writeOutputLine, out_line_buffer],
            p1.stderr.fileno(): [writeErrorLine, err_line_buffer],
        }

        while readable:
            for fd in select(readable, [], [])[0]:
                # Select on fds.
                data = os.read(fd, 1024)
                if not data:
                    # EOF
                    write(None, readable[fd])
                    del readable[fd]
                else:
                    write(data, readable[fd])

        p1.communicate()
        return p1.returncode


def get_idents(idents, errors, bogus_parts=[], bogus_sections=[]):
    idents_cp = [i for i in idents]
    idents.clear()
    errors.clear()

    # idents are not allowed to have whitespaces
    # and colons
    bogus_parts = [" ", ":"] + bogus_parts

    for i in idents_cp:

        def has_reserved_name(i, r):
            if i == r:
                return True
            if i.endswith(os.sep + r):
                return True
            if i.startswith(r + os.sep):
                return True
            if i.find(os.sep + r + os.sep) != -1:
                return True
            return False

        if not i:
            # ignore empty values
            continue

        with_error = False
        for part in bogus_parts:
            if part in i:
                errors.append((i, part))
                with_error = True

        for section in bogus_sections:
            if has_reserved_name(i, section):
                errors.append((i, section))
                with_error = True

        if not with_error:
            idents.append(i)

    return errors == []


def get_prjs_names(prjs, errors, bogus_chars=[]):
    return get_idents(prjs, errors, bogus_chars, ["src", "build"])


def get_mdls_names(mdls, errors):
    return get_idents(mdls, errors)


def exit(ret):
    show_cursor()
    if ret != 0:
        print("\nAborting...")
        sys.exit(ret)
    else:
        sys.exit(0)
