# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

from pathlib import Path

_pkg_root = Path(__file__).parent.absolute()


# ==========================================================================================
# Do not change
# ==========================================================================================

__version__ = '0.1.0'

# These are the xsuite modules that are used by boinc and the versions they are tied to.
# This will be automatically updated from the active environment when making a minor release.
# If a new package needs to be pinned, add it here with a random version number,
# and similarily in the pyproject.toml
__xsuite__versions__ = {
    'xobjects' : '0.2.8',
    'xdeps'    : '0.4.2',
    'xpart'    : '0.15.3',
    'xtrack'   : '0.42.0',
    'xfields'  : '0.13.1',
    'xcoll'    : '0.2.5',
}

# ==========================================================================================
