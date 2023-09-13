import os.path
from tinydb import TinyDB


class AnalysisDataBase:
    # TODO: implement
    """
    This class aims to be a "cache" of analyzed files.
    When a probe is about to be run on a target,
    the specified target is searched (by sha256) within AnalysisDatabase
    If the file has been previously analyzed with that probe, the results will be there

    The goal behind this idea is to reduce analysis time, since the probes might be time-consuming
    """
    def __init__(self, path):
        """

        :param path: Path to TinyDB JSON file
        """
        self.path = path if os.path.isfile(path) else 'db.json'
        self.connector = TinyDB(self.path)

    def update_tables(self):
        # TODO: initialize the other tables: Reports, Exit codes, templates
        # Initialize all the probe
        pb_table = self.connector.table('Probes')
        pb_table.truncate()
        # for pb in artsemLib.list_probes(os.path.join(os.path.dirname(self.path))):
        #     _pbconf = pb.conf
        #     logging.debug(f"Probe conf loaded:{_pbconf}")
        #     pb_table.insert(_pbconf)
        #
        # # Update exit codes
        # logging.info("Updating Exitcodes table")
        # t = self.connector.table('Exitcodes')
        # t.truncate()
        # t.insert_multiple(
        #     artsemLib.compile_exitcodes(
        #         csv_path=os.path.join(__install_dir__, 'config', 'exitcodes.csv'),
        #         outfile=os.path.join(__install_dir__, 'src', 'main', 'error.py')))
        # # t.insert_multiple(compileExitCodes.compile_exitcodes())
        #
