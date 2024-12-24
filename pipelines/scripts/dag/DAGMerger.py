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
_BRANCHES_TO_MERGE_FIELD = 'BranchesToMerge'
_LEVEL_FIELD = 'Level'
_BASE_BRANCH_FIELD = 'BaseBranch'

class DAGMerger:  
    def __init__(self, branches):
        self._branches = dict(branches)

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
    
    def _removeMergedBranches(self, mergingMap, branchesToRemove):
        for _, branchInfo in mergingMap.items():
            diff = branchInfo[_BRANCHES_TO_MERGE_FIELD].difference(branchesToRemove)
            branchInfo[_BRANCHES_TO_MERGE_FIELD] = diff
            
    def _getNextBranchesToMerge(self, mergingMap):
        mergingBranchInfo = None
        keysToRemove = []
        for _, branchInfo in mergingMap.items():
            branchesToMergeCounter = len(branchInfo[_BRANCHES_TO_MERGE_FIELD])
            if branchesToMergeCounter == 1:
                keysToRemove.append( branchInfo[_BASE_BRANCH_FIELD] )
            elif mergingBranchInfo is not None \
                and branchInfo[_LEVEL_FIELD] == mergingBranchInfo[_LEVEL_FIELD] \
                and branchesToMergeCounter > len(mergingBranchInfo[_BRANCHES_TO_MERGE_FIELD]):
                mergingBranchInfo = mergingBranchInfo
            elif mergingBranchInfo is None \
                or branchInfo[_LEVEL_FIELD] > mergingBranchInfo[_LEVEL_FIELD]:
                mergingBranchInfo = branchInfo
                
        for keyToRemove in keysToRemove:
            del mergingMap[keyToRemove]
        return mergingBranchInfo

    def _createMergeReplacementBranch(self, baseBranch, branchName):
        newBranch = Branch(branchName)
        newBranch.Level = self._branches[baseBranch].Level + 1
        newBranch.AllPredecessorBranchesNames = set(self._branches[baseBranch].AllPredecessorBranchesNames)
        newBranch.AllPredecessorBranchesNames.add(baseBranch)
        self._branches[branchName] = newBranch
        return newBranch.Name
        

    def getMergingSequence(self, branchesNamesList):
        mergingMap = dict()
        self._addBranchesToMergingMap(mergingMap, branchesNamesList)
        nextMerge = self._getNextBranchesToMerge(mergingMap)
        while(nextMerge is not None):
            mergedBranches = list(nextMerge[_BRANCHES_TO_MERGE_FIELD])
            tempCounter = 1
            tempDMR = f"{nextMerge[_BASE_BRANCH_FIELD]}_{str(tempCounter)}"
            nextBranchToMerge = mergedBranches[0]
            for anotherBranchToMerge in mergedBranches[1:]:
                print(f"{nextMerge[_BASE_BRANCH_FIELD]} <= {nextBranchToMerge} + {anotherBranchToMerge} == {tempDMR}")
                nextBranchToMerge = tempDMR
                tempCounter += 1
                tempDMR = f"{nextMerge[_BASE_BRANCH_FIELD]}_{str(tempCounter)}"
            
            self._removeMergedBranches(mergingMap, nextMerge[_BRANCHES_TO_MERGE_FIELD])
            replacementBranchName = self._createMergeReplacementBranch(nextMerge[_BASE_BRANCH_FIELD], nextBranchToMerge)
            self._addBranchesToMergingMap(mergingMap, [replacementBranchName])
            nextMerge = self._getNextBranchesToMerge(mergingMap)