from glob import glob
import logging
import os
from typing import List

import tator
from tator.openapi.tator_openapi.models import File
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _import_metadata(host: str, token: str, project_id: int, filename: str, file_type: int) -> int:
    tator_api = tator.get_api(host=host, token=token)

    # Perform idempotency check
    base_filename = os.path.basename(filename)
    paginator = tator.util.get_paginator(tator_api, "get_file_list")
    page_iter = paginator.paginate(project=project_id)
    try:
        for page in page_iter:
            for file_obj in page:
                if file_obj.name == base_filename:
                    file_id = file_obj.id
                    logger.info("Found existing file %d with same name, skipping upload", file_id)
                    return file_id
    except RuntimeError:
        # Bug in paginator will raise RuntimeError if zero entities are returned
        pass

    # Upload encrypted file to Tator
    response = None
    file_id = 0

    try:
        for progress, response in tator.util.upload_generic_file(
            tator_api, file_type, filename, "Encrypted sensor data", name=base_filename
        ):
            logger.info("Upload progress: %.1f%%", progress)
    except Exception as exc:
        raise RuntimeError(f"Raised exception while uploading '{base_filename}', skipping") from exc

    if isinstance(response, File) and isinstance(response.id, int):
        file_id = response.id

    return file_id


def upload_metadata(
    *, host: str, token: str, project_id: int, directory: str, meta_ext: str, file_type: int
) -> List[int]:
    """Finds all encrypted metadata files in `directory`, uploads them to Tator, and runs a workflow
    to decrypt and turn them into States. Disallows use of positional arguments.

    :param host: The hostname of the Tator deployment to upload to.
    :type host: str
    :param token: The Tator API token to use for authentication.
    :type token: str
    :param project_id: The integer id of the project to upload the videos to.
    :type project_id: int
    :param directory: The directory to search for encrypted metadata files.
    :type directory: str
    :param meta_ext: The extension of the encrypted metadata files.
    :type meta_ext: str
    """
    file_list = glob(os.path.join(directory, f"*{meta_ext}-[0-9]*"))
    logger.debug("Found the following files:\n* %s", "\n* ".join(file_list))

    results = []
    for filename in tqdm(
        file_list,
        total=len(file_list),
        desc="GPS Imports",
        dynamic_ncols=True,
        position=0,
        ascii=False,
    ):
        try:
            file_id = _import_metadata(host, token, project_id, filename, file_type)
        except Exception:
            logger.error("Failed to import '%s'", os.path.basename(filename), exc_info=True)
        else:
            if file_id:
                results.append(file_id)

    return results
