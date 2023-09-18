# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import json
from pathlib import Path

from .general import _pkg_root
from .user import update_user_data
from .server import server_account
from .server.paths import dropdir
from .server.eos import eos_exists, eos_rm, cp_to_eos, xrdcp_installed
from .server.afs import afs_add_acl


user_data_file = _pkg_root / 'user_data.json'


def _create_json(user, folder):
    user_file = _pkg_root / f'register_{user}.json'
    if list(folder.parents)[-2].as_posix() == '/eos':
        domain = 'eos'
    elif list(folder.parents)[-3].as_posix() == '/afs/cern.ch':
        domain = 'afs'
    else:
        raise ValueError(f"Folder {folder} not on EOS nor AFS! "
                        + "The xboinc server will not be able to reach it.")
    data = {'user': user, 'folder': folder.as_posix(), 'domain': domain}
    with user_file.open('w') as f:
        json.dump(data, f)
    return user_file, data


def _set_rights(folder, domain):
    if domain == 'eos':
        raise NotImplementedError("Ask CERN IT for explanation...")
    else:
        afs_add_acl(server_account, folder)


def register(user, folder):
    if not xrdcp_installed():
        raise ValueError("Error: xrdcp is not installed on your system. Cannot register to server.")
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Folder {folder} not found or not a folder (or no permissions)!")
    user_file, data = _create_json(user, folder)
    try:
        _set_rights(folder, data['domain'])
    except Exception as e:
        user_file.unlink()
        raise e
    if eos_exists(dropdir / user_file.name):
        eos_rm(dropdir / user_file.name)
        print("Replaced existing registration file on server dropdir.")
    if cp_to_eos(user_file, dropdir, maximum_trials=1):  # returncode 1 means error
        user_file.unlink()
        raise Exception(f"Failed to copy register file to server dropdir.\n"
                       + "Do you have permissions?\n"
                       + "If not, add yourself to the CERN xboinc-submitters egroup.")
    user_file.unlink()
    update_user_data(user, data)
