"""
This module used to clean the output artifacts folders of a task
Parameters:
- settings: path of the seetings json file
- taskid: task id at the settings file
- ws (optional): workspace path where all output artifacts paths will be calculated

examples:
    python3 task_clean.py -settings "tasks.json" -taskid task1 -ws "D:\repos\ArtifactsManagement"

"""

from utils import core
from utils import files
import os
import json

core.logger.setLevel(core.logging.INFO)
def task_clean(task_info):
    for directory in task_info["outputs"]:
        dir_path = directory["path"]
        core.logger.info(f"{core.GROUP_START} Deleting directory: {dir_path}")
        files.delete_folder(dir_path)
        
if __name__ == "__main__":
    core.logger.log(core.HEADER_LOG, core.SECTION_START)
    core.logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} task_dryrun")
    core.logger.log(core.HEADER_LOG, core.SECTION_END)
    
    settings_file_path = core.variables["settings"]
    task_id = core.variables["taskid"]
    workspace = core.variables.get("ws")
    if workspace:
        os.chdir(workspace)
        
    if not os.path.exists(settings_file_path):
        core.logger.warning(f"Can not find settings file '{settings_file_path}'")
    else:
        with open(settings_file_path, 'r') as settings_file:
            tasks = json.load(settings_file)
        
        if tasks.get(task_id) is None:
            core.logger.warning(f"Can not find task '{task_id}' in the settings file '{settings_file_path}'")
        else:
            task_info = tasks[task_id]
            task_clean(task_info)
            
    
    core.logger.log(core.HEADER_LOG, core.SECTION_END)
    
    # [out, error, returncode] = core.executeShellCommand("dir *", True)