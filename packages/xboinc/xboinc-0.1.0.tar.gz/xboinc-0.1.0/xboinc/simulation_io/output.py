# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import sys
from pathlib import Path
import numpy as np

import xobjects as xo
import xpart as xp

from ..general import __version__


# XXX.YYY.ZZZ to XXXYYYZZZ
def _version_to_int(version):
    vers = version.split('.')
    return int(vers[0])*1000000 + int(vers[1])*1000 + int(vers[2])

# XXXYYYZZZ to XXX.YYY.ZZZ
def _int_to_version(verint):
    XXX = int(verint / 1000000)
    YYY = int((verint - XXX*1000000)/1000)
    ZZZ = int(verint - XXX*1000000 - YYY*1000)
    return f"{XXX}.{YYY}.{ZZZ}"


# This class overloads the first field from the SimState,
# in order to read the correct version from the binary
class SimVersion(xo.HybridClass):
    _xofields = {
        'xboinc_version':   xo.Int64,    # version XXX.YYY.ZZZ as int
    }

    def __init__(self, **kwargs):
        if '_xobject' not in kwargs:
            kwargs['xboinc_version'] = _version_to_int(__version__)
        super().__init__(**kwargs)

    def assert_version(self):
        if int(_version_to_int(__version__)/1000) != int(self.xboinc_version/1000):
            error += f"Incompatible xboinc version! Output file needs "
            error +  f"{_int_to_version(self.xboinc_version)}, "
            error +  f"but current version is {__version__}.\n"
            raise ValueError(error)


class SimState(xo.HybridClass):
    _xofields = {
        'version':   SimVersion,    # This HAS to be the first field!
        'i_turn':    xo.Int64,
        'size':      xo.Int64,
        'particles': xp.Particles,
    }

    def __init__(self, **kwargs):
        if '_xobject' not in kwargs:
            kwargs['version'] = SimVersion()
        # TODO: can we set size at construction?
        super().__init__(**kwargs)

    @classmethod
    def from_binary(cls, filename, offset=0):
        # Read binary
        filename = Path(filename)
        with filename.open('rb') as fid:
            state_bytes = fid.read()
        buffer_data = xo.ContextCpu().new_buffer(capacity=len(state_bytes))
        buffer_data.buffer[:] = np.frombuffer(state_bytes, dtype=np.int8)
        # Cast to SimVersion to verify versions of xsuite packages
        version_offset = -1
        for field in cls._XoStruct._fields:
            if field.name == 'version':
                version_offset = field.offset
        if version_offset == -1:
            raise ValueError("No xofield 'version' found in SimState!")
        sim_ver_xobject = SimVersion._XoStruct._from_buffer(buffer=buffer_data, offset=offset+version_offset)
        sim_ver = SimVersion(_xobject=sim_ver_xobject)
        sim_ver.assert_version()
        # Retrieve simulation state
        sim_state_xobject = cls._XoStruct._from_buffer(buffer=buffer_data, offset=offset)
        sim_state_out = cls(_xobject=sim_state_xobject)
        return sim_state_out

