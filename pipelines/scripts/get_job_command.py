from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
_MATLAB_JOB_COMMANDS_FILE_PATH = 'matlab_job_commands.m'
_SHELL_COMMANDS_FILE_PATH = 'shell_commands'

def parseArguments():
    parser = argparse.ArgumentParser(description='get job command.', prog='get_job_command.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parseArguments()
    dag = DAG(DAG_PATH)
    currentJob = dag.getJob(args.jobname)
    commands = "function varargout = matlab_job_commands()\n"
    for command in currentJob.Commands:
        commands += f"\t{command}\n"
    
    commands += "\tvarargout{1}=0;\n"
    commands += "end"

    jobCommandsFilePath = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _MATLAB_JOB_COMMANDS_FILE_PATH)
    files.add_file(jobCommandsFilePath, commands)

    shellCommandsFilePath = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _SHELL_COMMANDS_FILE_PATH)
    if os.name == 'nt':           # isWindows
        shellCommandsFilePath += ".bat"
    else:
        shellCommandsFilePath += ".sh"
    files.add_file(shellCommandsFilePath, f"matlab -batch {_MATLAB_JOB_COMMANDS_FILE_PATH}")