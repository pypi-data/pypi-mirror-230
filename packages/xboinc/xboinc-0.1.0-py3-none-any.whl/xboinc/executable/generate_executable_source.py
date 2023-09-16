# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import xobjects as xo
from ..simulation_io import SimState, SimConfig, SimVersion, get_default_tracker
from ..general import _pkg_root, __version__

from pathlib import Path
import shutil
import subprocess

# ===============================================================================================
# IMPORTANT
# ===============================================================================================
# Only make changes to this file just before a minor version bump (need a separate commit though)
# to avoid having multiple xboinc versions with out-of-sync executables.
# ===============================================================================================

insert_in_all_files = """
#include <stdio.h>
#ifndef NULL
    #define NULL 0
#endif
"""

def generate_executable_source(write_source_files=True,
                                       _context=None):
    assert _context is None
    assert write_source_files

    sim_config_sources = [
        insert_in_all_files,
        xo.specialize_source(SimVersion._XoStruct._gen_c_api().source,
                                    specialize_for='cpu_serial'),
        xo.specialize_source(SimState._XoStruct._gen_c_api().source,
                                    specialize_for='cpu_serial'),
        xo.specialize_source(SimConfig._gen_c_api().source,
                                    specialize_for='cpu_serial'),
    ]

    sim_config_h = '\n'.join(sim_config_sources)

    default_tracker, default_config_hash = get_default_tracker()
    track_kernel = default_tracker.track_kernel[default_config_hash]
    xtrack_tracker_h = (
        insert_in_all_files + track_kernel.specialized_source)

    with open(_pkg_root.joinpath('executable/main.c'), 'r') as fid:
        main_c = insert_in_all_files + fid.read()

    dct_sources = {
        'sim_config.h': sim_config_h,
        'xtrack_tracker.h': xtrack_tracker_h,
        'main.c': main_c,
    }

    for nn, vv in dct_sources.items():
        file = Path.cwd() / nn
        with file.open('w') as fid:
            fid.write(vv)

    return dct_sources


def generate_executable(keep_source=False):
    main    = Path.cwd() / "main.c"
    config  = Path.cwd() / "sim_config.h"
    tracker = Path.cwd() / "xtrack_tracker.h"
    if not main.exists() or not config.exists() or not tracker.exists():
        source_files = generate_executable_source()

    if shutil.which("gcc") is not None:
        compiler = "gcc"
    elif shutil.which("clang") is not None:
        compiler = "clang"
    else:
        raise RuntimeError("Neither clang or gcc are found. Install a C compiler.")

    tag = '_'
    tag += '.'.join(__version__.split('.')[:2])
    cmd = subprocess.run(['uname', '-ps'], stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        tag += '-' + cmd.stdout.decode('UTF-8').strip().lower().replace(' ','-')
    cmd = subprocess.run([compiler, 'main.c', '-o', f'xboinc{tag}', '-lm'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cmd.returncode != 0:
        stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
        raise RuntimeError(f"Compilation failed. Stderr:\n {stderr}")

    if keep_source:
        main.rename(main.parent / f'{main.stem}{tag}{main.suffix}')
        config.rename(config.parent / f'{config.stem}{tag}{config.suffix}')
        tracker.rename(tracker.parent / f'{tracker.stem}{tag}{tracker.suffix}')
    else:
        main.unlink()
        config.unlink()
        tracker.unlink()
