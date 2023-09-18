# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import subprocess
from pathlib import Path
from time import sleep
import random

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


def afs_rm(path, is_server=False):
    try:
        path = Path(path).expanduser().resolve()
        cmd = subprocess.run(['rm', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd.returncode == 0:
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Failed afs_rm for {path}!\n{stderr}", is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed afs_rm for {path}!\n", e, is_server=is_server)
        return 1


# Always use this file by file, not for a list of files
def cp_from_afs(source, target, maximum_trials=10, wait=2.7, is_server=False):
    try:
        source = Path(source).expanduser().resolve()
        target = Path(target).expanduser().resolve()
        for i in range(maximum_trials):
            cmd = subprocess.run(['cp', source.as_posix(), target.as_posix()])
            if cmd.returncode == 0 and target.exists() and target.stat().st_size!=0:
                return 0
            if i != maximum_trials-1:
                log_debug(f"Failed to copy {str(source)} to {str(target)}!\nRetrying ({i})..", is_server=is_server)
                sleep(abs(wait+random.normalvariate(0, 0.1*wait)))
        log_error(f"Failed to copy {str(source)} to {str(target)}!", is_server=is_server)
        if not target.exists() or target.stat().st_size==0:
            log_error(f"Command succeeds but destination file is not created!", is_server=is_server)
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Command failed: {stderr}", is_server=is_server)
        log_error("\nGiving up.", is_server=is_server)
        return 1
    except Exception as e:
        log_error(f"Failed to copy {str(source)} to {str(target)}!\n", e, is_server=is_server)
        return 1

def mv_from_afs(source, target, maximum_trials=10, wait=2.7, is_server=False):
    if not cp_from_afs(source, target, maximum_trials, wait, is_server=is_server):   # returncode 0 means success
        afs_rm(source, is_server=is_server)


# Always use this file by file, not for a list of files
def cp_to_afs(source, target, maximum_trials=10, wait=2.7, is_server=False):
    try:
        source = Path(source).expanduser().resolve()
        target = Path(target).expanduser().resolve()
        for i in range(maximum_trials):
            cmd = subprocess.run(['cp', source.as_posix(), target.as_posix()])
            if cmd.returncode == 0 and target.exists() and target.stat().st_size!=0:
                return 0
            if i != maximum_trials-1:
                log_debug(f"Failed to copy {str(source)} to {str(target)}!\nRetrying ({i})..", is_server=is_server)
                sleep(abs(wait+random.normalvariate(0, 0.1*wait)))
        log_error(f"Failed to copy {str(source)} to {str(target)}!", is_server=is_server)
        if not target.exists() or target.stat().st_size==0:
            log_error(f"Command succeeds but destination file is not created!", is_server=is_server)
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Command failed: {stderr}", is_server=is_server)
        log_error("\nGiving up.", is_server=is_server)
        return 1
    except Exception as e:
        log_error(f"Failed to copy {str(source)} to {str(target)}!\n", e, is_server=is_server)
        return 1

def mv_to_afs(source, target, maximum_trials=10, wait=2.7, is_server=False):
    if not cp_to_afs(source, target, maximum_trials, wait, is_server=is_server):   # returncode 0 means success
        source.unlink()
