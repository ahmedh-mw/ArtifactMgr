from utils import core
from dag import DAG
from utils import files
import os
import json
import argparse
import logging
from config import *

logger = logging.getLogger()
_ENVIRONMENT_JENKINS_VARIABLES_PATH = 'pipelines/templates/vars.jenkins.json'
_GROOVY_ENVIRONMENT_VARIABLES_PATH = 'vars.groovy'
_ENVIRONMENT_GUTHUB_VARIABLES_PATH = 'pipelines/templates/vars.github.json'
_DAG_RELATIVE_PATH_FIELD = 'DAG_RELATIVE_PATH'

def parseArguments():
    parser = argparse.ArgumentParser(description='Prepare environemnt variables.', prog='env_prepare.py')
    parser.add_argument('-p', '--platform', required=True, help='ci platform')
    args = parser.parse_args()
    return args

def replace_env_variables(expression):
    if type(expression) != str:
        return expression
    pattern = re.compile(r'\$(\w+)')
    def replace_match(match):
        var_name = match.group(1)
        return os.environ.get(var_name, f'${var_name}')
    result = pattern.sub(replace_match, expression)
    return result

def loadPipelineVariables(variables, dag):
    if dag.Pipeline.RUNNER_TYPE: 
        variables[dag.Pipeline._RUNNER_TYPE_FIELD] = dag.Pipeline.RUNNER_TYPE
    if dag.Pipeline.RUNNER_LABEL: 
        variables[dag.Pipeline._RUNNER_LABEL_FIELD] = dag.Pipeline.RUNNER_LABEL
    if dag.Pipeline.IMAGE_TAG: 
        variables[dag.Pipeline._IMAGE_TAG_FIELD] = dag.Pipeline.IMAGE_TAG
    if dag.Pipeline.IMAGE_ARGS: 
        variables[dag.Pipeline._IMAGE_ARGS_FIELD] = dag.Pipeline.IMAGE_ARGS
    if dag.Pipeline.CONTINUE_ON_ERROR: 
        variables[dag.Pipeline._CONTINUE_ON_ERROR_FIELD] = str(dag.Pipeline.CONTINUE_ON_ERROR).lower()
    if dag.Pipeline.SUBMODULES_MODE: 
        variables[dag.Pipeline._SUBMODULES_MODE_FIELD] = dag.Pipeline.SUBMODULES_MODE
    if dag.Pipeline.IncrementalPipelineEnabled:
        variables[dag.Pipeline._INCREMENTAL_PIPELINE_ENABLED_FIELD] = str(dag.Pipeline.IncrementalPipelineEnabled).lower()
    if dag.Pipeline.MatlabInstrallationPath: 
        variables[dag.Pipeline._MATLAB_INSTALLATION_PATH_FIELD] = dag.Pipeline.MatlabInstrallationPath
    if dag.Pipeline.MatlabLaunchCmd: 
        variables[dag.Pipeline._MATLAB_LAUNCH_CMD_FIELD] = dag.Pipeline.MatlabLaunchCmd
    if dag.Pipeline.MatlabLaunchCmd: 
        variables[dag.Pipeline._MATLAB_STARTUP_OPTIONS_FIELD] = dag.Pipeline.MatlabStartupOptions
    if dag.Pipeline.AddBatchStartupOption: 
        variables[dag.Pipeline._ADD_BATCH_STARTUP_OPTIONS_FIELD] = str(dag.Pipeline.AddBatchStartupOption).lower()
    if dag.Pipeline.ProcessName: 
        variables[dag.Pipeline._PROCESS_NAME_FIELD] = dag.Pipeline.ProcessName
    if dag.Pipeline.GenerateReport: 
        variables[dag.Pipeline._GENERATE_REPORT] = str(dag.Pipeline.GenerateReport).lower()
    if dag.Pipeline.ReportPath: 
        variables[dag.Pipeline._REPORT_PATH_FIELD] = dag.Pipeline.ReportPath
    if dag.Pipeline.ReportFormat: 
        variables[dag.Pipeline._REPORT_FORMAT_FIELD] = dag.Pipeline.ReportFormat
    if dag.Pipeline.EnableArtifactCollection: 
        variables[dag.Pipeline._ENABLE_ARTIFACTS_COLLECTION_FIELD] = str(dag.Pipeline.EnableArtifactCollection).lower()
    
if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} ENVIRONMENT VARIABLES PREPARE")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    
    logger.info(f"Prepare environemnt variables")
    
    if args.platform == "jenkins":
        variables_file_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _ENVIRONMENT_JENKINS_VARIABLES_PATH)
    elif args.platform == "github":
        variables_file_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _ENVIRONMENT_GUTHUB_VARIABLES_PATH)
    
    with open(variables_file_path, 'r') as variables_file:
        variables = json.load(variables_file)

    os.environ[_DAG_RELATIVE_PATH_FIELD] = variables[_DAG_RELATIVE_PATH_FIELD]
    dag = DAG(getDagPath())
    loadPipelineVariables(variables, dag)

    if args.platform == "jenkins":
        content = str()
        if dag.Pipeline.MatlabInstrallationPath:
            if os.name == 'nt':           # isWindows
                content += f"env.PATH = \"{dag.Pipeline.MatlabInstrallationPath};$PATH\"\n"
            else:
                content += f"env.PATH = \"{dag.Pipeline.MatlabInstrallationPath}:$PATH\"\n"
                    
        for key, value in variables.items():
            content += f"env.{key} = \"{value}\"\n"
            
        content += "return this"
        jenkinsFilePath = os.path.join(WORKSPACE_PATH, _GROOVY_ENVIRONMENT_VARIABLES_PATH)
        files.add_file(jenkinsFilePath, content)
    elif args.platform == "github":
        with open(os.environ['GITHUB_ENV'], 'a') as github_env:
            if dag.Pipeline.MatlabInstrallationPath:
                envPATH = os.environ.get('PATH')
                if os.name == 'nt':           # isWindows
                    github_env.write(f"PATH={dag.Pipeline.MatlabInstrallationPath};{envPATH}\n")
                else:
                    github_env.write(f"PATH={dag.Pipeline.MatlabInstrallationPath}:{envPATH}\n")
                
            for key, value in variables.items():
                value = replace_env_variables(value)
                github_env.write(f"{key}={value}\n")
        
    logger.log(core.HEADER_LOG, core.SECTION_END)