import sys              # Used for retrieving process arguments.
import os               # Used for retrieving environment variables and path information.
import platform         # Used for retrieving platform/system information.
import time             # Used for sleep command.
import subprocess       # Used for executing os process calls
import logging          # logging feature
import importlib.util   # Used for checking the installed libraries

########################################################################## 
SECTION_START = '#' * 100 + " >>"
SECTION_NAME = '#' + ' ' * 30
SECTION_END = '#' * 100 + " <<"
FUNCTION_START = '=' * 80 + " >>"
FUNCTION_END = '=' * 80 + " <<"
GROUP_START = '.' * 20 
##########################################################################
# NOTSET=0  # DEBUG=10  # INFO=20   # WARN=30   # ERROR=40  # CRITICAL=50
HEADER_LOG = 21 # after Info
logging.addLevelName(HEADER_LOG, 'HEADER')
# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if importlib.util.find_spec('colorlog') is not None:
    import colorlog         # management for logging terminal color
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)-8s] %(message)s%(reset)s",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'HEADER':   'purple',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
else:
    formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s")
    
# Create a console handler and set the formatter
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

variables = dict()

def resolve_parameters(argv=None):   
    # OS related variables
    variables["cwd"] = os.getcwd()
    variables["homeDirectory"] = os.path.expanduser("~")
    variables["scriptDirectory"] = os.path.dirname(__file__)
    variables["isWindows"] = os.name == 'nt'
    variables["TMPDIR"] = "%temp%" if variables["isWindows"] else os.environ.get('TMP')
    if not variables["TMPDIR"]: variables["TMPDIR"] = "/tmp"
    return variables

resolve_parameters(sys.argv)
#################################################################################
#                           subprocesses
#################################################################################
# return out, error, returncode
def get_command_response(command, subprocessStdout = subprocess.STDOUT):
    # subprocessStdout = subprocess.PIPE or subprocess.STDOUT
    if subprocessStdout == subprocess.STDOUT: 
        process = subprocess.Popen(command, stderr=subprocessStdout, shell=True, bufsize=0, close_fds=True)
        process.communicate()
        out = None; error = None
    else: # subprocessStdout == subprocess.PIPE
        process = subprocess.Popen(command, stdout=subprocessStdout, stderr=subprocessStdout, shell=True, bufsize=0, close_fds=True)
        out, error = process.communicate()
    return out.decode('UTF-8').strip() if out else "", error.decode('UTF-8').strip() if error else "", process.returncode
###############################################################################
    
def sleep(seconds):
    logger.debug(f"Sleep for {seconds} second(s)")
    time.sleep(int(seconds))