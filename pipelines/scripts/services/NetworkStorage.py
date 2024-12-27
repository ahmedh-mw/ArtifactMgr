import sys, os
sys.path.append(os.path.abspath(str()))

import logging
from utils import files

logger = logging.getLogger()
class NetworkStorage:
    _LAST_SUCCESSFUL_RUNID_FILENAME = '__lastSuccessfulRunId__'

    def __init__(self, root_folder):
        self.root_folder = root_folder

    def downloadFromLastSuccessfulRun(self, projectName, lookupBranches, artifactsFolders, downloadsPath):
        if artifactsFolders is None or len(artifactsFolders) == 0:
            return
        
        lastSuccessfulRunId = None
        visitedBranch = set()
        for lookupBranch in lookupBranches:
            logger.info(f"Looking up artifactory at branch: {lookupBranch}")
            if lookupBranch not in visitedBranch:
                visitedBranch.add(lookupBranch)
                relativeRepoBranchPath = os.path.join(projectName, lookupBranch)
                lastSuccessfulRunId = self.getLastSuccessfulRunId(relativeRepoBranchPath)
                if lastSuccessfulRunId is not None:
                    break
                else:
                    logger.info(f"Checking fallback branch")
        
        if lastSuccessfulRunId is None:
            return False
        else:
            self.download(relativeRepoBranchPath, lastSuccessfulRunId, artifactsFolders, downloadsPath)

    def download(self, relativeRepoBranchPath, runId, artifactsFolders, downloadsPath):
        if artifactsFolders is None or len(artifactsFolders) == 0:
            return
        
        repoBranchPath = os.path.join(self.root_folder, relativeRepoBranchPath)
        for artifactsFolder in artifactsFolders:
            srcFolderPath = os.path.join(repoBranchPath, runId, artifactsFolder)
            destFolderPath = os.path.join(downloadsPath, artifactsFolder)
            if os.path.isdir(srcFolderPath):
                logger.info(f'downloading [{artifactsFolder}:{runId}]: {srcFolderPath} ==> {destFolderPath}')
                files.delete_folder(destFolderPath)
                files.copy_folder(srcFolderPath, destFolderPath)
            else:
                logger.info(f'Source path does not exist: {srcFolderPath}')

    def upload(self, uploadsPath, relativeRepoBranchPath, runId, artifactsFolder):
        repoBranchPath = os.path.join(self.root_folder, relativeRepoBranchPath)
        jobDestPath = os.path.join(repoBranchPath, runId, artifactsFolder)
        if os.path.isdir(uploadsPath):
            logger.info(f'uploading [{artifactsFolder}:{runId}]: {uploadsPath} ==> {jobDestPath}')
            # files.delete_folder(jobDestPath)
            files.copy_folder(uploadsPath, jobDestPath)
        else:
            logger.info(f'Source path does not exist: {uploadsPath}')


    def getLastSuccessfulRunId(self, relativeRepoBranchPath):
        repoBranchPath = os.path.join(self.root_folder, relativeRepoBranchPath)
        if os.path.isdir(repoBranchPath) == False:
            logger.info(f"Can not find the source git branch folder: {repoBranchPath}")
            return None
        
        lastSuccessfulRunIdPath = os.path.join(repoBranchPath, self._LAST_SUCCESSFUL_RUNID_FILENAME)
        if os.path.isfile(lastSuccessfulRunIdPath) == False:
            logger.debug(f"Can not find last succssful run id file: {lastSuccessfulRunIdPath}")
            return None
        else:
            with open(lastSuccessfulRunIdPath, 'r') as file:
                lastSuccessfulRunId = file.readline().strip('\n')
            return lastSuccessfulRunId
        
    def updateLastSuccessfulRunId(self, relativeRepoBranchPath, runId):
        repoBranchPath = os.path.join(self.root_folder, relativeRepoBranchPath)
        if os.path.isdir(repoBranchPath) == False:
            raise Exception(f"Can not find the source repo branch folder: {repoBranchPath}")
        
        lastSuccessfulRunIdPath = os.path.join(repoBranchPath, self._LAST_SUCCESSFUL_RUNID_FILENAME)
        if os.path.isfile(lastSuccessfulRunIdPath) == False:
            logger.debug(f"Can not find last succssful run id file: {lastSuccessfulRunIdPath}")
        
        with open(lastSuccessfulRunIdPath, 'w') as file:
            file.write(runId)
        