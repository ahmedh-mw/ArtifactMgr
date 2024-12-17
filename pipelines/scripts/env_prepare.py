from utils import core
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

def parseArguments():
    parser = argparse.ArgumentParser(description='Prepare environemnt variables.', prog='env_prepare.py')
    parser.add_argument('-p', '--platform', required=True, help='ci platform')
    args = parser.parse_args()
    return args

def replace_env_variables(expression):
    pattern = re.compile(r'\$(\w+)')
    def replace_match(match):
        var_name = match.group(1)
        return os.environ.get(var_name, f'${var_name}')
    result = pattern.sub(replace_match, expression)
    return result

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
    
    print(variables_file_path)
    with open(variables_file_path, 'r') as variables_file:
        variables = json.load(variables_file)

    if args.platform == "jenkins":
        content = str()
        for key, value in variables.items():
            content += f"env.{key} = \"{value}\"\n"

        content += "return this"
        print(content)
        jenkinsFilePath = os.path.join(WORKSPACE_PATH, _GROOVY_ENVIRONMENT_VARIABLES_PATH)
        print(jenkinsFilePath)
        files.add_file(jenkinsFilePath, content)
    elif args.platform == "github":
        with open(os.environ['GITHUB_ENV'], 'a') as github_env:
            for key, value in variables.items():
                value = replace_env_variables(value)
                github_env.write(f"{key}={value}\n")
        
    logger.log(core.HEADER_LOG, core.SECTION_END)