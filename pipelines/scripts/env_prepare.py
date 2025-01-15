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
_ENVIRONMENT_GUTHUB_VARIABLES_PATH = 'pipelines/templates/vars.github.json'
_ENVIRONMENT_LOCAL_VARIABLES_PATH = 'pipelines/templates/vars.local.json'
_GROOVY_ENVIRONMENT_VARIABLES_PATH = 'vars.groovy'
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

def loadVariableKey(variables, key, value):
    if value is not None:
        if isinstance(value, bool):
            variables[key] = str(value).lower()
        elif isinstance(value, str):
            variables[key] = value

def loadPipelineVariables(variables, dag, platform):
    pipelineOptions = dag.getPipeline()['Options']
    if platform == "jenkins":
        loadVariableKey(variables, 'RUNNER_TYPE', 'default')
        loadVariableKey(variables, 'RUNNER_LABEL', pipelineOptions.get('AgentLabel'))
        loadVariableKey(variables, 'IMAGE_TAG', pipelineOptions.get('IMAGE_TAG'))
        loadVariableKey(variables, 'CONTINUE_ON_ERROR', not pipelineOptions.get('StopOnStageFailure'))
        loadVariableKey(variables, 'SUBMODULES_MODE', pipelineOptions.get('SUBMODULES_MODE'))
        loadVariableKey(variables, 'USE_MATLAB_PLUGIN', pipelineOptions['UseMatlabPlugin'])
    elif platform == "github":
        loadVariableKey(variables, 'RUNNER_TYPE', pipelineOptions['RUNNER_TYPE'])
        loadVariableKey(variables, 'RUNNER_LABEL', pipelineOptions['RUNNER_LABEL'])
        loadVariableKey(variables, 'IMAGE_TAG', pipelineOptions['IMAGE_TAG'])
        loadVariableKey(variables, 'CONTINUE_ON_ERROR', pipelineOptions['CONTINUE_ON_ERROR'])
        loadVariableKey(variables, 'SUBMODULES_MODE', pipelineOptions['SUBMODULES_MODE'])
        loadVariableKey(variables, 'USE_MATLAB_PLUGIN', pipelineOptions['USE_MATLAB_PLUGIN'])
    else:
        loadVariableKey(variables, 'RUNNER_TYPE', 'default')
        loadVariableKey(variables, 'RUNNER_LABEL', pipelineOptions.get('AgentLabel'))
        loadVariableKey(variables, 'IMAGE_TAG', pipelineOptions.get('IMAGE_TAG'))
        loadVariableKey(variables, 'CONTINUE_ON_ERROR', not pipelineOptions.get('StopOnStageFailure'))
        loadVariableKey(variables, 'SUBMODULES_MODE', pipelineOptions.get('SUBMODULES_MODE'))
        loadVariableKey(variables, 'USE_MATLAB_PLUGIN', pipelineOptions['UseMatlabPlugin'])
    
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
    else:
        variables_file_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _ENVIRONMENT_LOCAL_VARIABLES_PATH)
    
    with open(variables_file_path, 'r') as variables_file:
        variables = json.load(variables_file)

    # Use dag relative path from env variables if exists otherwuse use it from variables
    if os.environ.get(_DAG_RELATIVE_PATH_FIELD) is None:
        os.environ[_DAG_RELATIVE_PATH_FIELD] = variables[_DAG_RELATIVE_PATH_FIELD]
    
    dag = DAG(getDagPath())
    loadPipelineVariables(variables, dag, args.platform)

    matlabInstrallationPath = dag.getPipeline()['Options']['MatlabInstrallationPath']
    if args.platform == "jenkins":
        content = str()
        if matlabInstrallationPath:
            if os.name == 'nt':           # isWindows
                content += f"env.PATH = \"{matlabInstrallationPath};$PATH\"\n"
            else:
                content += f"env.PATH = \"{matlabInstrallationPath}:$PATH\"\n"
                    
        for key, value in variables.items():
            content += f"env.{key} = \"{value}\"\n"
            
        content += "return this"
        jenkinsFilePath = os.path.join(WORKSPACE_PATH, _GROOVY_ENVIRONMENT_VARIABLES_PATH)
        files.add_file(jenkinsFilePath, content)
    elif args.platform == "github":
        with open(os.environ['GITHUB_ENV'], 'a') as github_env:
            if matlabInstrallationPath:
                envPATH = os.environ.get('PATH')
                if os.name == 'nt':           # isWindows
                    github_env.write(f"PATH={matlabInstrallationPath};{envPATH}\n")
                else:
                    github_env.write(f"PATH={matlabInstrallationPath}:{envPATH}\n")
                
            for key, value in variables.items():
                value = replace_env_variables(value)
                github_env.write(f"{key}={value}\n")
    else:
        for key, value in variables.items():
            print(f"$env:{key}='{value}'")
        
    logger.log(core.HEADER_LOG, core.SECTION_END)