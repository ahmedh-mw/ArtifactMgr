"""
This module used to collect the output artifacts folders of a task
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
def collect_outputs(task_info, outputs_path):
    files.delete_folder(outputs_path)
    files.create_folder(outputs_path)
    for directory in task_info["outputs"]:
        dir_path = directory["path"]
        core.logger.info(f"{core.GROUP_START} Collect directory: {dir_path}")
        outputs_dir_path = os.path.join(outputs_path, dir_path)
        files.copy_folder(dir_path, outputs_dir_path)
        
def calculate_delta(inputs_path, outputs_path, delta_path):
    files.delete_folder(delta_path)
    files.create_folder(delta_path)

if __name__ == "__main__":
    core.logger.log(core.HEADER_LOG, core.SECTION_START)
    core.logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} task_collect_outputs")
    core.logger.log(core.HEADER_LOG, core.SECTION_END)
    
    settings_file_path = core.variables["settings"]
    task_id = core.variables["taskid"]
    outputs_path = core.variables["outputs"]
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
            collect_outputs(task_info, outputs_path)
            delta_path = core.variables.get("delta")
            if delta_path:
                inputs_path = core.variables.get("inputs")
                calculate_delta(inputs_path, outputs_path, delta_path)
            
    
    core.logger.log(core.HEADER_LOG, core.SECTION_END)
    
    # [out, error, returncode] = core.executeShellCommand("dir *", True)