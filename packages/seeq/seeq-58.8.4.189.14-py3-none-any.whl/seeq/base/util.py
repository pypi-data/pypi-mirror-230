from __future__ import annotations

import os
import re
import sys
import tempfile
import time
import warnings
from inspect import stack


def remove_regex_capture_group_names(regex):
    # PostgreSQL will choke on named capture groups
    return re.sub(r'\?<\w+>', '', regex)


def pythonize_regex_capture_group_names(regex):
    # Unlike standard regex syntax, Python capture groups have a capital P:  (?P<group_name>.*?)
    return re.sub(r'\?<(\w+)>', r'?P<\1>', regex)


def replace_tokens_in_regex(regex, group_dict, escape=True):
    for name, value in group_dict.items():
        regex = regex.replace('${%s}' % name, re.escape(value) if escape else value)

    return regex


def os_lock(name, target, args=(), kwargs=None, timeout=7.0, retry_period=0.1):
    """
    Adapted from https://github.com/ses4j/backup/blob/master/oslockedaction.py
    To use, just wrap your python call with an os_lock() call.  Instead of:
    >>> time.sleep(5.0)
    Do:
    >>> os_lock(name="mylock", target=time.sleep, args=(5.0,))
    Nobody else using the same lockfile will be able to run at the same time.
    If timeout is None, it will never timeout if the lockfile exists.
    Otherwise it will just try to remove the lockfile after "timeout" seconds and do 'action()' anyway.
    retry_period is a float in seconds to wait between retries.
    """
    lockfile = os.path.abspath(os.path.join(tempfile.tempdir, f'{name}.lock'))

    f = None
    started_at = time.time()
    kwargs = dict() if kwargs is None else kwargs

    try:
        while True:
            if timeout is not None and time.time() > started_at + timeout:
                # timed out, it must be stale... (i hope)  so remove it.

                if time.time() > (started_at + (timeout * 2)):
                    raise RuntimeError(f"FAIL: os_lock() can't acquire directory lock, because {lockfile} was not "
                                       "cleaned up. Delete it manually if the process is finished.")

                try:
                    os.remove(lockfile)
                except OSError:
                    time.sleep(retry_period)
                    continue

            try:
                f = os.open(lockfile, os.O_RDWR | os.O_CREAT | os.O_EXCL)
                os.write(f, bytes(f'{str(__file__)} made this, called from {sys.argv[0]}', encoding='utf-8'))
                break
            except OSError:
                time.sleep(retry_period)

        target(*args, **kwargs)
    finally:
        if f:
            os.close(f)
            os.remove(lockfile)


def deprecation_warning(message, *, stack_index=2):
    frame_info = stack()
    if len(frame_info) > stack_index:
        warnings.warn(
            f'{message} (from line {frame_info[stack_index].lineno} in file "{frame_info[stack_index].filename}")')
    else:
        warnings.warn(message)


def get_platform():
    import platform
    plat = platform.platform()
    if plat.lower().find('windows') != -1:
        return 'windows'
    if plat.lower().find('linux') != -1:
        return 'linux'
    if plat.lower().find('darwin') != -1 or plat.lower().find('macos') != -1:
        return 'osx'


def is_windows():
    return get_platform() == 'windows'


def is_linux():
    return get_platform() == 'linux'


def is_osx():
    return get_platform() == 'osx'


def is_osx_aarch64():
    import platform
    return get_platform() == 'osx' and platform.platform().lower().find('arm64') != -1


def get_home_dir(user=None):
    if is_windows():
        home = os.environ['USERPROFILE']
    else:
        user_to_expand = user if user else ''
        home = os.path.expanduser(f'~{user_to_expand}')

    return home


def get_test_with_file():
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'sdk', 'test-with.txt'))


def get_test_with_root_dir():
    test_with_file = get_test_with_file()
    test_with = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    if os.path.exists(test_with_file):
        with open(test_with_file, 'r') as f:
            lines = f.readlines()
            test_with = lines[0]

    return test_with


def do_with_retry(func, timeout_sec=5, retry_sleep_sec=0.1):
    import time
    timer = time.time()
    while True:
        # noinspection PyBroadException
        try:
            func()
            break
        except BaseException:
            if time.time() - timer > timeout_sec:
                raise

            time.sleep(retry_sleep_sec)


def cleanse_filename(filename, replacement_char='_'):
    return re.sub(r'[:"%\\/<>^|?*&\[\]]', replacement_char, filename)
