from collections import defaultdict
import datetime
import logging
from math import floor
import os
import requests
import tempfile
from typing import Any, Dict

from natsort import natsorted
import pynmea2
import tator
from tator.openapi.tator_openapi import File, MediaType
from tqdm import tqdm

from hms_import.util import section_from_name

DATETIME_FORMAT = "%Y%m%dT%H%M%SZ"
logger = logging.getLogger(__file__)


def _line_to_attrs(line):
    stripped_line = line.strip("\x00")
    if stripped_line:
        try:
            message = pynmea2.parse(f"$GPRMC,{stripped_line}")
            return {
                "Knots": message.spd_over_grnd,
                "Heading": message.true_course,
                "Datecode": message.datetime,
                "Position": [message.lon, message.lat],
            }
        except Exception:
            logger.debug("Skipping malformed gps entry: '%s'", line)
    return None


def points_from_file(gps_data_path):
    with open(gps_data_path, "r") as fp:
        lines = fp.readlines()
    metadata = [_line_to_attrs(line) for line in lines]
    return [point for point in metadata if point is not None]


def generate_multis_and_states(
    host: str,
    token: str,
    media_type_id: int,
    multi_type_id: int,
    state_type_id: int,
    section_name: str,
    attrs: Dict[str, Any],
):
    tator_api = tator.get_api(host=host, token=token)

    try:
        multi_type = tator_api.get_media_type(multi_type_id)
    except Exception:
        logger.error(
            "Could not find MediaType '%d' in Tator, aborting!", multi_type_id, exc_info=True
        )
        return
    if not isinstance(multi_type, MediaType):
        return
    if multi_type.project:
        project_id = multi_type.project
    else:
        return

    section = section_from_name(tator_api, project_id, section_name)
    if section is None:
        logger.error(
            "Found no section named '%s' in project '%d', aborting!", section_name, project_id
        )
        return

    media_list = tator_api.get_media_list(
        project=project_id, section=section.id, type=media_type_id
    )
    if not (isinstance(media_list, list) or media_list):
        logger.error(
            "Found no media in section '%s' in project '%d', aborting!", section_name, project_id
        )
        return

    project_id = media_list[0].project
    datetime_lookup = {}
    multi_lookup = defaultdict(list)
    state_file_ids = set()

    for media in media_list:
        try:
            # Get info to create states
            state_file_ids.update(
                int(fid)
                for fid in media.attributes.get("related_files", "").split(",")
                if fid.isnumeric()
            )

            toc_start = datetime.datetime.fromisoformat(media.attributes["toc_start"])
            duration = datetime.timedelta(seconds=media.num_frames / media.fps)
            datetime_lookup[media.id] = {
                "fps": media.fps,
                "toc_start": toc_start,
                "toc_end": toc_start + duration,
            }

            # Get info to create multiviews
            if not media.name:
                logger.warning("Could not get filename for media '%d', skipping", media.id)
                continue
            filename = media.name
            multi_lookup[toc_start].append((filename, media.id))
        except Exception:
            logger.error(
                "Encountered exception while processing '%d', skipping", media.id, exc_info=True
            )

    # Make multiviews from pairs of concurrent videos
    for start_dt, media_lst in tqdm(
        list(multi_lookup.items()),
        desc="Creating Multis",
        dynamic_ncols=True,
        position=0,
        ascii=False,
    ):
        sorted_ids = [ele[-1] for ele in natsorted(media_lst)]
        tator.util.make_multi_stream(
            api=tator_api,
            type_id=multi_type_id,
            layout=[1, 2],
            name=start_dt.strftime(DATETIME_FORMAT),
            media_ids=sorted_ids,
            section=section.name,
        )

    try:
        tator_api.update_media_list(
            project=project_id,
            media_bulk_update={"attributes": attrs},
            type=multi_type_id,
            section=section.id,
        )
    except Exception:
        logger.warning("Failed to update attributes on multiviews, moving on")

    # Generate states
    state_specs = []
    for file_id in state_file_ids:
        try:
            file_obj = tator_api.get_file(file_id)
        except Exception:
            logger.error("Could not get File '%d', skipping", file_id, exc_info=True)
            continue
        if not isinstance(file_obj, File):
            logger.warning("Could not find file with id %d, skipping", file_id)
            continue
        if not isinstance(file_obj.name, str):
            logger.warning("Could not get name of file %d, skipping", file_id)
            continue
        download_info = tator_api.get_download_info(
            file_obj.project, download_info_spec={"keys": [file_obj.path]}
        )

        if not (download_info and isinstance(download_info, list) and download_info[0].url):
            logger.warning(
                "Could not get download info for '%s' (%d), skipping", file_obj.name, file_id
            )
            continue
        else:
            download_url = download_info[0].url

        # Make working directories
        with tempfile.TemporaryDirectory() as data_dir:
            # Download the encrypted GPS file
            gps_data_path = os.path.join(data_dir, file_obj.name)
            response = requests.get(download_url, stream=True)
            with open(gps_data_path, "wb") as fp:
                for chunk in response.iter_content(chunk_size=128):
                    fp.write(chunk)

            metadata = points_from_file(gps_data_path)

        # Create a state spec for each point/media pair, where the point timestamp occurs between
        # the start and stop timestamps of the media object
        for point in metadata:
            for media_id, media_info in datetime_lookup.items():
                if (
                    media_info["toc_start"] <= point["Datecode"] <= media_info["toc_end"]
                    and media_info["fps"]
                ):
                    delta = (point["Datecode"] - media_info["toc_start"]).total_seconds()
                    frame = floor(delta * media_info["fps"])
                    state_specs.append(
                        {
                            "type": state_type_id,
                            "media_ids": [media_id],
                            "frame": frame,
                            "attributes": point,
                        }
                    )

    for response in tator.util.chunked_create(
        tator_api.create_state_list, project_id, body=state_specs
    ):
        logger.info(response.message)
