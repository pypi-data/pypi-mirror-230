import os
import subprocess
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
exec = sys.executable
subprocess.run([exec, "v2rayp.py"])
