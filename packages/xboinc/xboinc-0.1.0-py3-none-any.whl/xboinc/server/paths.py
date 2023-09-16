# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

from pathlib import Path

eosdir  = Path('/','eos','user','s','sixtadm','spooldirs','xtrack') # EOS spooldir for server
dropdir = eosdir / 'drop'                                           # only location where users have write access (i.e. to register)
