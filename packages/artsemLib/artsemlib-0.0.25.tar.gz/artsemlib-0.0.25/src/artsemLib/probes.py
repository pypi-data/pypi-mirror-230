import logging
import os.path
from subprocess import call as _subprocess_call
from os import path as _os_path, walk as _os_walk
from yaml import safe_load as _yaml_safe_load
from pandas import DataFrame as _DataFrame, Series as _Series
from checksumdir import dirhash


def filehash(fpath):
    from hashlib import md5, sha1, sha256
    try:
        with open(fpath, 'rb') as _file:
            _fcontent = _file.read()
            return {
                'md5': md5(_fcontent).hexdigest(),
                'sha1': sha1(_fcontent).hexdigest(),
                'sha256': sha256(_fcontent).hexdigest()
            }
    except FileNotFoundError:
        logging.warning(f"The target file is not found ({fpath})")
        return {'md5': '', 'sha1': '', 'sha256': ''}


class Subject:

    def __init__(self, fpath):
        if not Subject.validate_path(fpath):
            raise ValueError(f"Not an ELF {fpath}")
        self.path = fpath
        self.hash = filehash(fpath)

    @staticmethod
    def validate_path(fpath):
        # TODO: assert is elf file
        return _os_path.isfile(fpath)

    @property
    def filename(self):
        return _os_path.basename(self.path)

    def __repr__(self):
        return self.filename

    def to_json(self):
        # Exclude self.hash. Computed when the instance is initialized
        return {'path': self.path, 'hash': self.hash}


class Probe:
    __return_codes__ = {
        'positive': 0,
        'negative': 1,
        'fail': 2,
        'undetermined': 3,
        'undefined': 4
    }

    def __init__(self, dirpath):
        if not Probe.validate_probe_structure(dirpath):
            raise ValueError("Not parser directory. Missing 'main.py' and/or .conf file")
        self.root_dir = dirpath
        with open(_os_path.join(dirpath, '.conf'), 'r') as pbconffile:
            self.conf = _yaml_safe_load(pbconffile)
            self.conf.update({'sha256': dirhash(_os_path.dirname(dirpath), "sha256")})

    @property
    def name(self):
        return _os_path.basename(self.root_dir)

    @property
    def exec_path(self):
        return _os_path.abspath(_os_path.join(self.root_dir, 'main.py'))

    def __repr__(self):
        return f"{self.name} ({self.conf.get('id')})"

    @staticmethod
    def validate_probe_structure(dirpath) -> bool:
        """

        :param dirpath: Dir path pointing to a probe dir
        :return: True if dirpath points to a valid probe dir. False otherwise
        """
        return _os_path.isfile(_os_path.join(dirpath, 'main.py')) and _os_path.isfile(_os_path.join(dirpath, '.conf'))

    def run(self, target_path) -> int:
        """Execute this probe on a target
        Prepares the environment to execute the probe, then runs it, and finally validates the result


        :param target_path: path to the file to be analyzed
        :return: an integer number. Check the docs for more info about return codes
        """

        def validate_result(res: int) -> tuple[str, int]:
            if str(res) not in Probe.__return_codes__.values():
                # return Probe.__return_codes__.get('undefined'), 'undefined'
                # return 'undefined', int(Probe.__return_codes__['undefined'])
                _filter = lambda k, v: k == 'undefined'
                # return next(filter(lambda k, v: k == 'undefined', Probe.__return_codes__.items()))[0]
            else:
                # _bound = max(res, len(Probe.__return_codes__) - 1)
                # _valid = next(filter(lambda k, v: v == res, Probe.__return_codes__.items()))[0]
                # return res, Probe.__return_codes__.get(str(res))
                _filter = lambda k, v: v == res
            return next(filter(_filter, Probe.__return_codes__.items()))[0]
            # return _valid[1], _valid[0]

        # Execute the probe and validate the result
        logging.info(f"Executing probe '{self.name}' on target '{target_path}'")
        ret = _subprocess_call(f"{self.exec_path} {target_path}", shell=True)
        _validated_res = validate_result(ret)
        logging.info(f"Probe '{self.name}' {_validated_res[0]} ({ret})")
        return _validated_res[1]

    def parse_cli(self, cmd=None):
        import argparse
        parser = argparse.ArgumentParser(
            prog=_os_path.join(self.name, 'main.py'),
            description=self.conf.get('description')
        )
        parser.add_argument('target', help="Path to target (ELF) file to be analyzed")
        _args = parser.parse_args(cmd)
        _args.__setattr__('probe_conf', self.conf)
        return _args


class AnalysisMatrix:

    def __init__(self):
        self.matrix = _DataFrame(columns=['Probe'])

    def count_probes(self):
        return self.matrix.shape[0]

    def count_targets(self):
        return self.matrix.shape[1] - 1

    def load_subjects(self, subj_list: list):
        if not isinstance(subj_list, list):
            raise TypeError(f"Unexpected type ({type(subj_list)}) for param 'subj_list'. Expected: list")
        for fpath in subj_list:
            try:
                # Add column 'Subject' at the end of the matrix
                self.matrix.insert(
                    self.matrix.shape[1],
                    Subject(fpath),
                    _Series(["Pending"] * self.count_probes()),
                    False)
            except ValueError:
                logging.error(f"Not an ELF {fpath}. Skipping this target")

    def add_probe(self, pb_path):
        if not Probe.validate_probe_structure(pb_path):
            logging.error(f"Not a Probe directory ({pb_path})")
            return
        self.matrix.loc[len(self.matrix)] = [Probe(pb_path)]

    def load_probes(self, prob_list: list):
        if not isinstance(prob_list, list):
            raise TypeError(f"Unexpected type ({type(prob_list)}) for param 'subj_list'. Expected: list")
        # Iterate (absolute path) entries in this directory and filter by the sub-files included in it
        logging.info("Loading probes")
        for i in filter(Probe.validate_probe_structure, prob_list):
            try:
                self.add_probe(i)
            except ValueError:
                continue
        logging.info(f"({self.count_probes()}) Probes loaded: {[x.name for x in self.matrix['Probe']]}")

    def load_probes_from_dir(self, dirpath):
        # https://stackoverflow.com/questions/141291/how-to-list-only-top-level-directories-in-python
        self.load_probes([os.path.join(dirpath, d) for d in next(_os_walk(dirpath))[1]])

    def full_load(self, probes, subj_list):
        if isinstance(probes, list):
            self.load_probes(probes)
        elif _os_path.isdir(probes):
            self.load_probes_from_dir(probes)
        else:
            raise ValueError(f"Unexpected value for param 'probes'. Expected: list, dir-path")
        self.load_subjects(subj_list)

    def analyze(self, include=None, exclude=None):
        # TODO: run all the corresponding probe
        # TODO: apply parallelism. The computations of each item are independent from the rest
        """
        Analyze the current Matrix
        :param include: If not None, only those Probe IDs within the list will be executed
        :param exclude: If not None, only those Probe IDs NOT IN this list are executed
        :return: None
        """
        for tg in self.matrix.columns[1:]:
            for y_coord, probe in enumerate(self.matrix["Probe"]):
                if (include is not None and probe.id in include) or (exclude is not None and probe.id not in exclude):
                    self.matrix.at[y_coord, tg] = probe.run(tg)
                    print('-' * 25)
                elif include is not None or exclude is not None:
                    # If either params is not None and this clause is reached => filter was not passed
                    self.matrix.at[y_coord, tg] = "Excluded"
                else:
                    # If both are None, probes are not filtered, thus all of them are run
                    self.matrix.at[y_coord, tg] = probe.run(tg)
                    print('-' * 25)

        logging.info(f"All target files analyzed ({self.count_targets})")

    def to_json(self):
        # TODO: implement
        pass

    def to_excel(self):
        # TODO: implement
        pass
