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
    _JOBS_DIC = 'Jobs'
    _PIPELINE_DIC = 'Pipeline'
    
    def __init__(self, dag_path):
        self._dag_path = dag_path
        self._dagObject = self._getDAGObject()
        self.Jobs = self._getJobs()
        self.Pipeline = self._getPipeline()
        self._updateSuccessorJobs()
        startJob = self._updateStartJob()
        self.StartJobName = startJob.Name
        endJob = self._updateEndJob()
        self.EndJobName = endJob.Name
        self._pipelineOutputsPaths = set()
        self.Branches = dict()
        self._traverseJobs(startJob, [])    # IsStartingNewBranch, BranchName, Pipeline.OutputsPaths
        self.Pipeline.OutputsPaths = self.removeDescendantFolders(list(self._pipelineOutputsPaths))
        # Branch names for all jobs need to be calculated before building OutputPaths
        self._traverseJobs_BuildBranchesOutputsPaths(startJob, [])
        self._calculateBranchesLevels()
        startJob.DownloadBranchName = endJob.BranchName
        # Debugging: for _,job in dag.Jobs.items(): vars(job)

    def getJobUploadPaths(self, job):
        # If the job is initiating a new branch, it will upload all pipeline output folders. This case includes 'Start' job.
        # If the job is on the same branch as the previous job, it will upload the job output folders only
        if job.IsStartingNewBranch: # New branch will be created, so upload all artifacts
            return self.Pipeline.OutputsPaths
        else:
            return set(job.Outputs.keys())
   
    def getPredecessorJobsBranchesNames(self, job):
        brancheshNames = set()
        for predecessorJobName in job.PredecessorJobsNames:
            predecessorJob = self.Jobs[predecessorJobName]
            brancheshNames.add(predecessorJob.BranchName)
        return brancheshNames

    def dictEncode(self):
        result = Utils.dictEncode(self)
        result["Pipeline"] = Utils.dictEncode(result["Pipeline"])
        result["Jobs"] = {jobName: Utils.dictEncode(job) for jobName, job in result["Jobs"].items()}
        result["Branches"] = {branchName: Utils.dictEncode(branch) for branchName, branch in result["Branches"].items()}
        # result["Branches"] = {branchName: branchName for branchName, branch in result["Branches"].items()}
        return result
    #################################################################
    #                Private traverse methds
    ################################################################
    def _traverseJobs(self, currentJob, visitedJobs):
        ###############################################
        #       Update IsStartingNewBranch
        ##############################################
        # IsStartingNewBranch = true: First Job on the branch
        #   The branch name is the same as the job name
        #   1) Start job: has no predecessor jobs
        #   2) Merging job: first job after merging and it has more than one predecessor jobs
        #   3) First job after splitting: the predecessor job has more than one successor jobs
        # IsStartingNewBranch = false: otherwise
        #   The branch name is the same as the predecessor job branch name
        #   If the job has only one predecessor job and the predecessor job has only one successor job
        predecessorJobsCount = len(currentJob.PredecessorJobsNames)
        if predecessorJobsCount == 0:  # 1) Start job
            currentJob.IsStartingNewBranch = True
        elif predecessorJobsCount > 1:  # 2) Merging job: first job after merging
            currentJob.IsMergingJob = True
            currentJob.IsStartingNewBranch = True
        else:    # PredecessorJobsCount = 1
            predecessorJob = self.getJob(currentJob.PredecessorJobsNames[0])
            predecessorJobSuccessorJobsCount = len(predecessorJob.SuccessorJobsNames)
            if predecessorJobSuccessorJobsCount > 1: # 3) First job after splitting
                currentJob.IsStartingNewBranch = True

        ##############################################
        #       Update BranchName
        ##############################################
        if currentJob.IsStartingNewBranch:
            currentJob.BranchName = currentJob.Name
            jobBranch = Branch(currentJob.BranchName)
            self.Branches[currentJob.BranchName] = jobBranch    
        else:
            currentJob.BranchName = predecessorJob.BranchName
            jobBranch = self.Branches[currentJob.BranchName]
       
        jobBranch.JobsNames.add(currentJob.Name)
        ##############################################
        #       Update Pipeline.OutputsPaths
        ##############################################
        self._pipelineOutputsPaths.update(currentJob.Outputs.keys())
        ##############################################
        #       Traverse forward
        ##############################################
        visitedJobs.append(currentJob.Name)
        for successorJobName in currentJob.SuccessorJobsNames:
            if successorJobName not in visitedJobs:
                successorJob = self.getJob(successorJobName)
                self._traverseJobs(successorJob, visitedJobs)

    def _traverseJobs_BuildBranchesOutputsPaths(self, currentJob, visitedJobs):
        ##############################################
        #       Build BranchesOutputsPaths
        ##############################################
        jobBranch = self.Branches[currentJob.BranchName]
        for predecessorJobName in currentJob.PredecessorJobsNames:      # Add all incoming branches
            if predecessorJobName not in visitedJobs:
                predecessorJob = self.getJob(predecessorJobName)
                self._traverseJobs_BuildBranchesOutputsPaths(predecessorJob, visitedJobs)
            predecessorJob = self.getJob(predecessorJobName)
            predecessorBranchOutputs = self.Branches[predecessorJob.BranchName].OutputsPaths
            jobBranch.OutputsPaths.update(predecessorBranchOutputs)

        jobBranch.OutputsPaths.update(currentJob.Outputs.keys())
        ##############################################
        #       Build PredecessorBranchesNames & SuccessorBranchesNames
        ##############################################
        if currentJob.IsStartingNewBranch:
            jobBranch.PredecessorBranchesNames = self.getPredecessorJobsBranchesNames(currentJob)
            jobBranch.AllPredecessorBranchesNames = set(jobBranch.PredecessorBranchesNames)
            for predecessorBranchName in jobBranch.PredecessorBranchesNames:
                predecessorBranch = self.Branches[predecessorBranchName]
                predecessorBranch.SuccessorBranchesNames.add(currentJob.BranchName)
            
        ##############################################
        #       Traverse forward
        ##############################################
        visitedJobs.append(currentJob.Name)
        for successorJobName in currentJob.SuccessorJobsNames:
            if successorJobName not in visitedJobs:
                successorJob = self.getJob(successorJobName)
                self._traverseJobs_BuildBranchesOutputsPaths(successorJob, visitedJobs)

    def _calculateBranchesLevels(self):
        startJob = self.getJob(self.StartJobName)
        levelBranch = self.Branches[startJob.BranchName]
        levelBranch.Level = 0
        nextLevelQueue = deque([levelBranch])

        while len(nextLevelQueue) > 0:
            levelBranch = nextLevelQueue.popleft()
            for successorBranchName in levelBranch.SuccessorBranchesNames:
                successorBranch = self.Branches[successorBranchName]
                successorBranch.AllPredecessorBranchesNames.update(levelBranch.AllPredecessorBranchesNames)
                if successorBranch.Level == -1:
                    successorBranch.Level = levelBranch.Level + 1
                    nextLevelQueue.append(successorBranch)

    def _updateSuccessorJobs(self):
        for jobName,job in self.Jobs.items():
            for predecessorJobName in job.PredecessorJobsNames:
                self.Jobs[predecessorJobName].SuccessorJobsNames.append(jobName)
    
    def _updateStartJob(self):
        startJobs = [job for _,job in self.Jobs.items() if len(job.PredecessorJobsNames) == 0]
        startJobsCount = len(startJobs)
        if startJobsCount == 0:
            raise Exception(f"Can not find Start job")
        elif startJobsCount > 1:
            raise Exception(f"DAG can not contain more than one Start job")
        startJob = startJobs[0]
        startJob.IsStartJob = True
        return startJob

    def _updateEndJob(self):
        endJobs = [job for _,job in self.Jobs.items() if len(job.SuccessorJobsNames) == 0]
        endJobsCount = len(endJobs)

        if endJobsCount == 0:
            raise Exception(f"Can not find End job")
        elif endJobsCount > 1:
            raise Exception(f"DAG can not contain more than one End job")
        endJob = endJobs[0]
        endJob.IsEndJob = True
        return endJob

    ################################################
    #                Private helper methds
    ################################################
    def removeDescendantFolders(self, folder_list):
        folder_list = sorted(folder_list)
        result = set()
        for folder in folder_list:
            if not any(folder.startswith(ancestor + "/") for ancestor in result):
                result.add(folder)
        return result

    def getJob(self, jobName):
        return self.Jobs[jobName]
    
    def _getJobs(self):
        jobsObjects = self._dagObject[self._JOBS_DIC].items()
        jobs = {jobName: Job(jobName, jobObject) for jobName, jobObject in jobsObjects}
        return jobs

    def _getPipeline(self):
        pipelineObject = self._dagObject[self._PIPELINE_DIC]
        pipeline = Pipeline(pipelineObject)
        return pipeline
    
    def _getDAGObject(self):
        if os.path.isfile(self._dag_path) == False:
            raise Exception(f"Can not find dag file: {self._dag_path}")
        else:
            with open(self._dag_path, 'r') as file:
                dagObject = json.load(file)
            if dagObject is None:
                raise Exception(f"DAG is empty")
            return dagObject