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

def loadVariableKey(variables, key, value):
    if value is not None:
        if isinstance(value, bool):
            variables[key] = str(value).lower()
        elif isinstance(value, str):
            variables[key] = value

def loadPipelineVariables(variables, dag):
    loadVariableKey(variables, dag.Pipeline._RUNNER_TYPE_FIELD, dag.Pipeline.RUNNER_TYPE)
    loadVariableKey(variables, dag.Pipeline._RUNNER_LABEL_FIELD, dag.Pipeline.RUNNER_LABEL)
    loadVariableKey(variables, dag.Pipeline._IMAGE_TAG_FIELD, dag.Pipeline.IMAGE_TAG)
    loadVariableKey(variables, dag.Pipeline._IMAGE_ARGS_FIELD, dag.Pipeline.IMAGE_ARGS)
    loadVariableKey(variables, dag.Pipeline._CONTINUE_ON_ERROR_FIELD, dag.Pipeline.CONTINUE_ON_ERROR)
    loadVariableKey(variables, dag.Pipeline._SUBMODULES_MODE_FIELD, dag.Pipeline.SUBMODULES_MODE)
    loadVariableKey(variables, dag.Pipeline._USE_MATLAB_PLUGIN_FIELD, dag.Pipeline.USE_MATLAB_PLUGIN)
    loadVariableKey(variables, dag.Pipeline._INCREMENTAL_PIPELINE_ENABLED_FIELD, dag.Pipeline.IncrementalPipelineEnabled)
    loadVariableKey(variables, dag.Pipeline._GENERATE_REPORT_FIELD, dag.Pipeline.GenerateReport)
    loadVariableKey(variables, dag.Pipeline._ENABLE_ARTIFACTS_COLLECTION_FIELD, dag.Pipeline.EnableArtifactCollection)
    
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

    print(variables)
    os.environ[_DAG_RELATIVE_PATH_FIELD] = variables[_DAG_RELATIVE_PATH_FIELD]
    print(os.environ[_DAG_RELATIVE_PATH_FIELD])
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