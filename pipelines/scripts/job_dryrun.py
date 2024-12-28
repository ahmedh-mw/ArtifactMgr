"""
This module used to simulate generating the output artifacts of a task
Parameters:
- settings: path of the seetings json file
- taskid: task id at the settings file
- ws (optional): workspace path where all output artifacts paths will be calculated

examples:
    python3 task_dryrun.py -settings "tasks.json" -taskid task1 -ws "D:\repos\ArtifactsManagement"

"""
from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()
_DRYRUN_FILE_NAME = "dryrun.txt"
_DUMMY_CONTENT = 'Dummy content'


def parseArguments():
    parser = argparse.ArgumentParser(description='Job dryrun.', prog='job_dryrun.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    args = parser.parse_args()
    return args

def dryrun(jobName):
    dag = DAG(getDagPath())
    job = dag.getJob(jobName)
    
    for outputPath in job.Outputs:
        dir_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, outputPath)
        logger.info(f"{core.GROUP_START} Building directory: {dir_path}")
        files.create_folder(dir_path)
        full_path = os.path.join(dir_path, _DRYRUN_FILE_NAME)
        files.add_file(full_path, _DUMMY_CONTENT)
        
    # for outputPath, dirFiles in job.Outputs.items():
        # dir_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, outputPath)
        # logger.info(f"{core.GROUP_START} Building directory: {dir_path}")
        # files.create_folder(dir_path)
        # for file in dirFiles:
        #     full_path = os.path.join(dir_path, file)
        #     logger.info(f"Adding file: {full_path}")
        #     file_dir_path = os.path.dirname(full_path)
        #     files.create_folder(file_dir_path)
        #     files.add_file(full_path, _DUMMY_CONTENT)

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB DRYRUN")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    logger.info(args)
        
    dryrun(args.jobname)
    
    core.logger.log(core.HEADER_LOG, core.SECTION_END)