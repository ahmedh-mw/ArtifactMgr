import sys, os
sys.path.append(os.path.abspath(str()))
from collections import defaultdict
from .Utils import Utils
import logging
logger = logging.getLogger()

class Branch:

    def __init__(self, branchName):
        self.Name = branchName
        self.PredecessorBranchesNames = None
        self.AllPredecessorBranchesNames = None
        self.SuccessorBranchesNames = set()
        self.OutputsPaths = set()
        self.JobsNames = set()
        self.Level = -1