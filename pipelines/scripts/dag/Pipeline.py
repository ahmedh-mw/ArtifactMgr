import sys, os
sys.path.append(os.path.abspath(str()))

from .Utils import Utils
from collections import defaultdict
import logging
logger = logging.getLogger()

class Pipeline:
    _REPO_FALLBACK_BRANCHES_FIELD = 'RepoFallbackBranches'
    _RUNNER_TYPE_FIELD = 'RUNNER_TYPE'
    _RUNNER_LABEL_FIELD = 'RUNNER_LABEL'
    _IMAGE_TAG_FIELD = 'IMAGE_TAG'
    _IMAGE_ARGS_FIELD = 'IMAGE_ARGS'
    _USE_MATLAB_PLUGIN_FIELD = 'USE_MATLAB_PLUGIN'

    _CONTINUE_ON_ERROR_FIELD = 'CONTINUE_ON_ERROR'
    _SUBMODULES_MODE_FIELD = 'SUBMODULES_MODE'
    _INCREMENTAL_PIPELINE_ENABLED_FIELD = 'IncrementalPipelineEnabled'
    _MATLAB_INSTALLATION_PATH_FIELD = 'MatlabInstrallationPath'
    _MATLAB_LAUNCH_CMD_FIELD = 'MatlabLaunchCmd'
    _MATLAB_STARTUP_OPTIONS_FIELD = 'MatlabStartupOptions'
    _ADD_BATCH_STARTUP_OPTIONS_FIELD = 'AddBatchStartupOption'
    
    _PROCESS_NAME_FIELD = 'ProcessName'
    _GENERATE_REPORT_FIELD = 'GenerateReport'
    _REPORT_PATH_FIELD = 'ReportPath'
    _REPORT_FORMAT_FIELD = 'ReportFormat'

    _ENABLE_ARTIFACTS_COLLECTION_FIELD = 'EnableArtifactCollection'
    _RUN_PROCESS_OPTIONS_DIC = 'RunprocessOptions'
    
    def __init__(self, pipelineObject):
        self._pipelineObject = pipelineObject
        self.RepoFallbackBranches = Utils.getList(pipelineObject, self._REPO_FALLBACK_BRANCHES_FIELD)
        self.RUNNER_TYPE = self._pipelineObject.get(self._RUNNER_TYPE_FIELD)
        self.RUNNER_LABEL = self._pipelineObject.get(self._RUNNER_LABEL_FIELD)
        self.IMAGE_TAG = self._pipelineObject.get(self._IMAGE_TAG_FIELD)
        self.IMAGE_ARGS = self._pipelineObject.get(self._IMAGE_ARGS_FIELD)
                
        self.CONTINUE_ON_ERROR = Utils.getBoolean(pipelineObject, self._CONTINUE_ON_ERROR_FIELD, False)
        self.SUBMODULES_MODE = Utils.getBoolean(pipelineObject, self._SUBMODULES_MODE_FIELD, False)
        self.USE_MATLAB_PLUGIN = Utils.getBoolean(pipelineObject, self._USE_MATLAB_PLUGIN_FIELD, False)
        self.IncrementalPipelineEnabled = Utils.getBoolean(pipelineObject, self._INCREMENTAL_PIPELINE_ENABLED_FIELD, True)
        self.MatlabInstrallationPath = self._pipelineObject.get(self._MATLAB_INSTALLATION_PATH_FIELD)
        self.MatlabLaunchCmd = self._pipelineObject.get(self._MATLAB_LAUNCH_CMD_FIELD)
        self.MatlabStartupOptions = self._pipelineObject.get(self._MATLAB_STARTUP_OPTIONS_FIELD)
        self.AddBatchStartupOption = Utils.getBoolean(pipelineObject, self._ADD_BATCH_STARTUP_OPTIONS_FIELD, True)
        
        self.ProcessName = self._pipelineObject.get(self._PROCESS_NAME_FIELD)
        self.GenerateReport = Utils.getBoolean(pipelineObject, self._GENERATE_REPORT_FIELD, True)
        self.ReportPath = self._pipelineObject.get(self._REPORT_PATH_FIELD)
        self.ReportFormat = self._pipelineObject.get(self._REPORT_FORMAT_FIELD)

        self.EnableArtifactCollection = Utils.getBoolean(pipelineObject, self._ENABLE_ARTIFACTS_COLLECTION_FIELD, True)
        
        self.RunprocessOptions = Utils.getDic(pipelineObject, self._RUN_PROCESS_OPTIONS_DIC, {})
        self.OutputsPaths = None