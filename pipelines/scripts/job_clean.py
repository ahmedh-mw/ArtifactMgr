from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()

if __name__ == "__main__":
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB CLEAN")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    
    logger.info(f"Clean job workspace")

    workspace_items = os.listdir(WORKSPACE_PATH)
    for item in workspace_items:
        if item == SOURCECODE_FOLDER:
            continue
        else:
            item_path = os.path.join(WORKSPACE_PATH, item)
            if os.path.isfile(item_path):
                files.delete_file(item_path)
            else:
                files.delete_folder(item_path)
    
    logger.log(core.HEADER_LOG, core.SECTION_END)