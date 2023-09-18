# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

from .general import _pkg_root, __version__, __xsuite__versions__

from .register import register
from .submit import SubmitJobs

from .simulation_io import SimState, SimConfig, app_version, app_version_int
from .executable import generate_executable_source, generate_executable


# Check that the active environment has the correct pinned versions
import sys
error = ""
for mod in __xsuite__versions__.keys():
    __import__(mod)
    version = sys.modules[mod].__version__
    if version != __xsuite__versions__[mod]:
        error += f"This xboinc version ({__version__}) needs "
        error += f"{mod} {__xsuite__versions__[mod]}, "
        error +=  f"but active version is {version}!\n"
if error != "":
    raise ValueError(error)
