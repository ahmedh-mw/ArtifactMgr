from utils import core
from dag import DAG, Utils
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

def build_shell_commands(pipeline, currentJob):
    commands = "function varargout = matlab_job_commands()\n"
    projectPath = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER)
    commands += f"\tcd('{projectPath}');\n"
    commands += "\texitCode=0;\n"
    for command in currentJob['Commands']:
        if "{{runprocess}}" in command:
            command = command.replace("{{runprocess}}", build_runprocess_command(pipeline, currentJob))
        elif "{{generate-report}}" in command:
            command = command.replace("{{generate-report}}", build_generate_report_command(pipeline, currentJob))
        elif "{{mergeDmrFiles}}" in command:
            command = command.replace("{{mergeDmrFiles}}", build_mergeDmrFiles_command(pipeline, currentJob))
        elif "{{conditionalUpdateArtifacts}}" in command:
            command = command.replace("{{conditionalUpdateArtifacts}}", build_conditionalUpdateArtifacts_command(pipeline, currentJob))
        elif "{{checkOutdatedResults}}" in command:
            command = command.replace("{{checkOutdatedResults}}", build_checkOutdatedResults_command        (pipeline, currentJob))
        if command:
            commands += f"\t{command}\n"
    commands += "end"

    jobCommandsFilePath = os.path.join(WORKSPACE_PATH, _MATLAB_JOB_COMMANDS_FILE_PATH)
    files.add_file(jobCommandsFilePath, commands)

    shellCommandsFilePath = os.path.join(WORKSPACE_PATH, _SHELL_COMMANDS_FILE_PATH)
    if os.name == 'nt':           # isWindows
        shellCommandsFilePath += ".bat"
    else:
        shellCommandsFilePath += ".sh"
    
    pipelineOptions = pipeline['Options']
    if pipelineOptions['MatlabStartupOptions'] is None:
        shellCommand = f"{pipelineOptions['MatlabLaunchCmd']}"
    else:
        shellCommand = f"{pipelineOptions['MatlabLaunchCmd']} {pipelineOptions['MatlabStartupOptions']}"
    
    if pipelineOptions['AddBatchStartupOption']:
        shellCommand += " -batch"
    shellCommand += f" \"{_MATLAB_JOB_COMMANDS_FILE_NAME}\""
    files.add_file(shellCommandsFilePath, shellCommand)
    
    files.set_execute_flag(shellCommandsFilePath)

def build_runprocess_command(pipeline, currentJob):
    result = ""
    if len(currentJob['Tasks']) > 0 or len(pipeline['Jobs'].keys()) == 1:
        arguments = []
        tasks = Utils.getList(currentJob, 'Tasks')
        if len(tasks) > 0:
            arguments.append("Tasks = {'" + "','".join(tasks) + "'}")

        arguments.append(f"Process = '{pipeline['ProcessName']}'")
        runrocessOptions = pipeline['Options']['RunprocessCommandOptions']
        if runrocessOptions:
            for arg, argValue in runrocessOptions.items():
                arguments.append(f"{arg}={str(argValue).lower()}")
        result = f"[~,exitCode]=runprocess( {','.join(arguments)});"
    return result

def build_generate_report_command(pipeline, currentJob):
    command = ""
    if pipeline['Options']['GenerateReport'] == True and currentJob['IsEndJob'] == True:
        arguments = []
        arguments.append(f"Process = '{pipeline['ProcessName']}'")
        arguments.append(f"Format = '{pipeline['ReportFormat']}'")
        arguments.append(f"OutputPath = '{pipeline['ReportPath']}'")
        command = f"rptObj=padv.ProcessAdvisorReportGenerator({','.join(arguments)});\n"
        command += f"\trptObj.generateReport();"
    return command

def build_mergeDmrFiles_command(pipeline, currentJob):
    command = ""
    if currentJob['IsMergingJob'] == True:
        command = f"padv.internal.mergeDmrFiles(SequenceFilePath = '../_dmr_merging_/dmrsMergeSequence.json', EnableDiagnostics=true)"
    return command

def build_conditionalUpdateArtifacts_command(pipeline, currentJob):
    command = ""
    tasks = Utils.getList(currentJob, 'Tasks')
    if len(pipeline['Jobs'].keys()) > 1 and len(tasks) == 0:
        command = f"padv.internal.AlmArtifactHelper.conditionalUpdateArtifacts()"
    return command

def build_checkOutdatedResults_command(pipeline, currentJob):
    command = ""
    if currentJob['IsEndJob'] == True and currentJob['IsMergingJob'] == True:
        command = f"padv.internal.checkOutdatedResults(CurrentProject=cp, ProcessName='CIPipeline');"
    return command

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB PREPARE")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    
    logger.info(f"Prepare job data and check job status")
    print(getDagPath())
    dag = DAG(getDagPath())
    pipeline = dag.getPipeline()
    currentJob = dag.getJob(args.jobname)
    build_shell_commands(pipeline, currentJob)
        
    logger.log(core.HEADER_LOG, core.SECTION_END)