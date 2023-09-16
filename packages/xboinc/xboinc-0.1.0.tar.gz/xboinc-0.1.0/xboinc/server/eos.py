# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import os, subprocess
from pathlib import Path
from time import sleep
import random

from .tools import log_debug, log_info, log_error


# Functions to work with the EOS file system
# ==========================================
EOS_MGM_URL = 'root://eosuser.cern.ch'
eos_env = {**os.environ, 'EOS_MGM_URL': EOS_MGM_URL}


def is_xrdcp_installed():
    try:
        # Run the xrdcp command with the "--version" flag to check if it's installed
        cmd = subprocess.run(["xrdcp", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        # xrdcp is not installed or returned an error
        return False


def _eos_path(path):
    path = Path(path).expanduser().resolve()
    return path.as_posix().replace('home-','user/')

def _xrd_path(path):
    path = Path(path).expanduser().resolve()
    return EOS_MGM_URL + '/' + _eos_path(path)

def eos_glob(pattern, path, is_server=False):
    try:
        path = Path(path).expanduser().resolve()
        cmd = subprocess.run(['eos', 'find', '-name', pattern, _eos_path(path)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=eos_env)
        if cmd.returncode != 0 or cmd.stdout == b'':
            return []
        files = [Path(ss).resolve() for ss in cmd.stdout.decode('UTF-8').strip().split('\n')]
        return [f for f in files if f.stat().st_size!=0]
    except Exception as e:
        log_error(f"Failed eos_glob {pattern} in {path}!\n", e, is_server=is_server)
        return []

def eos_exists(path, is_server=False):
    try:
        path = Path(path).expanduser().resolve()
        cmd = subprocess.run(['eos', 'find', '-name', path.name, _eos_path(path.parent)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=eos_env)
        if cmd.returncode != 0 or cmd.stdout == b'':
            return False
        return Path(cmd.stdout.decode('UTF-8').strip()).resolve().stat().st_size!=0
    except Exception as e:
        log_error(f"Failed eos_exists for {path}!\n", e, is_server=is_server)
        return False

def eos_rm(path, is_server=False):
    try:
        path = Path(path).expanduser().resolve()
        cmd = subprocess.run(['eos', 'rm', _eos_path(path)], stdout=subprocess.PIPE, env=eos_env)
        if cmd.returncode == 0:
            return 0
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Failed eos_rm for {path}!\n{stderr}", is_server=is_server)
            return 1
    except Exception as e:
        log_error(f"Failed eos_rm for {path}!\n", e, is_server=is_server)
        return 1


# Always use this file by file, not for a list of files
def cp_from_eos(source, target, maximum_trials=10, wait=2.7, is_server=False):
    try:
        target = Path(target).expanduser().resolve()
        for i in range(maximum_trials):
            cmd = subprocess.run(['xrdcp', '--cksum', 'adler32', _eos_path(source), target.as_posix()], env=eos_env)
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

def mv_from_eos(source, target, maximum_trials=10, wait=2.7, is_server=False):
    if not cp_from_eos(source, target, maximum_trials, wait, is_server=is_server):   # returncode 0 means success
        eos_rm(source, is_server=is_server)


# Always use this file by file, not for a list of files
def cp_to_eos(source, target, maximum_trials=10, wait=2.7, is_server=False):
    try:
        source = Path(source).expanduser().resolve()
        target = Path(target, source.name).expanduser().resolve()
#         target = Path(target).expanduser().resolve()
        for i in range(maximum_trials):
            cmd = subprocess.run(['xrdcp', '--cksum', 'adler32', source.as_posix(), _eos_path(target)], env=eos_env)
            if cmd.returncode == 0 and eos_exists(target):
                return 0
            if i != maximum_trials-1:
                log_debug(f"Failed to copy {str(source)} to {str(target)}!\nRetrying ({i})..", is_server=is_server)
                sleep(abs(wait+random.normalvariate(0, 0.1*wait)))
        log_error(f"Failed to copy {str(source)} to {str(target)}!", is_server=is_server)
        if not eos_exists(target):
            log_error(f"Command succeeds but destination file is not created!", is_server=is_server)
        else:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            log_error(f"Command failed: {stderr}", is_server=is_server)
        log_error("\nGiving up.", is_server=is_server)
        return 1
    except Exception as e:
        log_error(f"Failed to copy {str(source)} to {str(target)}!\n", e, is_server=is_server)
        return 1

def mv_to_eos(source, target, maximum_trials=10, wait=2.7, is_server=False):
    if not cp_to_eos(source, target, maximum_trials, wait, is_server=is_server):   # returncode 0 means success
        source.unlink()
