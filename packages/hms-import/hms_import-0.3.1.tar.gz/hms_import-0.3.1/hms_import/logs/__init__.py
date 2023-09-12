import logging
import os

import tator

logger = logging.getLogger(__name__)

def main(
    host: str,
    token: str,
    log_file_type_id: int,
    log_filename: str,
) -> bool:
    """
    :host: The Tator domain
    :token: The REST API token
    :log_file_type_id: The unique ID of the type of file to create for storing GPS data
    :log_filename: The name of an existing log file to upload to Tator
    :returns: True if the import was successful, False if any part of it fails
    """
    tator_api = tator.get_api(host=host, token=token)
    r = None
    try:
        for p, r in tator.util.upload_generic_file(api=tator_api, file_type=log_file_type_id, path=log_filename, description="Log file from hms-import", name=os.path.basename(log_filename), timeout=120):
            logger.info("Upload progress: %.1f%%", p)
    except Exception:
        logger.error("Exception while uploading log file", exc_info=True)

    if r:
        logger.info(r)
        return True
    return False
