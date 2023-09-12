from argparse import ArgumentParser, RawDescriptionHelpFormatter
from io import TextIOBase
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

import tator

from hms_import.util import file_exists


def get_parser():
    parser = ArgumentParser(
        description="Script for importing video and metadata in O2 and B3 formats.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Changes the console log level from INFO to WARNING; defers to --verbose",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Changes the console log level from INFO to DEBUG; takes precedence over --quiet",
    )
    cmd_parser = parser.add_subparsers(title="Commands", dest="command")

    b3_parser = cmd_parser.add_parser(
        "b3-upload", help="Imports video and GPS files from unlocked LUKS-encrypted device"
    )
    b3_parser = tator.get_parser(b3_parser)
    b3_parser.add_argument("--media-type-id", type=int)
    b3_parser.add_argument("--file-type-id", type=int)
    b3_parser.add_argument("--multi-type-id", type=int)
    b3_parser.add_argument("--state-type-id", type=int)
    b3_parser.add_argument("--image-type-id", type=int)
    b3_parser.add_argument("--directory", type=str)
    b3_parser.add_argument("--hdd-sn", type=str, required=False)

    o2_parser = cmd_parser.add_parser(
        "o2-upload", help="Script for uploading raw, encrypted video files."
    )
    o2_parser.add_argument(
        "config_file", type=str, help=f"The configuration .ini file used to initialize {__name__}."
    )

    log_parser = cmd_parser.add_parser(
        "log-upload",
        help=f"Uploads the log file {HmsLogHandler.log_filename} to Tator, if it exists",
    )
    log_parser = tator.get_parser(log_parser)
    log_parser.add_argument("--log-file-type-id", type=int)
    log_parser.add_argument(
        "--log-filename", type=file_exists, required=False, default=HmsLogHandler.log_filename
    )
    return parser


class HmsLogHandler(TextIOBase):
    log_filename = os.path.join(os.getcwd(), f"{__name__.split('.')[0]}.log")

    def __init__(self, console_log_level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(console_log_level)
        self._file_handler = TimedRotatingFileHandler(
            HmsLogHandler.log_filename, when="midnight", interval=1, backupCount=7
        )
        self._file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s]: %(message)s")
        self._console_handler.setFormatter(formatter)
        self._file_handler.setFormatter(formatter)
        root_logger.addHandler(self._console_handler)
        root_logger.addHandler(self._file_handler)
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def write(self, *args, **kwargs):
        self._console_handler.stream.write(*args, **kwargs)
        self._file_handler.stream.write(*args, **kwargs)

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self

    def __exit__(self, *_):
        sys.stdout = self._stdout
        sys.stderr = self._stderr


def main() -> None:
    # Parse arguments
    parser = get_parser()
    args = parser.parse_args()
    argdict = vars(args)

    # Always log everything to file, set console log level based on `--quiet` and `--verbose` flags
    console_log_level = logging.INFO
    if argdict.pop("quiet"):
        console_log_level = logging.WARNING
    if argdict.pop("verbose"):
        console_log_level = logging.DEBUG

    # Import the desired main function
    with HmsLogHandler(console_log_level=console_log_level):
        command = argdict.pop("command")
        if command == "o2-upload":
            from hms_import.o2 import main
        elif command == "b3-upload":
            from hms_import.b3 import main
        elif command == "log-upload":
            from hms_import.logs import main
        else:
            raise RuntimeError(f"Received unhandled command '{command}'")

        main(**argdict)
