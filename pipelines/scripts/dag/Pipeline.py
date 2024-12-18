import sys, os
sys.path.append(os.path.abspath(str()))

from .Utils import Utils
from collections import defaultdict
import logging
logger = logging.getLogger()

class Pipeline:
    _PROCESS_NAME_FIELD = 'ProcessName'
    _GENERATE_REPORT = 'GenerateReport'
    _ENABLE_ARTIFACTS_COLLECTION_FIELD = 'EnableArtifactCollection'
    _RUN_PROCESS_OPTIONS_DIC = 'RunprocessOptions'
    
    def __init__(self, pipelineObject):
        self._pipelineObject = pipelineObject
        self.ProcessName = self._pipelineObject.get(self._PROCESS_NAME_FIELD)
        self.GenerateReport = Utils.getBoolean(pipelineObject, self._pipelineObject[self._GENERATE_REPORT], True)
        self.EnableArtifactCollection = Utils.getBoolean(pipelineObject, self._pipelineObject[self._ENABLE_ARTIFACTS_COLLECTION_FIELD], True)
        self.RunprocessOptions = Utils.getDic(pipelineObject, self._RUN_PROCESS_OPTIONS_DIC, {})
        self.OutputsPaths = None
        self.BranchesOutputsPaths = defaultdict(list)