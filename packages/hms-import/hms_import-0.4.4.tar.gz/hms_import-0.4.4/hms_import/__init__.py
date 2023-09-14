from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging

import tator

from hms_import.util import file_exists, HmsLogHandler


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
        "o2-upload", help="Script for uploading raw, encrypted video files"
    )
    o2_parser.add_argument(
        "config_file", type=str, help=f"The configuration .ini file used to initialize {__name__}."
    )

    log_parser = cmd_parser.add_parser(
        "log-upload",
        help=f"Uploads a log file to Tator",
    )
    log_parser = tator.get_parser(log_parser)
    log_parser.add_argument("--log-file-type-id", type=int)
    log_parser.add_argument(
        "--log-filename", type=file_exists, required=False, default=HmsLogHandler.log_filename
    )
    return parser


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
