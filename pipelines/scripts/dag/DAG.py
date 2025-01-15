import sys, os
sys.path.append(os.path.abspath(str()))

import logging
import json
from .Job import Job
from .Pipeline import Pipeline
from .Branch import Branch
from .Utils import Utils
from collections import deque
from collections import defaultdict

logger = logging.getLogger()

class DAG:   
    def __init__(self, dag_path):
        self._dag_path = dag_path
        self._pipeline = self._getDAGObject()
        
    def getJobUploadPaths(self, job):
        # If the job is initiating a new branch, it will upload all pipeline output folders. This case includes 'Start' job.
        # If the job is on the same branch as the previous job, it will upload the job output folders only
        if job["IsStartingNewBranch"]: # New branch will be created, so upload all artifacts
            return self._pipeline["OutputsPaths"]
        else:
            return set(job.Outputs)

    def getPredecessorJobsBranchesNames(self, job):
        brancheshNames = set()
        for predecessorJobName in job["PredecessorJobsNames"]:
            predecessorJob = self._pipeline["Jobs"][predecessorJobName]
            brancheshNames.add(predecessorJob["BranchName"])
        return brancheshNames
    
    ################################################
    #                Private helper methds
    ################################################
    def getPipeline(self):
        return self._pipeline
        
    def getJob(self, jobName):
        return self._pipeline["Jobs"][jobName]

    def _getDAGObject(self):
        if os.path.isfile(self._dag_path) == False:
            raise Exception(f"Can not find dag file: {self._dag_path}")
        else:
            with open(self._dag_path, 'r') as file:
                dagObject = json.load(file)
            if dagObject is None:
                raise Exception(f"DAG is empty")
            return dagObject