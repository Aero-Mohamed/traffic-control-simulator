import subprocess
import os
import sys

sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'));
import sumolib


subprocess.run("whoami");
