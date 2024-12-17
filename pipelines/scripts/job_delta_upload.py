from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()
_MATLAB_JOB_COMMANDS_FILE_PATH = 'derived/matlab_job_commands.m'
_SHELL_COMMANDS_FILE_PATH = 'derived/shell_commands'

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

    dag = DAG(DAG_PATH)
    # Move to _uploads_ => calculate delta => upload
    ####### Download:
    # 'Start' job:  - download only the 'End' job branch folder from the last succssful run
    #               - No merging will be required in this case
    # All other jobs:
    #               - download all input branches, input branches are the branches of all
    #               - predecessor jobs (using 'flow_predecessor_jobs' field)
    #######  Merge
    # Merge :       - Merge downloaded branches into a single current job branch if there 
    #               - are more than one branch downloaded
    #######  Move to project
    # Move to project:
    #               - Move the single downloaded branch or the merged one to the project folder

    ############################################################
    #           Move to _uploads_ folder
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Moving artifacts to _uploads_ folder")
    currentJob = dag.getJob(args.jobname)

    uploadPaths = dag.getJobUploadPaths(currentJob)
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