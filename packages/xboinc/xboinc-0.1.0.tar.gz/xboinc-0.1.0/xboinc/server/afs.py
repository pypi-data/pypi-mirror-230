# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import subprocess
from pathlib import Path

from .tools import log_debug, log_info, log_error


def afs_add_acl(user, folder, acl='rlwik', is_server=False):
    try:
        folder = Path(folder).resolve()
        if folder.is_dir():
            cmd = subprocess.run(['fs', 'sa', folder, user, acl],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd.returncode == 0:
                log_info(f"Set ACL '{acl}' on folder {folder} for user {user}.", is_server=is_server)
                return 0
            else:
                stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
                log_error(f"Failed to set ACL '{acl}' on {folder} for user {user}.\n{stderr}", is_server=is_server)
                return 1
        else:
            log_error(f"Folder {folder} not found. Do you have access permissions?", is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to set ACL '{acl}' on {folder} for user {user}.\n{stderr}", e, is_server=is_server)
        return 1


def afs_remove_acl(user, folder, is_server=False):
    try:
        folder = Path(folder).resolve()
        if folder.is_dir():
            cmd = subprocess.run(['fs', 'sa', folder, user, 'none'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd.returncode == 0:
                log_info(f"Removed ACL on folder {folder} for user {user}.", is_server=is_server)
                return 0
            else:
                stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
                log_error(f"Failed to remove ACL on {folder} for user {user}.\n{stderr}", is_server=is_server)
                return 1
        else:
            log_error(f"Folder {folder} not found. Do you have access permissions?", is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to remove ACL on {folder} for user {user}.\n{stderr}", e, is_server=is_server)
        return 1


def afs_print_acl(folder, is_server=False):
    try:
        folder = Path(folder).resolve()
        if folder.is_dir():
            cmd = subprocess.run(['fs', 'la', folder],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd.returncode == 0:
                stdout = cmd.stdout.decode('UTF-8').strip().split('\n')
                log_info(f"{stdout}", is_server=is_server)
                return 0
            else:
                stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
                log_error(f"Failed to remove ACL on {folder} for user {user}.\n{stderr}", is_server=is_server)
                return 1
        else:
            log_error(f"Folder {folder} not found. Do you have access permissions?", is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed to remove ACL on {folder} for user {user}.\n{stderr}", e, is_server=is_server)
        return 1

