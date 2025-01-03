from utils import core
from dag import DAG
from utils import files
import os
import argparse
import logging
from config import *

logger = logging.getLogger()
_MATLAB_JOB_COMMANDS_FILE_NAME = 'matlab_job_commands'
_MATLAB_JOB_COMMANDS_FILE_PATH = f"{_MATLAB_JOB_COMMANDS_FILE_NAME}.m"
_SHELL_COMMANDS_FILE_PATH = 'shell_commands'

def parseArguments():
    parser = argparse.ArgumentParser(description='Prepare job data and check job status.', prog='job_prepare.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    args = parser.parse_args()
    return args

def build_shell_commands(dag, currentJob):
    commands = "function varargout = matlab_job_commands()\n"
    projectPath = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER)
    commands += f"\tcd('{projectPath}');\n"
    commands += "\texitCode=0;\n"
    for command in currentJob.Commands:
        if "{{runprocess}}" in command:
            command = command.replace("{{runprocess}}", build_runprocess_command(dag, currentJob))
        elif "{{generate-report}}" in command:
            command = command.replace("{{generate-report}}", build_generate_report_command(dag))
            
        commands += f"\t{command}\n"
    commands += "end"

    jobCommandsFilePath = os.path.join(WORKSPACE_PATH, _MATLAB_JOB_COMMANDS_FILE_PATH)
    files.add_file(jobCommandsFilePath, commands)

    shellCommandsFilePath = os.path.join(WORKSPACE_PATH, _SHELL_COMMANDS_FILE_PATH)
    if os.name == 'nt':           # isWindows
        shellCommandsFilePath += ".bat"
    else:
        shellCommandsFilePath += ".sh"
    
    if dag.Pipeline.MatlabStartupOptions is None:
        shellCommand = f"{dag.Pipeline.MatlabLaunchCmd}"
    else:
        shellCommand = f"{dag.Pipeline.MatlabLaunchCmd} {dag.Pipeline.MatlabStartupOptions}"
    
    if dag.Pipeline.AddBatchStartupOption:
        shellCommand += " -batch"
    shellCommand += f" \"{_MATLAB_JOB_COMMANDS_FILE_NAME}\""
    files.add_file(shellCommandsFilePath, shellCommand)
    
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
    
    return f"runprocess( {','.join(arguments)})"

def build_generate_report_command(dag):
    arguments = []
    arguments.append(f"Process = '{dag.Pipeline.ProcessName}'")
    arguments.append(f"Format = '{dag.Pipeline.ReportFormat}'")
    arguments.append(f"OutputPath = '{dag.Pipeline.ReportPath}'")
    command = f"rptObj=padv.ProcessAdvisorReportGenerator({','.join(arguments)});\n"
    command += f"\trptObj.generateReport()"
    return command

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB PREPARE")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    
    logger.info(f"Prepare job data and check job status")
    dag = DAG(getDagPath())
    currentJob = dag.getJob(args.jobname)
    build_shell_commands(dag, currentJob)
        
    logger.log(core.HEADER_LOG, core.SECTION_END)