import sys, os
sys.path.append(os.path.abspath(str()))

from .Utils import Utils
from collections import defaultdict
import logging
logger = logging.getLogger()

class Pipeline:
    _PROCESS_NAME_FIELD = 'ProcessName'
    _GENERATE_REPORT = 'GenerateReport'
    _COLLECT_ARTIFACTS = 'CollectArtifacts'
    _RUN_PROCESS_OPTIONS_DIC = 'RunprocessOptions'
    
    def __init__(self, pipelineObject):
        self._pipelineObject = pipelineObject
        self.ProcessName = self._pipelineObject.get(self._PROCESS_NAME_FIELD)
        self.GenerateReport = Utils.getBoolean(pipelineObject, self._pipelineObject[self._GENERATE_REPORT], True)
        self.CollectArtifacts = Utils.getBoolean(pipelineObject, self._pipelineObject[self._COLLECT_ARTIFACTS], True)
        self.RunprocessOptions = Utils.getDic(pipelineObject, self._RUN_PROCESS_OPTIONS_DIC, {})
        self.OutputsPaths = None
        self.BranchesOutputsPaths = defaultdict(list)