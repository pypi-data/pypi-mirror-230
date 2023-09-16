import json
import tarfile
from pathlib import Path
import tempfile
import datetime

from .eos import mv_from_eos, mv_to_eos
from .sim_data import build_input_file
from .default_tracker import get_default_tracker

temp    = tempfile.TemporaryDirectory()
tempdir = Path(temp.name).resolve()
eosdir  = '/eos/user/d/ddicroce/xboinc/'

def timestamp(ms=False):
    ms = -3 if ms else -7
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:ms]

class SubmitJobs:

    def __init__(self, user, study):
        if '__' in study:
            raise ValueError("The character sequence '__' is not allowed in 'study'!")
        self._username = user
        self._studyname = study
        self._submitfile = f"{self._studyname}__{timestamp()}.tar.gz"
        self._json_files = []
        self._bin_files = []
        tempdir.mkdir(parents=True, exist_ok=True)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._submit()
        temp.cleanup()

    def add(self, *, job_name, num_turns, line, particles, checkpoint_every=-1):
        if '__' in job_name:
            raise ValueError("The character sequence '__' is not allowed in 'job_name'!")
        filename = f"{self._username}__{timestamp(ms=True)}"
        json_file = Path(tempdir, f"{filename}.json")
        bin_file  = Path(tempdir, f"{filename}.bin")
        json_dict = {'study': self._studyname, 'user': self._username, 'job_name': job_name}
        with open(json_file, 'w') as fid:
            json.dump(json_dict, fid)
        build_input_file(name=bin_file, num_turns=num_turns, line=line,
                         particles=particles, checkpoint_every=checkpoint_every)
        self._json_files += [json_file]
        self._bin_files  += [bin_file]

    def _submit(self):
        with tarfile.open(tempdir / self._submitfile, "w:gz") as tar:
            for thisfile in self._json_files + self._bin_files:
                tar.add(thisfile, arcname=thisfile.name)
        mv_to_eos(tempdir / self._submitfile, eosdir)
        # TODO: check that tar contains all files
        for thisfile in self._json_files + self._bin_files:
            thisfile.unlink()

