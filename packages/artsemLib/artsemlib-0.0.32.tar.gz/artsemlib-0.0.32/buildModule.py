import logging
import os
import subprocess
import sys
from re import fullmatch

__interpreter__ = 'python3' if sys.platform.find('linux') != -1 else 'python.exe'
__build_tools__ = ['twine', 'build']


def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Builds and publish artsemLib package")
    parser.add_argument(
        "-v",
        action="count",
        default=0,
        help="increase logging verbosity [-v, -vv]")
    parser.add_argument(
        "-p", "--pub",
        nargs='*',
        type=str,
        metavar="NEW_VERSION",
        help="If build success, publish the NEW_VERSION package to the repository"
    )
    parser.add_argument(
        "-V", "--version",
        action="store_true",
        default=False,
        help="Print the current package version and exits"
    )
    _a = parser.parse_args(cmd)
    if _a.v == 0:
        logging.basicConfig(level='WARN')
    elif _a.v == 1:
        logging.basicConfig(level='INFO')
    else:
        logging.basicConfig(level='DEBUG')
    logging.debug(f"CLI arguments: {_a}")
    return _a


def auto_increment_version(v) -> str:
    _version = str(v).split('.')
    _version[-1] = str(int(_version[-1]) + 1)
    logging.info(f"Auto incrementing version ({v} -> {'.'.join(_version)})")
    return '.'.join(_version)


def get_current_version() -> str:
    _result = subprocess.run([__interpreter__, '-m', 'hatch', 'version'], stdout=subprocess.PIPE)
    return _result.stdout.decode('utf-8').replace('\n', '').strip()


def clean_build():
    logging.info("Cleaning up previous builds")
    run_cmd(f"{__interpreter__} -m hatch clean")
    logging.info("Clean up completed")


def run_cmd(cmd):
    # The program execution stops if any command fail
    _ret = os.system(f"{cmd}")
    if _ret != 0:
        raise RuntimeError(f"Command failed: {cmd} -> {_ret}")
    else:
        logging.debug(f"Command completed: {cmd} -> {_ret}")
    return _ret


def validate_version(version) -> bool:
    """Validates the syntax of a version number

    :param version: version number to be validated
    :return: True if version is valid
    """
    return fullmatch('(\\d+\\.)*\\d+', version) is not None


if __name__ == '__main__':
    _args = parse_args()
    if _args.version:
        print(f"Current package version: {get_current_version()}")
        exit(0)

    if _args.pub is not None:
        if len(_args.pub) > 1:
            logging.error(f"More than one version specified. Please use only one version at a time")
            exit(1)
        elif len(_args.pub) == 0:
            _args.pub = auto_increment_version(get_current_version())
        else:
            _args.pub = _args.pub[0] if len(_args.pub) > 1 else auto_increment_version(get_current_version())
            logging.info(f"Manual versioning ({get_current_version()} -> {_args.pub})")

        if validate_version(_args.pub):
            run_cmd(f"{__interpreter__} -m hatch version {_args.pub}")
        else:
            logging.error(f"Invalid syntax version ({_args.pub}). Allowed [x.]x, where x are integers")
            logging.error("Building process aborted")
            exit(2)
    clean_build()
    logging.info(f"Building module...")
    run_cmd(f'{__interpreter__} -m build')
    logging.info(f"Build completed successfully")

    if _args.pub is not None:
        logging.info(f"Publishing package...")
        run_cmd(f"{__interpreter__} -m hatch publish")
        logging.info(f"Package published successfully")

    logging.info("Execution completed. Exiting...")
    exit(0)
