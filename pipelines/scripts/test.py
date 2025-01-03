import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')
from utils import core
from dag import DAG, DAGMerger
from dag import Utils as ut
from utils import files
import os
import json
import logging
import pathlib
from config import *

logger = logging.getLogger()
logger.setLevel(core.logging.DEBUG)
_ENVIRONMENT_JENKINS_VARIABLES_PATH = 'pipelines/templates/vars.local.json'
_DAG_RELATIVE_PATH_FIELD = 'DAG_RELATIVE_PATH'

# pip install numpy
# pip install networkx
# pip install matplotlib
# pip install pyvis
import networkx as nx
import numpy as np
# import matplotlib.pyplot as plt
from pyvis.network import Network
from pyvis.options import Layout

def drawDAG(dag):
    nodesList = []
    for jobName in dag.Jobs:
        for predessorJobName in dag.getJob(jobName).PredecessorJobsNames:
            nodesList.append( ( predessorJobName, jobName) )
        
    G = nx.DiGraph(nodesList)
    # for layer, nodes in enumerate(nx.topological_generations(G)):
    for layer, nodes in enumerate(nx.topological_generations(G)):
        # `multipartite_layout` expects the layer as a node attribute, so add the
        # numeric layer value as a node attribute
        for node in nodes:
            G.nodes[node]["layer"] = layer

    # pos = nx.multipartite_layout(G, subset_key="layer")
    # fig, ax = plt.subplots()
    # nx.draw_networkx(G, pos=pos, ax=ax, node_size=2000)
    # ax.set_title("DAG layout in topological order")
    # fig.tight_layout()
    # plt.show()

    net = Network(directed = True)
    layout = { "randomSeed": None,
            "hierarchical": {"enabled": True, "levelSeparation": 700, "nodeSpacing": 100, "direction": 'LR', "sortMethod": 'directed'}
        }
    nodes_options = {"borderWidth": 2, "shape" : "ellipse", "font" : {"size" : 30}}
    net.options.layout = layout
    net.options.edges.smooth.type = 'cubicBezier'
    net.options.nodes = nodes_options
    net.height = "1200"
    net.toggle_physics(False)
    
    # net.show_buttons() # Show part 3 in the plot (optional)
    net.from_nx(G, default_node_size=30) # Create directly from nx graph
    for node in net.nodes: node["shape"] = 'ellipse'
    net.show('test.html',  notebook=False)


if __name__ == "__main__":
    logger.log(core.HEADER_LOG, core.SECTION_START)
    logger.log(core.HEADER_LOG, f"{core.SECTION_NAME} TEST")
    logger.log(core.HEADER_LOG, core.SECTION_END)

    # variables_file_path = os.path.join(WORKSPACE_PATH, SOURCECODE_FOLDER, _ENVIRONMENT_JENKINS_VARIABLES_PATH)
    variables_file_path = "D:/repos/gh/ArtifactMgr/pipelines/templates/vars.local.json"
    with open(variables_file_path, 'r') as variables_file:
        variables = json.load(variables_file)

    os.environ[_DAG_RELATIVE_PATH_FIELD] = variables[_DAG_RELATIVE_PATH_FIELD]
    # dag = DAG("C:/Data/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.complex.json")
    # dag = DAG("D:/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.complex.json")
    # dag = DAG("D:/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.parallel.json")
    # dag = DAG("D:/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.jenkins.json")
    dag = DAG("D:/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.jenkins.1task.json")
    # dag = DAG("D:/repos/gh/ArtifactMgr/pipelines/derived/pipeline_dag.github.balanced.json")
    
    with open("data.json", "w") as outfile:
        json.dump(dag.dictEncode(), outfile, indent=4)

    # drawDAG(dag)

    dagMerger = DAGMerger(dag.Branches)
    # dmrsMergeSequence, requiredBaseDMRsBranchesNames = dagMerger.getMergingSequence([
    #             "br_Top_Model_Tasks",
    #             "br_AHRS_Voter_L2B",
    #             "br_Actuator_Control_L2B",
    #             "br_InnerLoop_Control_L2B",
    #             "br_Flight_Control_L1A"

    #         ])
    # sequenceList = ut.dictEncode(dmrsMergeSequence)
    #   files.add_file(f"{pathlib.Path().resolve()}/data.test.json", json.dumps(sequenceList, indent=4))
    logger.log(core.HEADER_LOG, core.SECTION_END)