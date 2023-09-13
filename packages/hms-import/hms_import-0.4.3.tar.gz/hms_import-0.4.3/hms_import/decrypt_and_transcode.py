import argparse
import datetime
from glob import glob
import io
import logging
from math import floor, isnan
import os
from pprint import pformat
import requests
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Union

import tator
from tator.openapi.tator_openapi.models import File
from tator.transcode.__main__ import transcode_main as tator_transcode
from tqdm import tqdm

from hms_import.util import LAND_DATE_PLACEHOLDER, SAIL_DATE_PLACEHOLDER, wait_for_thumbs


if __name__ != "__main__":
    logger = logging.getLogger(__name__)

GPS_EXT = ".log"
LOGS_TO_IGNORE = ["tracelog", "eventlog"]


def decrypt_file(private_key_path, data_dir, output_dir) -> bool:
    retval = True
    args = [
        "/scripts/FileProcessor",
        "--decrypt",
        private_key_path,
        "--verbose",
        output_dir,
        data_dir,
    ]
    try:
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            if process.stdout is not None:
                for line in io.TextIOWrapper(process.stdout, newline=""):
                    logger.info(line.strip())
    except Exception:
        logger.warning(f"Attempt to decrypt contents of '{data_dir}' unsuccessful", exc_info=True)
        retval = False

    return retval


def decrypt_media(
    private_key_path: str, data_dir: str, output_dir: str, toc_extension: str
) -> Dict[str, Any]:
    if not decrypt_file(private_key_path, data_dir, output_dir):
        return {}

    toc_files = glob(os.path.join(output_dir, f"*{toc_extension}"))
    if len(toc_files) != 1:
        return {}

    with open(toc_files[0]) as fp:
        decrypted_filename, start_time_ms, end_time_ms = fp.read().strip().split(",")

    return {
        "toc_start": datetime.datetime.fromtimestamp(
            int(start_time_ms) / 1000, tz=datetime.timezone.utc
        ),
        "toc_end": datetime.datetime.fromtimestamp(
            int(end_time_ms) / 1000, tz=datetime.timezone.utc
        ),
        "decrypted_name": decrypted_filename,
    }


def convert_int(value: str) -> int:
    try:
        return int(value)
    except Exception:
        pass
    return 0


def convert_float(value: str) -> float:
    try:
        converted_float = float(value)
    except Exception:
        converted_float = 0.0
    else:
        if isnan(converted_float):
            converted_float = 0.0
    return converted_float


def convert_datetime(value: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(value, "%y%m%d%H%M%S%z")
    except Exception:
        pass
    return datetime.datetime.min


def _line_to_attrs(line: str) -> Union[Dict[str, Any], None]:
    try:
        (
            date_col,
            time_col,
            latitude_col,
            longitude_col,
            satellite_error_col,
            speed_col,
            heading_col,
            video_col,
            pressure1_col,
            set_rotation1_col,
            retrieval_rotation1_col,
            _,
        ) = line.split(",")
    except ValueError:
        logger.debug("Could not split line '%s' 12 times as desired, skipping", line, exc_info=True)
        return None
    return {
        "Satellite Count": convert_int(satellite_error_col),
        "Knots": convert_float(speed_col),
        "Heading": convert_float(heading_col),
        "Datecode": convert_datetime(f"{date_col}{time_col}Z"),
        "Position": [convert_float(longitude_col), convert_float(latitude_col)],
        "Video": convert_int(video_col),
        "Pressure 1": convert_float(pressure1_col),
        "Set Rotation 1": convert_float(set_rotation1_col),
        "Retrieval Rotation 1": convert_float(retrieval_rotation1_col),
    }


def decrypt_metadata(private_key_path: str, data_dir: str, output_dir: str) -> List[Dict[str, Any]]:
    # Decrypt the file
    if not decrypt_file(private_key_path, data_dir, output_dir):
        return []

    # Make sure there is exactly one file with the desired extension
    gps_list = glob(os.path.join(output_dir, f"*{GPS_EXT}"))
    if len(gps_list) != 1:
        return []

    # Convert the lines of the file to attributes
    with open(gps_list[0]) as fp:
        metadata = [_line_to_attrs(line) for line in fp.readlines()]

    return [point for point in metadata if point]


def main(
    *,
    host: str,
    token: str,
    work_dir: str,
    project_id: int,
    media_ids: List[int],
    media_extension: str,
    toc_extension: str,
    state_type: int,
    image_type: int,
    multi_type: int,
    private_key_path: Optional[str] = None,
) -> None:
    tator_api = tator.get_api(host=host, token=token)
    media_list = tator_api.get_media_list(project_id, media_id=media_ids)
    section_name = ""
    section_id = -1
    media_type = None
    if media_list:
        media = media_list[0]
        media_type = media.type
        tator_user_sections = media.attributes["tator_user_sections"]
        section_list = tator_api.get_section_list(project_id)
        if isinstance(section_list, list):
            for sec in section_list:
                if sec.tator_user_sections == tator_user_sections:
                    section_name = sec.name
                    section_id = sec.id
                    break

    datetime_lookup = {}
    starts_and_ids = []

    # Decrypt and transcode all media files first
    logger.info("Decrypting and transcoding media")
    sail_date = datetime.date.max
    land_date = datetime.date.min
    vessel_name = None
    for media in media_list:
        with tempfile.TemporaryDirectory(dir=work_dir) as data_dir, tempfile.TemporaryDirectory(
            dir=work_dir
        ) as output_dir:
            # Get download info for encrypted file
            encrypted_path = media.attributes.get("encrypted_path", None)
            if encrypted_path:
                download_info = tator_api.get_download_info(project_id, {"keys": [encrypted_path]})
                if not (
                    download_info
                    and isinstance(download_info, list)
                    and download_info[0].key == encrypted_path
                    and download_info[0].url
                ):
                    raise RuntimeError(
                        f"Could not get download info for {encrypted_path=}; received:\n"
                        f"{pformat(download_info)}"
                    )

                # Download the encrypted video file
                encrypted_path = os.path.join(data_dir, media.name)
                response = requests.get(download_info[0].url, stream=True)
                with open(encrypted_path, "wb") as fp:
                    for chunk in response.iter_content(chunk_size=10485760):  # 10 MiB
                        fp.write(chunk)

                # Decrypt and transcode the file
                attributes = decrypt_media(private_key_path, data_dir, output_dir, toc_extension)
                if not attributes:
                    logger.warning("Could not decrypt %s, skipping transcode", media.name)
                    continue
                source_dir = output_dir
            else:
                source_dir = work_dir
                attributes = {
                    "toc_start": datetime.datetime.fromisoformat(media.attributes["toc_start"]),
                    "toc_end": datetime.datetime.fromisoformat(media.attributes["toc_end"]),
                    "decrypted_name": media.attributes["decrypted_name"],
                }

            sail_date = min(sail_date, attributes["toc_start"].date())
            land_date = max(land_date, attributes["toc_end"].date())
            if not vessel_name:
                vessel_name = media.attributes.get("Vessel Name", None)
            path = os.path.join(source_dir, attributes["decrypted_name"])
            media_update = {"attributes": attributes}
            datetime_lookup[media.id] = {"obj": None, **attributes}
            try:
                tator_api.update_media(media.id, media_update=media_update)
            except Exception:
                logger.warning("Could not update media %d with update %s", media.id, media_update)
            if os.path.isfile(path):
                filename = attributes["decrypted_name"]
                pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100, ascii=False)
                last_progress = 0
                for p, _ in tator.util.upload_media(
                    api=tator_api,
                    type_id=media.type,
                    path=path,
                    md5=tator.util.md5sum(path),
                    fname=filename,
                    media_id=media.id,
                    timeout=120,
                ):
                    increment = max(p - last_progress, 1)
                    pbar.update(increment)
                    last_progress = p

                # Store info for creating multiviews
                starts_and_ids.append((attributes["toc_start"], media.id))
            else:
                logger.error("Error decrypting %s", attributes["decrypted_name"])
                err_log_path = f"{path}.log"

                if os.path.isfile(err_log_path):
                    with open(err_log_path) as fp:
                        for line in fp.readlines():
                            logger.error(line.strip())
                else:
                    logger.error("Could not open log file at '%s'", err_log_path)

            # Get updated media file metadata
            datetime_lookup[media.id]["obj"] = tator_api.get_media(media.id)

    starts_and_ids.sort()
    current_start, media_id = starts_and_ids[0]
    multi_lookup = {current_start: [media_id]}
    for start_dt, media_id in starts_and_ids[1:]:
        if (start_dt - current_start).total_seconds() > 5:
            multi_lookup[start_dt] = []
            current_start = start_dt
        multi_lookup[current_start].append(media_id)
    # Determine extant multiviews by comparing against id lists and remove from creation list
    media_id_sets = [(start, set(media_ids)) for start, media_ids in multi_lookup.items()]
    paginator = tator.util.get_paginator(tator_api, "get_media_list")
    kwargs = {"project": project_id, "type": multi_type}
    if section_id:
        kwargs["section"] = section_id
    page_iter = paginator.paginate(**kwargs)
    try:
        for page in page_iter:
            for multi in page:
                multi_id_set = set()
                if (
                    hasattr(multi, "media_files")
                    and hasattr(multi.media_files, "ids")
                    and multi.media_files.ids
                ):
                    multi_id_set.update(multi.media_files.ids)
                if multi_id_set:
                    for start, media_id_set in media_id_sets:
                        if multi_id_set == media_id_set:
                            multi_lookup.pop(start, None)
                            break
    except RuntimeError:
        # Paginator has a bug in handling zero results
        pass

    # Create non-existent multiviews
    if wait_for_thumbs(tator_api, media_ids):
        logger.info("Creating %d multiviews", len(multi_lookup))
        for start, media_ids in multi_lookup.items():
            # Get latest start time
            multi_start = max(datetime_lookup[media_id]["toc_start"] for media_id in media_ids)

            # Sort media by filename for consistent display order
            media_objects = [datetime_lookup[media_id]["obj"] for media_id in media_ids]
            media_objects.sort(key=lambda ele: ele.name)
            ordered_media_ids = [m.id for m in media_objects]

            # Calculate frame offsets
            frame_offsets = [
                floor(
                    (multi_start - datetime_lookup[media.id]["toc_start"]).total_seconds() * media.fps
                )
                if media.fps
                else 0
                for media in media_objects
            ]

            try:
                tator.util.make_multi_stream(
                    api=tator_api,
                    type_id=multi_type,
                    layout=[1, 2],
                    name=start.isoformat(),
                    media_ids=ordered_media_ids,
                    section=section_name,
                    frame_offset=frame_offsets,
                )
            except Exception:
                logger.warning(
                    "Failed to make multi for start time %s", start.isoformat(), exc_info=True
                )

    # Update section and media with sail and land dates
    new_section_name = section_name
    new_section_name = new_section_name.replace(
        SAIL_DATE_PLACEHOLDER, sail_date.strftime("%Y-%m-%d")
    )
    new_section_name = new_section_name.replace(
        LAND_DATE_PLACEHOLDER, land_date.strftime("%Y-%m-%d")
    )
    try:
        tator_api.update_section(section_id, section_update={"name": new_section_name})
    except Exception:
        logger.warning(
            "Could not change section name from %s to %s",
            section_name,
            new_section_name,
            exc_info=True,
        )
    bulk_update = {
        "attributes": {
            "Sail Date": sail_date,
            "Land Date": land_date,
            "Vessel Name": vessel_name,
        }
    }
    for mt in [media_type, multi_type, image_type]:
        try:
            tator_api.update_media_list(project_id, bulk_update, type=mt)
        except Exception:
            logger.warning(
                "Could not apply bulk update '%s' to MediaType %d", bulk_update, mt, exc_info=True
            )

    related_file_ids = set(
        int(file_id)
        for entry in datetime_lookup.values()
        for file_id in entry["obj"].attributes.get("related_files", "").split(",")
        if file_id.isnumeric()  # Protects against an empty string
    )

    # For idempotency, delete any existing state specs on the media, one media at a time to avoid
    # too many deletions
    for media_id in datetime_lookup.keys():
        try:
            response = tator_api.delete_state_list(project_id, media_id=[media_id])
        except Exception:
            logger.warning("Could not delete existing states on media %d", media_id, exc_info=True)

    metadata = []
    if related_file_ids:
        for file_id in related_file_ids:
            file_obj = tator_api.get_file(file_id)
            if not isinstance(file_obj, File):
                logger.warning("Could not find file with id %d, skipping", file_id)
                continue
            if not isinstance(file_obj.name, str):
                logger.warning("Could not get name of file %d, skipping", file_id)
                continue
            if any(kw in file_obj.name for kw in LOGS_TO_IGNORE):
                logger.info("Skipping log file '%s'; it does not contain GPS data", file_obj.name)
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
            with tempfile.TemporaryDirectory(dir=work_dir) as data_dir, tempfile.TemporaryDirectory(
                dir=work_dir
            ) as output_dir:
                # Download the encrypted GPS file
                encrypted_path = os.path.join(data_dir, file_obj.name)
                response = requests.get(download_url, stream=True)
                with open(encrypted_path, "wb") as fp:
                    for chunk in response.iter_content(chunk_size=128):
                        fp.write(chunk)

                metadata.extend(decrypt_metadata(private_key_path, data_dir, output_dir))
    else:
        gps_list = glob(os.path.join(work_dir, f"*primary_sensor*{GPS_EXT}"))
        # Convert the lines of the file to attributes
        for gps_file in gps_list:
            with open(gps_file) as fp:
                file_points = [_line_to_attrs(line) for line in fp.readlines()]
            metadata.extend(point for point in file_points if point)

    state_specs = []
    # Create a state spec for each point/media pair, where the point timestamp occurs between
    # the start and stop timestamps of the media object
    for point in metadata:
        for media_id, media_info in datetime_lookup.items():
            if (
                media_info["toc_start"] <= point["Datecode"] <= media_info["toc_end"]
                and media_info["obj"].fps
            ):
                delta = (point["Datecode"] - media_info["toc_start"]).total_seconds()
                frame = floor(delta * media_info["obj"].fps)
                state_specs.append(
                    {
                        "type": state_type,
                        "media_ids": [media_id],
                        "frame": frame,
                        "attributes": point,
                    }
                )

    for response in tator.util.chunked_create(
        tator_api.create_state_list, project_id, body=state_specs
    ):
        logger.info(response.message)


if __name__ == "__main__":
    from hms_import.util import HmsLogHandler
    parser = argparse.ArgumentParser(
        description="Script for decrypting and transcoding encrypted video files"
    )
    # Get updated media file metadata
    tator.get_parser(parser)
    parser.add_argument("--work-dir", type=str, required=True)
    parser.add_argument("--project-id", type=int, required=True)
    parser.add_argument("--media-ids", nargs="+", type=int, required=True)
    parser.add_argument("--media-extension", type=str, required=True)
    parser.add_argument("--toc-extension", type=str, required=True)
    parser.add_argument("--state-type", type=int, required=True)
    parser.add_argument("--image-type", type=int, required=True)
    parser.add_argument("--multi-type", type=int, required=True)
    parser.add_argument("--private-key-path", type=str, required=False)
    args = parser.parse_args()

    with HmsLogHandler(console_log_level=logging.INFO):
        logger = logging.getLogger(__name__)
        main(**vars(args))
