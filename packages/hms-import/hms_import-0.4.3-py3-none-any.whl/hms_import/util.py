import argparse
from configparser import ConfigParser
from datetime import date
from io import TextIOBase
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
from time import sleep
from typing import Any, Callable, List, Optional

from tator.openapi.tator_openapi import Media, Section, TatorApi
from tqdm import tqdm

logger = logging.getLogger(__name__)

SAIL_DATE_PLACEHOLDER = "NO_SAIL_DATE"
LAND_DATE_PLACEHOLDER = "NO_LAND_DATE"
VESSEL_NAME_MAP = {
    "1022773": "Eagle Eye II",
    "1027010": "Alex Marie",
    "1029712": "Kenny Boy",
    "1031845": "Destiny",
    "1038712": "Ellen Jean",
    "1049623": "Leo B",
    "1061277": "Miss Kaleigh",
    "1075516": "Jamie B",
    "1081640": "Capt Easy",
    "1097631": "Hanna Katherine",
    "1231179": "Full Timer",
    "1231553": "Dayboat One",
    "1275363": "Market Price",
    "507646": "Daytona",
    "510728": "Miss Suzanne",
    "539456": "Bookie",
    "541694": "Eaglet II",
    "557860": "Independence",
    "579208": "Galilean",
    "591301": "Charleston Star",
    "592269": "Capt. Gorman III",
    "595941": "Blue Wave",
    "596805": "Mary Ann",
    "597797": "Bluefin",
    "600048": "Kim Thanh II",
    "600293": "4 Cs",
    "600322": "Bobalou",
    "604915": "Frances Ann",
    "608436": "Christopher Joe",
    "609121": "Carol Ann",
    "610006": "Captain Michael",
    "610080": "Blessings",
    "611243": "Erica Lynn",
    "616696": "Cynthia Renee",
    "620696": "Albi",
    "622027": "Carter Anthony",
    "624406": "Dayboat Too",
    "628300": "Bigeye",
    "630306": "Defiance",
    "633432": "Kelly Ann",
    "638863": "Miss Shannon",
    "641486": "Miss Ann",
    "646506": "Janice Ann",
    "651698": "Intrepido II",
    "652211": "Lisa Ann",
    "655108": "Miss Haylee II",
    "656259": "Kristin Lee",
    "659026": "Eyelander",
    "661098": "Miss Rita",
    "661284": "Hannah Boden",
    "662409": "Fine Tuna",
    "665962": "Linnea C",
    "668316": "Capt. Luu",
    "669872": "Eagle Eye",
    "671174": "Delphinus",
    "673556": "Candace",
    "674417": "Bear",
    "680845": "Endeavor",
    "683311": "Iron Maiden",
    "904300": "Kim Nhi",
    "905679": "Capt. Mike",
    "908045": "Julianne",
    "911431": "Capt. David",
    "912738": "Joshua Nicole",
    "913385": "2nd Wind",
    "918933": "Miss Lena",
    "919799": "Blue Sea I",
    "929813": "Capt. Bob",
    "936041": "Cecelia II",
    "937416": "Kim Thanh",
    "956008": "Dakota",
    "957958": "Miss Jane",
    "969495": "Hannah Story",
    "983321": "Blue Sea 2",
    "997091": "Alexandria Dawn",
    "FL5295PN": "Big B",
    "MD9128BD": "Integrity",
    "MS1993DD": "Angel's Grace",
    "NC2015WS": "Kaitlyn C",
    "NC3377EM": "Big Dave",
    "NC5126DC": "Hardway",
    "NC5516DF": "Fish Wish",
    "NC6362EX": "Big Skipper",
    "NC8831WR": "Body Count",
    "NJ4755FP": "Backwash",
}


def validate_type_from_config(
    api: TatorApi,
    config: ConfigParser,
    config_field: str,
    project_id: int,
    tator_type: str,
    list_filters=None,
) -> int:
    if tator_type not in ["media_type", "file_type"]:
        raise ValueError(f"Cannot validate {config_field=} for {tator_type=}")

    type_id = config["Tator"].getint(config_field, -1)
    if type_id > 0:
        try:
            getattr(api, f"get_{tator_type}")(type_id)
        except Exception as exc:
            raise ValueError(f"Could not find {config_field} with id {type_id}") from exc
    else:
        try:
            types = getattr(api, f"get_{tator_type}_list")(project_id)
        except Exception as exc:
            raise RuntimeError(f"Could not list {config_field}s from project {project_id}") from exc
        if list_filters:
            for attr, value in list_filters:
                types = [
                    _type
                    for _type in types
                    if hasattr(_type, attr) and getattr(_type, attr) == value
                ]
        if len(types) > 1:
            raise ValueError(
                f"Project {project_id} has more than one {config_field}, specify one of the "
                f"following in the config: {types}"
            )
        type_id = types[0].id
    return type_id


def safe_get_type(type_id: int, type_getter: Callable[[int], Any]):
    type_inst = None
    try:
        type_inst = type_getter(type_id)
    except Exception:
        logger.error("Could not find type %d", type_id, exc_info=True)
    return type_inst


def file_exists(filename: str) -> str:
    if os.path.isfile(filename):
        return filename
    raise argparse.ArgumentTypeError("Expected the name of an existing file!")


def build_section_name(
    vessel_name: str, sail_date: Optional[date] = None, land_date: Optional[date] = None
) -> str:
    try:
        sail_date_str = sail_date.strftime("%Y-%m-%d") if sail_date else SAIL_DATE_PLACEHOLDER
    except Exception:
        sail_date_str = SAIL_DATE_PLACEHOLDER
    try:
        land_date_str = land_date.strftime("%Y-%m-%d") if land_date else LAND_DATE_PLACEHOLDER
    except Exception:
        land_date_str = LAND_DATE_PLACEHOLDER

    return f"{vessel_name} ({sail_date_str} - {land_date_str})"


def section_from_name(tator_api: TatorApi, project_id: int, section_name: str) -> Optional[Section]:
    section = None
    try:
        section_list = tator_api.get_section_list(project_id)
    except Exception:
        pass
    else:
        if isinstance(section_list, list):
            for sec in section_list:
                if sec.name == section_name:
                    section = sec
                    break
    return section


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


def wait_for_thumbs(tator_api: TatorApi, created_ids: List[int]) -> bool:
    # Wait for imports to generate thumbnails
    logger.info("Waiting for transcodes to generate thumbnails for all uploads...")
    pbar = tqdm(total=len(created_ids), dynamic_ncols=True, position=0, ascii=False)
    while created_ids:
        media = None
        media_id = created_ids.pop(0)
        try:
            media = tator_api.get_media(media_id)
        except Exception:
            logger.warning("Could not get media '%d'", media_id)

        if isinstance(media, Media) and getattr(media.media_files, "thumbnail_gif", None):
            # Do not put the id back on the list if it is invalid or it is ready; check the next one
            pbar.update()
        else:
            # Put the id at the end to check later and sleep to avoid a tight loop
            logger.debug("Media gif thumbnail creation not complete for media %d", media_id)
            created_ids.append(media_id)
            sleep(1.0)
    return True
