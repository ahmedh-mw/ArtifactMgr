from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()
_MATLAB_JOB_COMMANDS_FILE_PATH = 'matlab_job_commands.m'
_SHELL_COMMANDS_FILE_PATH = 'shell_commands'

def parseArguments():
    parser = argparse.ArgumentParser(description='Prepare job data and check job status.', prog='job_prepare.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    args = parser.parse_args()
    return args

def build_shell_commands(dag, currentJob):
    commands = "function varargout = matlab_job_commands()\n"
    commands += "\texitCode=0;\n"
    for command in currentJob.Commands:
        if "{{runprocess}}" in command:
            command = command.replace("{{runprocess}}", build_runprocess_command(dag, currentJob))
        commands += f"\t{command}\n"
    
    # commands += "\tvarargout{1}=0;\n"
    commands += "end"

    jobCommandsFilePath = os.path.join(WORKSPACE_PATH, _MATLAB_JOB_COMMANDS_FILE_PATH)
    files.add_file(jobCommandsFilePath, commands)

    shellCommandsFilePath = os.path.join(WORKSPACE_PATH, _SHELL_COMMANDS_FILE_PATH)
    if os.name == 'nt':           # isWindows
        shellCommandsFilePath += ".bat"
    else:
        shellCommandsFilePath += ".sh"
    files.add_file(shellCommandsFilePath, f"matlab -batch \"addpath(fileparts(pwd));{_MATLAB_JOB_COMMANDS_FILE_PATH}\"")
    files.set_execute_flag(shellCommandsFilePath)

def build_runprocess_command(dag, currentJob):
    arguments = []
    if len(currentJob.Tasks) > 0:
        arguments.append("Tasks = {'" + "','".join(currentJob.Tasks) + "'}")

    arguments.append(f"Process = '{dag.Pipeline.ProcessName}'")
    runrocessOptions = dag.Pipeline.RunprocessOptions or currentJob.RunrocessOptions
    if runrocessOptions:
        for arg, argValue in runrocessOptions.items():
            arguments.append(f"{arg}={str(argValue).lower()}")
    
    return f"[~,exitCode] = runprocess( {','.join(arguments)})"

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB PREPARE")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    
    logger.info(f"Prepare job data and check job status")
    dag = DAG(DAG_PATH)
    currentJob = dag.getJob(args.jobname)
    build_shell_commands(dag, currentJob)
        
    logger.log(core.HEADER_LOG, core.SECTION_END)