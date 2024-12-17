import sys, os
sys.path.append(os.path.abspath(str()))
from collections import defaultdict
from .Utils import Utils
import logging
logger = logging.getLogger()

class Job:
    _OUTPUTS_LIST = 'Outputs'
    _PATH_FIELD = 'Path'
    _FLOW_PREDECESSOR_JOBS_LIST = 'Flow_Predecessor_Jobs'
    _FILES_LIST = 'Files'
    _COMMANDS_LIST = 'Commands'
    _TASKS_LIST = 'Tasks'
    _RUN_PROCESS_OPTIONS_DIC = 'RunprocessOptions'

    def __init__(self, jobName, jobObject):
        self._jobObject = jobObject
        self.Name = jobName
        self.Commands = Utils.getList(jobObject, self._COMMANDS_LIST)
        self.Tasks = Utils.getList(jobObject, self._TASKS_LIST)
        self.RunprocessOptions = Utils.getDic(jobObject, self._RUN_PROCESS_OPTIONS_DIC, {})
        self.PredecessorJobsNames = self._getPredecessorJobsNames()
        self.IsStartJob = False
        self.IsEndJob = False
        self.IsMergingJob = False
        self.IsStartingNewBranch = False
        self.BranchName = str()
        self.DownloadBranchName = str()
        self.Outputs = self._getOutputs()
        self.SuccessorJobsNames = []
        
    def _getOutputs(self):
        outputs = defaultdict(list)
        jobOutputs = self._jobObject.get(self._OUTPUTS_LIST)
        if jobOutputs is None:
            return outputs
        for directoryOutput in jobOutputs:
            outputPath = directoryOutput[self._PATH_FIELD]
            directoryFiles = directoryOutput.get(self._FILES_LIST)
            if directoryFiles:
                if directoryFiles and len(directoryFiles) > 0:
                    for file in directoryFiles:
                        outputs[outputPath].append(file)
            else:
                outputs[outputPath] = []

        return outputs
    
    def _getPredecessorJobsNames(self):
        predecessorJobsNames = self._jobObject.get(self._FLOW_PREDECESSOR_JOBS_LIST)
        if not predecessorJobsNames:
            predecessorJobsNames = []
        return predecessorJobsNames