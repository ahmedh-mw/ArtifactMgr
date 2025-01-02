import sys, os
sys.path.append(os.path.abspath(str()))

import logging
import json
from .Job import Job
from .Pipeline import Pipeline
from .Branch import Branch
from .Utils import Utils
from .DMRMergeStep import DMRMergeStep
from collections import deque
from collections import defaultdict

logger = logging.getLogger()
_BRANCHES_TO_MERGE_FIELD = 'BranchesToMerge'
_LEVEL_FIELD = 'Level'
_BASE_BRANCH_FIELD = 'BaseBranch'
_DMR_EXTENSION = 'dmr'

class DAGMerger:  
    def __init__(self, branches):
        self._branches = dict(branches)

    def getMergingSequence(self, branchesNamesList):
        dmrsMergeSequence = []
        requiredBaseDMRsBranchesNames = set()
        mergingMap = dict()
        self._addBranchesToMergingMap(mergingMap, branchesNamesList)
        nextMerge = self._getNextBranchesToMerge(mergingMap)
        while(nextMerge is not None):
            mergedBranches = list(nextMerge[_BRANCHES_TO_MERGE_FIELD])
            tempCounter = 1
            requiredBaseDMRBranchName = nextMerge[_BASE_BRANCH_FIELD]
            requiredBaseDMRsBranchesNames.add(requiredBaseDMRBranchName)
            tempDMR = f"{requiredBaseDMRBranchName}_tmp_{str(tempCounter)}"
            nextBranchToMerge = mergedBranches[0]
            for anotherBranchToMerge in mergedBranches[1:]:
                dmrsMergeSequence.append( DMRMergeStep( 
                    base=f"{requiredBaseDMRBranchName}.{_DMR_EXTENSION}",
                    ours=f"{nextBranchToMerge}.{_DMR_EXTENSION}",
                    theirs=f"{anotherBranchToMerge}.{_DMR_EXTENSION}",
                    merged= f"{tempDMR}.{_DMR_EXTENSION}") )
                logger.info(f"BASE: {requiredBaseDMRBranchName}: {nextBranchToMerge} + {anotherBranchToMerge} ==> {tempDMR}")
                nextBranchToMerge = tempDMR
                tempCounter += 1
                tempDMR = f"{requiredBaseDMRBranchName}_tmp_{str(tempCounter)}"
            
            self._removeBranchesFromMergingMap(mergingMap, nextMerge[_BRANCHES_TO_MERGE_FIELD])
            virtualTempBranchName = self._createVirtualBranch(requiredBaseDMRBranchName, nextBranchToMerge)
            self._addBranchesToMergingMap(mergingMap, [virtualTempBranchName])
            nextMerge = self._getNextBranchesToMerge(mergingMap)
        return dmrsMergeSequence, requiredBaseDMRsBranchesNames

    #################################################################
    #                Private methds
    ################################################################
    def _addBranchesToMergingMap(self, mergingMap, branchesNamesList):
        for branchName in branchesNamesList:
            branch = self._branches[branchName]            
            for predecessorBranchName in branch.AllPredecessorBranchesNames:
                predecessorBranch = self._branches[predecessorBranchName]
                if mergingMap.get(predecessorBranchName) is None:
                    mergingMap[predecessorBranchName] = { \
                                _BASE_BRANCH_FIELD: predecessorBranchName, \
                                _LEVEL_FIELD: predecessorBranch.Level, \
                                _BRANCHES_TO_MERGE_FIELD : set([branchName]) }
                else:
                    mergingMap[predecessorBranchName][_BRANCHES_TO_MERGE_FIELD].add(branchName)
    
    def _removeBranchesFromMergingMap(self, mergingMap, branchesToRemove):
        for _, branchInfo in mergingMap.items():
            diff = branchInfo[_BRANCHES_TO_MERGE_FIELD].difference(branchesToRemove)
            branchInfo[_BRANCHES_TO_MERGE_FIELD] = diff
            
    def _getNextBranchesToMerge(self, mergingMap):
        mergingBranchInfo = None
        keysToRemove = []
        for branchName, branchInfo in mergingMap.items():
            # logger.debug(f"branchInfo: {branchInfo}")
            branchesToMergeCounter = len(branchInfo[_BRANCHES_TO_MERGE_FIELD])    
            if branchesToMergeCounter <= 1:
                keysToRemove.append( branchInfo[_BASE_BRANCH_FIELD] )
            elif mergingBranchInfo is None:
                mergingBranchInfo = branchInfo
            elif branchInfo[_LEVEL_FIELD] > mergingBranchInfo[_LEVEL_FIELD]:
                mergingBranchInfo = branchInfo
            elif branchInfo[_LEVEL_FIELD] == mergingBranchInfo[_LEVEL_FIELD] \
                and branchesToMergeCounter > len(mergingBranchInfo[_BRANCHES_TO_MERGE_FIELD]):
                mergingBranchInfo = branchInfo
                
        for keyToRemove in keysToRemove:
            del mergingMap[keyToRemove]
        # logger.debug(f"mergingBranchInfo: {mergingBranchInfo}")
        return mergingBranchInfo

    def _createVirtualBranch(self, baseBranchName, branchName):
        newBranch = Branch(branchName)
        baseBranch = self._branches[baseBranchName]
        newBranch.Level = baseBranch.Level + 1
        newBranch.AllPredecessorBranchesNames = set(baseBranch.AllPredecessorBranchesNames)
        newBranch.AllPredecessorBranchesNames.add(baseBranchName)
        self._branches[branchName] = newBranch
        return newBranch.Name