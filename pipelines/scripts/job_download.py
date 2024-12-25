from utils import core
from dag import DAG, DAGMerger, Utils
from utils import files
import os
import argparse
import logging
import json
from config import *

logger = logging.getLogger()

_DMR_RELATIVE_PATH = 'derived/artifacts.dmr'
_DMR_EXTENSION = 'dmr'
_DMR_MERGE_SEQ_FILE_NAME = 'dmrsMergeSequence.json'

def parseArguments():
    parser = argparse.ArgumentParser(description='Download job artifacts.', prog='job_download.py')
    parser.add_argument('-j', '--jobname', required=True, help='job name')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parseArguments()
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} JOB DOWNLAOD")
    logger.log(core.HEADER_LOG, core.SECTION_END)
    logger.info(args)

    dag = DAG(getDagPath())
    # Download => Merge => Move to project
    ####### Download:
    # 'Start' job:  - download only the 'End' job branch folder from the last succssful run
    #               - No merging will be required in this case
    # All other jobs:
    #               - download all input branches, input branches are the branches of all
    #               - predecessor jobs (using 'flow_predecessor_jobs' field)
    #######  Merge
    # Merge :       - Merge downloaded branches into a single current job branch if there 
    #               - are more than one branch downloaded
    #######  Move to project
    # Move to project:
    #               - Move the single downloaded branch or the merged one to the project folder
    ############################################################
    #           Download to _downlaods_ folder
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Downloading artifacts to _downlaods_ folder")
    currentJob = dag.getJob(args.jobname)
    
    relativeRepoBranchPath = os.path.join(PROJECT_NAME, REPO_BRANCH_NAME)
    downloadsPath = os.path.join(WORKSPACE_PATH, DONWLOADS_FOLDER)

    predecessorJobsBranchesNames = None
    if currentJob.IsStartJob:
        predecessorJobsBranchesNames = [currentJob.DownloadBranchName]
        artifactsService.downloadFromLastSuccessfulRun(relativeRepoBranchPath, predecessorJobsBranchesNames, downloadsPath)
    else:
        predecessorJobsBranchesNames = list(dag.getPredecessorJobsBranchesNames(currentJob))
        artifactsService.download(relativeRepoBranchPath, CURRENT_RUN_ID, predecessorJobsBranchesNames, downloadsPath)
    
    dmrMergingPath = os.path.join(WORKSPACE_PATH, DMR_MERGING_FOLDER)
    # Download required base DMR files
    if len(predecessorJobsBranchesNames) > 1: # Merging is required
        dagMerger = DAGMerger(dag.Branches)
        dmrsMergeSequence, requiredBaseDMRsBranchesNames = dagMerger.getMergingSequence(predecessorJobsBranchesNames)
        dmrsMergeSequenceFilePath = os.path.join(dmrMergingPath, _DMR_MERGE_SEQ_FILE_NAME)
        dmrsMergeSequenceList = Utils.dictEncode(dmrsMergeSequence)
        files.add_file(dmrsMergeSequenceFilePath, json.dumps(dmrsMergeSequenceList, indent=4))
        baseDMRsToDownload = set()
        for requiredBaseDMRBranchName in requiredBaseDMRsBranchesNames:
            baseBranchDmrFile = os.path.join(requiredBaseDMRBranchName, _DMR_RELATIVE_PATH)
            baseDMRsToDownload.add(baseBranchDmrFile)
        artifactsService.download(relativeRepoBranchPath, CURRENT_RUN_ID, baseDMRsToDownload, downloadsPath)

    ############################################################
    #           Merging
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Merging artifacts")
    mergingFolder = os.path.join(downloadsPath, currentJob.BranchName)
    if len(predecessorJobsBranchesNames) > 1: # Merging is required
        ###################################
        #           Merging Artifacts
        ###################################
        uniqueFiles = dict()
        conflictFiles = dict()
        for branchName in predecessorJobsBranchesNames:
            logger.debug(f"== Branch Name: {branchName}")
            ###############################################################3
            logger.debug(f"Move branch dmr file") 
            srcBranchDmrFilePath = os.path.join(WORKSPACE_PATH, branchName, _DMR_RELATIVE_PATH)
            destBranchDmrFilePath = os.path.join(dmrMergingPath, f"{branchName}.{_DMR_EXTENSION}")
            files.move_file(srcBranchDmrFilePath, destBranchDmrFilePath)
            ###############################################################3
            branchOutputsPaths = dag.Branches[branchName].OutputsPaths
            for outputPath in branchOutputsPaths:
                branchPath = os.path.join(downloadsPath, branchName)
                fullOutputPath = os.path.join(branchPath, outputPath)
                filesList = files.list_folder_files(fullOutputPath)
                filesChecksums = files.get_checksum_list(filesList)
                for file in filesList:
                    relativeFilePath = os.path.relpath(file, branchPath)
                    if relativeFilePath == "derived/artifacts.dmr" or relativeFilePath == "derived\\artifacts.dmr" \
                        or relativeFilePath == "derived/resultservice.dmr" or relativeFilePath == "derived\\resultservice.dmr":
                        continue
                    currentFileCheckSum = filesChecksums[file]
                    currentFileEntry = {"branch": branchName, "checksum":currentFileCheckSum}
                    if relativeFilePath in conflictFiles:
                        conflictFiles[relativeFilePath].append(currentFileEntry)
                        logger.debug(f"conflictFiles == append ==> {branchName} - {relativeFilePath} - {currentFileCheckSum}")
                    elif relativeFilePath in uniqueFiles:
                        uniqueFile = uniqueFiles[relativeFilePath][0]
                        uniqueFiles[relativeFilePath].append(currentFileEntry)
                        if uniqueFile["checksum"] != currentFileCheckSum:
                            conflictFiles[relativeFilePath] = uniqueFiles[relativeFilePath]
                            del uniqueFiles[relativeFilePath]
                            logger.debug(f"conflictFiles == create ==> {branchName} - {relativeFilePath} - {currentFileCheckSum}")
                    else:
                        uniqueFiles[relativeFilePath] = [{"branch": branchName, "checksum":currentFileCheckSum}]
                        logger.info(f"Copying: {branchName}:{relativeFilePath} =====> {currentJob.BranchName}")
                        files.copy_file(file, os.path.join(mergingFolder, relativeFilePath))
    
        logger.info(f"uniqueFiles: {uniqueFiles}")
        logger.info(f"conflictFiles: {conflictFiles}")
        if len(conflictFiles) > 0:
            raise Exception(f"Conflicts found")
        ###############################################
        #           Move Required base branches DMRs
        ##############################################
        logger.debug(f"Move branch dmr file") 
        # Move required base branches to DMR merging folder
        for baseBrancheName in baseDMRsToDownload:
            srcBranchDmrFilePath = os.path.join(WORKSPACE_PATH, baseBrancheName, _DMR_RELATIVE_PATH)
            destBranchDmrFilePath = os.path.join(dmrMergingPath, f"{baseBrancheName}.{_DMR_EXTENSION}")
            files.move_file(srcBranchDmrFilePath, destBranchDmrFilePath)
    else:    # Merging is not required
        logger.info(f"Merging is not required")
        branchName = predecessorJobsBranchesNames[0]
        branchPath = os.path.join(downloadsPath, branchName)
        if mergingFolder != branchPath:
            files.move_folder(branchPath, mergingFolder)

    ############################################################
    #           Move artifacts to project folder
    ############################################################
    logger.log(core.HEADER_LOG, f"{core.GROUP_START} Moving artifacts to project folder")
    srcArtifactsFolder = mergingFolder
    destProjectFolder = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER)
    files.move_merge_folder_content(srcArtifactsFolder, destProjectFolder)

    logger.log(core.HEADER_LOG, core.SECTION_END)