import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')
from utils import core
from dag import DAG
from dag import DAGMerger
from utils import files
import os
import json
import logging
from config import *

logger = logging.getLogger()
logger.setLevel(core.logging.DEBUG)
_ENVIRONMENT_JENKINS_VARIABLES_PATH = 'pipelines/templates/vars.local.json'
_DAG_RELATIVE_PATH_FIELD = 'DAG_RELATIVE_PATH'
        
if __name__ == "__main__":
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} TEST")
    logger.log(core.HEADER_LOG, core.SECTION_END)

    variables_file_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _ENVIRONMENT_JENKINS_VARIABLES_PATH)
    with open(variables_file_path, 'r') as variables_file:
        variables = json.load(variables_file)

    os.environ[_DAG_RELATIVE_PATH_FIELD] = variables[_DAG_RELATIVE_PATH_FIELD]
    dag = DAG("C:/Data/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.complex.json")

    dagMerger = DAGMerger(dag.Branches)
    dagMerger.getMergingSequence(["job4", "job9", "job6"])

    with open("data.json", "w") as outfile:
        json.dump(dag.dictEncode(), outfile, indent=4)
    logger.log(core.HEADER_LOG, core.SECTION_END)