from services import *
import os 
import re

# Original string with special characters
SPECIAL_CHARACTERS = r'[^A-Za-z0-9\s]'

# Workspace
WORKSPACE_PATH_KEY = os.environ.get('WORKSPACE_PATH_KEY')
if WORKSPACE_PATH_KEY is None:
    WORKSPACE_PATH_KEY = 'WORKSPACE'

WORKSPACE_PATH = os.environ.get(WORKSPACE_PATH_KEY)
if WORKSPACE_PATH is None:
    WORKSPACE_PATH = 'C:\\Data\\repos\\gh\\ArtifactMgr'

DONWLOADS_FOLDER = os.environ.get('DONWLOADS_FOLDER')
if DONWLOADS_FOLDER is None:
    DONWLOADS_FOLDER = '_downloads_'

DMR_MERGING_FOLDER = os.environ.get('DMR_MERGING_FOLDER')
if DMR_MERGING_FOLDER is None:
    DMR_MERGING_FOLDER = '_dmr_merging_'

UPLOADS_FOLDER = os.environ.get('UPLOADS_FOLDER')
if UPLOADS_FOLDER is None:
    UPLOADS_FOLDER = '_uploads_'

SOURCECODE_FOLDER = os.environ.get('SOURCECODE_FOLDER')
if SOURCECODE_FOLDER is None:
    SOURCECODE_FOLDER = ''

PROJECT_NAME = os.environ.get('PROJECT_NAME')
if PROJECT_NAME is None:
    PROJECT_NAME = "Artifactory/bslcicd"

REPO_BRANCH_NAME = os.environ.get('REPO_BRANCH_NAME')
if REPO_BRANCH_NAME is None:
    REPO_BRANCH_NAME = "main"
else:
    REPO_BRANCH_NAME = re.sub(SPECIAL_CHARACTERS, '', REPO_BRANCH_NAME)

CURRENT_RUN_ID = os.environ.get('CURRENT_RUN_ID')
if CURRENT_RUN_ID is None:
    CURRENT_RUN_ID = "None"

INCREMENTAL_PIPELINE_ENABLED = os.environ.get('INCREMENTAL_PIPELINE_ENABLED')
if INCREMENTAL_PIPELINE_ENABLED is None:
    INCREMENTAL_PIPELINE_ENABLED = "true"

if os.name == 'nt':           # isWindows
    NETWORK_STORAGE_PATH = "C:\\Data\\artifactory"
else:
    NETWORK_STORAGE_PATH = "/home/ahmedh/artifactory"
artifactsService = NetworkStorage(NETWORK_STORAGE_PATH, INCREMENTAL_PIPELINE_ENABLED == 'true')
# artifactsService = Artifactory(root_folder)

def getDagPath():
    dagPath = os.environ.get('DAG_PATH')
    if dagPath is None:
        dagPath = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, os.environ.get('DAG_RELATIVE_PATH'))
    return dagPath