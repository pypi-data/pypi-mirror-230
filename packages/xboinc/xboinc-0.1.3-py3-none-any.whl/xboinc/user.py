# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import json
from pathlib import Path

from .general import _pkg_root


user_data_file = _pkg_root / 'user_data.json'
if not user_data_file.exists():
    with user_data_file.open('w') as fid:
        json.dump({}, fid)


def update_user_data(user, data):
    with user_data_file.open('r') as fid:
        userdict = json.load(fid)
    data.pop('user', None)
    if user in userdict:
        userdict[user].update(data)
    else:
        userdict[user] = data
    with user_data_file.open('w') as fid:
        json.dump(userdict, fid)

def get_user_data(user):
    with user_data_file.open('r') as fid:
        userdict = json.load(fid)
    return userdict[user]

def get_folder(user):
    return Path(get_user_data(user)['folder']).resolve()

def get_domain(user):
    return get_user_data(user)['domain']

def remove_user(user):
    with user_data_file.open('r') as fid:
        userdict = json.load(fid)
    if user in userdict:
        userdict.pop(user)
        with user_data_file.open('w') as fid:
            json.dump(userdict, fid)
    
