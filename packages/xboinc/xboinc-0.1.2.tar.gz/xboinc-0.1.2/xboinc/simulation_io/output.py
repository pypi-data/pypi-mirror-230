# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

from pathlib import Path
import numpy as np

import xobjects as xo
import xpart as xp

from .version import SimVersion

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

