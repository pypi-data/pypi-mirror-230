# copyright ############################### #
# This file is part of the Xboinc Package.  #
# Copyright (c) CERN, 2023.                 #
# ######################################### #

import json
import tarfile
from pathlib import Path
import tempfile

from .user import get_domain, get_folder
from .server.eos import mv_from_eos, mv_to_eos, xrdcp_installed
from .server.tools import timestamp
from .simulation_io import SimConfig, app_version


eosdir  = '/eos/user/d/ddicroce/xboinc/'


class SubmitJobs:

    def __init__(self, user, study):
        if '__' in study:
            raise ValueError("The character sequence '__' is not allowed in 'study'!")
        self._username = user
        self._domain = get_domain(user)
        if self._domain=='eos' and not xrdcp_installed():
            raise ValueError("Error: xrdcp is not installed on your system. Cannot submit.")
        self._target = get_folder(user)
        self._studyname = study
        self._submitfile = f"{self._studyname}__{timestamp()}.tar.gz"
        self._json_files = []
        self._bin_files = []
        self._temp    = tempfile.TemporaryDirectory()
        self._tempdir = Path(temp.name).resolve()
        self._tempdir.mkdir(parents=True, exist_ok=True)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._submit()
        self._temp.cleanup()


    def add(self, *, job_name, num_turns, line, particles, checkpoint_every=-1, **kwargs):
        if '__' in job_name:
            raise ValueError("The character sequence '__' is not allowed in 'job_name'!")
        filename = f"{self._username}__{timestamp(ms=True)}"
        json_file = Path(self._tempdir, f"{filename}.json")
        bin_file  = Path(self._tempdir, f"{filename}.bin")
        kwargs['xboinc_ver'] = app_version
        json_dict = {
            'study': self._studyname,
            'user': self._username,
            'job_name': job_name,
            **kwargs
        }
        with json_file.open('w') as fid:
            json.dump(json_dict, fid)
        SimConfig.build(filename=bin_file, num_turns=num_turns, line=line,
                         particles=particles, checkpoint_every=checkpoint_every)
        self._json_files += [json_file]
        self._bin_files  += [bin_file]


    def _submit(self):
        with tarfile.open(self._tempdir / self._submitfile, "w:gz") as tar:
            for thisfile in self._json_files + self._bin_files:
                tar.add(thisfile, arcname=thisfile.name)
        if self._domain == 'eos':
            mv_to_eos(self._tempdir / self._submitfile, self._target)
        elif self._domain == 'afs':
            mv_to_afs(self._tempdir / self._submitfile, self._target)
        else:
            raise ValueError(f"Wrong domain {self._domain} for user {self._username}!")
        # TODO: check that tar contains all files
        for thisfile in self._json_files + self._bin_files:
            thisfile.unlink()

