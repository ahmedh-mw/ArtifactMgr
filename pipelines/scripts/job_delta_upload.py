from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()

_DERIVED_FOLDER = 'derived'

def parseArguments():
    parser = argparse.ArgumentParser(description='Calculate delta artifacts generated by current job then upload artifacts.'
                                     , prog='job_delta_upload.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    parser.add_argument('-e', '--errordetected', required=True, help='error detected flag')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB DELTA UPLOAD")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    logger.info(args)

    dag = DAG(getDagPath())
    # Move to _uploads_ => calculate delta => upload
    ############################################################
    #           Move to _uploads_ folder
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Moving artifacts to _uploads_ folder")
    currentJob = dag.getJob(args.jobname)

    uploadPaths = dag.getJobUploadPaths(currentJob)
    if _DERIVED_FOLDER not in uploadPaths:
        uploadPaths.append(_DERIVED_FOLDER)
    uploadPaths.sort()
    logger.info(f"uploadPaths: {uploadPaths}")

    srcFolder = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER)
    uploadsFolder = os.path.join(WORKSPACE_PATH, UPLOADS_FOLDER)
    files.move_paths(srcFolder, uploadsFolder, uploadPaths)

    ############################################################
    #           Calculate delta
    ############################################################
    # Enhancement after the proof of concept

    ############################################################
    #           Upload
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Uploading artifacts")
    relativeRepoBranchPath = os.path.join(PROJECT_NAME, REPO_BRANCH_NAME)
    artifactsService.upload(uploadsFolder, relativeRepoBranchPath, CURRENT_RUN_ID, currentJob.BranchName)

    if currentJob.IsEndJob and args.errordetected == 'false':
        logger.info(f"Update last successful run id to {CURRENT_RUN_ID}")
        artifactsService.updateLastSuccessfulRunId(relativeRepoBranchPath, CURRENT_RUN_ID)
        
    logger.log(core.HEADER_LOG, core.SECTION_END)