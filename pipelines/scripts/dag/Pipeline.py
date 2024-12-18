import sys, os
sys.path.append(os.path.abspath(str()))

from .Utils import Utils
from collections import defaultdict
import logging
logger = logging.getLogger()

class Pipeline:
    _RUNNER_TYPE_FIELD = 'RunnerType'
    _RUNNER_LABEL_FIELD = 'RunnerLabel'
    _IMAGE_TAG_FIELD = 'ImageTag'
    _IMAGE_ARGS_FIELD = 'ImageArgs'

    _CONTINUE_ON_ERROR_FIELD = 'ContinueOnError'
    _SUBMODULES_MODE_FIELD = 'SubmodulesMode'
    _INCREMENTAL_PIPELINE_ENABLED_FIELD = 'IncrementalPipelineEnabled'
    _MATLAB_INSTALLATION_PATH_FIELD = 'MatlabInstrallationPath'
    _MATLAB_LAUNCH_CMD_FIELD = 'MatlabLaunchCmd'
    _MATLAB_STARTUP_OPTIONS_FIELD = 'MatlabStartupOptions'
    _ADD_BATCH_STARTUP_OPTIONS_FIELD = 'AddBatchStartupOption'
    
    _PROCESS_NAME_FIELD = 'ProcessName'
    _GENERATE_REPORT = 'GenerateReport'
    _REPORT_PATH_FIELD = 'ReportPath'
    _REPORT_FORMAT_FIELD = 'ReportFormat'

    _ENABLE_ARTIFACTS_COLLECTION_FIELD = 'EnableArtifactCollection'
    _RUN_PROCESS_OPTIONS_DIC = 'RunprocessOptions'
    
    def __init__(self, pipelineObject):
        self._pipelineObject = pipelineObject

        self.RunnerType = self._pipelineObject.get(self._RUNNER_TYPE_FIELD)
        self.RunnerLabel = self._pipelineObject.get(self._RUNNER_LABEL_FIELD)
        self.ImageTag = self._pipelineObject.get(self._IMAGE_TAG_FIELD)
        self.ImageArgs = self._pipelineObject.get(self._IMAGE_ARGS_FIELD)
                
        self.ContinueOnError = Utils.getBoolean(pipelineObject, self._pipelineObject.get(self._CONTINUE_ON_ERROR_FIELD), False)
        self.SubmodulesMode = Utils.getBoolean(pipelineObject, self._pipelineObject.get(self._SUBMODULES_MODE_FIELD), False)
        self.IncrementalPipelineEnabled = Utils.getBoolean(pipelineObject, self._pipelineObject.get(self._INCREMENTAL_PIPELINE_ENABLED_FIELD), True)
        self.MatlabInstrallationPath = self._pipelineObject.get(self._MATLAB_INSTALLATION_PATH_FIELD)
        self.MatlabLaunchCmd = self._pipelineObject.get(self._MATLAB_LAUNCH_CMD_FIELD)
        self.MatlabStartupOptions = self._pipelineObject.get(self._MATLAB_STARTUP_OPTIONS_FIELD)
        self.AddBatchStartupOption = self._pipelineObject.get(self._ADD_BATCH_STARTUP_OPTIONS_FIELD)
        
        self.ProcessName = self._pipelineObject.get(self._PROCESS_NAME_FIELD)
        self.GenerateReport = Utils.getBoolean(pipelineObject, self._pipelineObject[self._GENERATE_REPORT], True)
        self.ReportPath = self._pipelineObject.get(self._REPORT_PATH_FIELD)
        self.ReportFormat = self._pipelineObject.get(self._REPORT_FORMAT_FIELD)

        self.EnableArtifactCollection = Utils.getBoolean(pipelineObject, self._pipelineObject[self._ENABLE_ARTIFACTS_COLLECTION_FIELD], True)
        
        self.RunprocessOptions = Utils.getDic(pipelineObject, self._RUN_PROCESS_OPTIONS_DIC, {})
        self.OutputsPaths = None
        self.BranchesOutputsPaths = defaultdict(list)