import sys, os
sys.path.append(os.path.abspath(str()))
from collections import defaultdict
from .Utils import Utils
import logging
logger = logging.getLogger()

class Branch:

    def __init__(self, branchName):
        self.Name = branchName
        self.PredecessorBranchesNames = []
        self.SuccessorBranchesNames = []
        self.OutputsPaths = []
        self.JobsNames = []