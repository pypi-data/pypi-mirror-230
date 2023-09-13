from datetime import datetime
from glob import iglob
import logging
import os
import re
from tempfile import NamedTemporaryFile
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
import tator
from tator.openapi.tator_openapi import CreateResponse

from hms_import.util import VESSEL_NAME_MAP, build_section_name


logger = logging.getLogger(__name__)
FONT = os.path.join(os.path.dirname(__file__), "Cascadia.ttf")
FONT_SIZE = 36
SUMMARY_IMG_SZ = 1024


def create_summary_image(
    host: str,
    token: str,
    media_type: int,
    directory: str,
    import_type: str,
    skip_decrypt: Optional[bool] = False,
    hdd_sn: Optional[str] = None,
) -> Tuple[str, str]:
    """Creates a summary image for a trip.

    :host: The Tator hostname
    :token: The Tator API token
    :media_type: The Tator media type to create
    :directory: The directory containing files to use to determine the vessel name
    :skip_decrypt: If true, use the decrypted filename format to find the vessel name
    :hdd_sn: The value for the HDD Serial Number attribute
    :returns: The created section name and found vessel name
    """

    vessel_name = "UNKNOWN"
    if import_type == "O2":
        # Get the vessel name and trip id from the first filename found starting with `stream-`
        if skip_decrypt:
            filename = os.path.basename(next(iglob(os.path.join(directory, f"*.mp4"))))
            name_parts = os.path.splitext(filename)[0].split("-")
            vessel_name = name_parts[0]
        else:
            filename = os.path.basename(next(iglob(os.path.join(directory, f"stream-*"))))
            name_parts = os.path.splitext(filename)[0].split("-")
            vessel_name = name_parts[1]
    elif import_type == "B3":
        video_list = list(iglob(os.path.join(directory, f"*.mp4")))
        video_path = video_list[0]
        filename = os.path.basename(video_path)
        filename_parts = os.path.splitext(filename)[0].split("-")
        if len(filename_parts) == 4:
            try:
                vessel_name = filename_parts[0]
            except Exception:
                logger.warning("Could not get the vessel or section name", exc_info=True)
    else:
        raise RuntimeError(f"Received unexepected import type argument: {import_type}")

    vessel_name = VESSEL_NAME_MAP.get(vessel_name, vessel_name)
    attrs = {"Vessel Name": vessel_name}
    section_name = build_section_name(vessel_name)
    attrs = {
        "Vessel Name": vessel_name,
        "HDD Date Received": datetime.today().strftime("%Y-%m-%d"),
        "HDD Serial Number": hdd_sn,
    }
    label_len = max(len(key) for key in attrs.keys())
    image_text = "\n".join(f"{k: >{label_len}}: {v}" for k, v in attrs.items())
    font = ImageFont.truetype(font=FONT, size=FONT_SIZE)
    image = Image.new("RGB", (SUMMARY_IMG_SZ, SUMMARY_IMG_SZ), color="black")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox((0, 0), image_text, font=font)
    x_pos = (SUMMARY_IMG_SZ - (right - left)) // 2
    y_pos = (SUMMARY_IMG_SZ - (bottom - top)) // 2
    draw.text((x_pos, y_pos), image_text, fill="white", font=font)

    with NamedTemporaryFile(suffix=".png") as temp_file:
        image.save(temp_file.name)
        tator_api = tator.get_api(host=host, token=token)

        import_media_args = {
            "api": tator_api,
            "type_id": media_type,
            "path": temp_file.name,
            "section": section_name,
            "fname": os.path.basename(temp_file.name),
            "attributes": {k: v for k, v in attrs.items() if v is not None},
        }

        response = None
        try:
            for progress, response in tator.util.upload_media(**import_media_args):
                logger.info("Upload progress for %s: %d%%", temp_file.name, progress)
        except Exception:
            logger.error(
                "Could not create trip summary with args:\n%s", import_media_args, exc_info=True
            )
        else:
            if isinstance(response, CreateResponse):
                logger.info("Uploaded image, received response: %s", response.message)

    return section_name, vessel_name
