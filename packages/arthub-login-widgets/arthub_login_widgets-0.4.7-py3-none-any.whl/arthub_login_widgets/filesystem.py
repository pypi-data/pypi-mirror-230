# -*- coding: utf-8 -*-
"""The utils functions of the arthub_login_window."""

# Import built-in modules
import os

# Import third-party modules
from platformdirs import user_cache_dir


def current_path():
    return os.path.dirname(__file__)


def get_resource_file(file_name):
    root = current_path()
    return os.path.join(root, "resources", file_name)


def read_file(file_path):
    with open(file_path, "r") as file_obj:
        return file_obj.read()


def write_file(file_path, data):
    with open(file_path, "w") as file_obj:
        file_obj.write(data)


def get_login_account():
    account_file = get_account_cache_file()
    if os.path.exists(account_file):
        return read_file(account_file)


def save_login_account(account, cache_file=None):
    account_file = cache_file or get_account_cache_file()
    write_file(account_file, account)


def get_account_cache_file():
    root = user_cache_dir(appauthor="arthub", opinion=False)
    try:
        os.makedirs(root)
    # Ingoing when try create folder failed.
    except (IOError, WindowsError):
        pass
    return os.path.join(root, "arthub_account")
