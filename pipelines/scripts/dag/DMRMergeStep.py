import sys, os
sys.path.append(os.path.abspath(str()))
from collections import defaultdict
from .Utils import Utils
import logging
logger = logging.getLogger()

class DMRMergeStep:
    def __init__(self, base, ours, theirs, merged):
        self.BASE = base
        self.OURS = ours
        self.THEIRS = theirs
        self.MERGED = merged