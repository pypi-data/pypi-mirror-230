import datetime
from glob import iglob
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import tator
from tator.openapi.tator_openapi import (
    CreateListResponse,
    File,
    FileType,
    MediaType,
    Section,
    TatorApi,
)
from tqdm import tqdm

from hms_import.b3.generate_states import generate_multis_and_states
from hms_import.util import build_section_name, safe_get_type, section_from_name, wait_for_thumbs
from hms_import.summary_image import create_summary_image

logger = logging.getLogger(__name__)
DATETIME_FORMAT = "%Y%m%dT%H%M%SZ"


def upload_and_import_videos(
    tator_api: TatorApi,
    video_list: List[str],
    media_type: MediaType,
    summary_type_id: int,
    vessel_name: str,
    file_list: List[File],
    section_name: str,
) -> Tuple[List[int], Dict[str, Any], str]:
    """Returns list of created media ids"""
    created_ids = []
    media_type_id = media_type.id
    project_id = media_type.project
    shared_attributes = {
        "Vessel Name": vessel_name,
        "Sail Date": datetime.date.max,
        "Land Date": datetime.date.min,
        "related_files": ",".join(str(file_obj.id) for file_obj in file_list),
    }

    # Collect media_specs
    media_specs = []
    for video_path in video_list:
        try:
            filename = os.path.basename(video_path)
            filename_parts = os.path.splitext(filename)[0].split("-")
            start_datetime = datetime.datetime.min
            if len(filename_parts) == 4:
                start_date, start_time = filename_parts[2:4]
                try:
                    start_datetime = datetime.datetime.strptime(
                        f"{start_date}T{start_time}", DATETIME_FORMAT
                    ).replace(tzinfo=datetime.timezone.utc)
                except Exception:
                    logger.warning("Could not parse datetime from filename '%s'", filename)
            if start_datetime != datetime.datetime.min:
                shared_attributes["Sail Date"] = min(
                    shared_attributes["Sail Date"], start_datetime.date()
                )
            if start_datetime != datetime.datetime.min:
                shared_attributes["Land Date"] = max(
                    shared_attributes["Land Date"], start_datetime.date()
                )
            vid_md5 = tator.util.md5sum(video_path)

            # Store the media spec and video path for creation
            media_specs.append(
                (
                    video_path,
                    {
                        "attributes": {"toc_start": start_datetime},
                        "name": filename,
                        "type": media_type_id,
                        "section": section_name,
                        "md5": vid_md5,
                    },
                )
            )
        except Exception:
            logger.warning("Encountered exception while processing '%s', skipping", video_path)

    # Rename section
    logger.info("renaming section")
    section = section_from_name(tator_api, project_id, section_name)
    new_section_name = section_name
    section_id = -1
    if isinstance(section, Section):
        section_id = section.id
        new_section_name = build_section_name(
            vessel_name=shared_attributes["Vessel Name"],
            sail_date=shared_attributes["Sail Date"],
            land_date=shared_attributes["Land Date"],
        )
        try:
            response = tator_api.update_section(
                section.id, section_update={"name": new_section_name}
            )
        except Exception:
            new_section_name = section_name

    # Upload files and create media objects
    logger.info("uploading files")
    for video_path, media_spec in tqdm(
        media_specs, desc="Video Imports", dynamic_ncols=True, position=0, ascii=False
    ):
        try:
            media_spec["section"] = new_section_name
            media_spec["attributes"].update(shared_attributes)
            response = tator_api.create_media_list(project_id, body=[media_spec])
            if isinstance(response, CreateListResponse) and response.id:
                filename = media_spec["name"]
                vid_md5 = media_spec["md5"]
                created_ids.append(response.id[0])
                pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100, ascii=False)
                last_progress = 0
                for p, _ in tator.util.upload_media(
                    api=tator_api,
                    type_id=media_type_id,
                    path=video_path,
                    md5=vid_md5,
                    section=new_section_name,
                    fname=filename,
                    media_id=created_ids[-1],
                    timeout=120,
                ):
                    increment = max(p - last_progress, 1)
                    pbar.update(increment)
                    last_progress = p

            else:
                logger.warning("Could not create media object for '%s', skipping", video_path)
        except Exception:
            logger.warning("Encountered exception while processing '%s', skipping", video_path)

    # Update summary image, if any, with shared attributes
    shared_attributes.pop("related_files", None)
    try:
        tator_api.update_media_list(
            project_id,
            media_bulk_update={"attributes": shared_attributes},
            type=summary_type_id,
            section=section_id,
        )
    except Exception:
        logger.warning("Failed to update summary image with attributes %s", shared_attributes)

    return created_ids, shared_attributes, new_section_name


def upload_sensor_data(
    tator_api: TatorApi,
    sensor_list: List[str],
    file_type: FileType,
) -> List[File]:
    file_type_id = file_type.id
    file_list = []
    for sensor_path in tqdm(
        sensor_list, dynamic_ncols=True, desc="Sensor Import", position=0, ascii=False
    ):
        filename = os.path.basename(sensor_path)
        try:
            pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100, ascii=False)
            last_progress = 0
            response = None
            for p, response in tator.util.upload_generic_file(
                api=tator_api,
                file_type=file_type_id,
                path=sensor_path,
                description="Raw sensor data",
                name=filename,
                timeout=120,
            ):
                increment = max(p - last_progress, 1)
                pbar.update(increment)
                last_progress = p
        except Exception:
            logger.warning("Encountered exception while processing '%s', skipping", sensor_path)
            continue
        if isinstance(response, File):
            file_list.append(response)
    return file_list


def main(
    host: str,
    token: str,
    media_type_id: int,
    file_type_id: int,
    multi_type_id: int,
    state_type_id: int,
    image_type_id: int,
    directory: str,
    hdd_sn: Optional[str] = None,
) -> bool:
    """
    :host: The Tator domain
    :token: The REST API token
    :media_type_id: The unique ID of the type of video to create
    :file_type_id: The unique ID of the type of file to create for storing GPS data
    :multi_type_id: The unique ID of the type of multiview to create
    :state_type_id: The unique ID of the type of State to create
    :image_type_id: The unique ID of the type of summary image to create
    :directory: The folder containing the files to import
    :hdd_sn: The hard drive serial number
    :returns: True if the import was successful, False if any part of it fails
    """

    # Validate the given media and file types, abort if they do not exist or are incompatible
    tator_api = tator.get_api(host=host, token=token)
    media_type = safe_get_type(media_type_id, tator_api.get_media_type)
    file_type = safe_get_type(file_type_id, tator_api.get_file_type)
    if media_type is None:
        logger.error("Could not get media type %d from Tator, aborting", media_type_id)
        return False
    if file_type is None:
        logger.error("Could not get file type %d from Tator, aborting", file_type_id)
        return False
    if media_type.project != file_type.project:
        logger.error(
            "Received MediaType %d and FileType %d, which are from different projects, aborting",
            media_type_id,
            file_type_id,
        )
        return False

    # Locate media for import and create summary image
    video_list = list(iglob(os.path.join(directory, f"*.mp4")))
    section_name, vessel_name = create_summary_image(
        host=host,
        token=token,
        media_type=image_type_id,
        import_type="B3",
        directory=directory,
        hdd_sn=hdd_sn,
    )

    # Locate sensor data for import
    sensor_list = list(iglob(os.path.join(directory, f"*.log")))
    if sensor_list:
        file_list = upload_sensor_data(tator_api, sensor_list, file_type)
    else:
        file_list = []
        logger.warning("No sensor data found, only videos will be imported")

    if video_list:
        logger.debug("importing videos")
        created_ids, shared_attrs, new_section_name = upload_and_import_videos(
            tator_api, video_list, media_type, image_type_id, vessel_name, file_list, section_name
        )
    else:
        logger.error("No media found, aborting")
        return False

    # Generate associated multiviews and GPS States
    if wait_for_thumbs(tator_api, created_ids):
        generate_multis_and_states(
            host=host,
            token=token,
            media_type_id=media_type_id,
            multi_type_id=multi_type_id,
            state_type_id=state_type_id,
            section_name=new_section_name,
            attrs=shared_attrs,
        )
    return True
