import sys
import platform
import subprocess
from typing import List

pids: List[str] = []
pops: List[subprocess.Popen] = []

# commands regarding each platform
terminate_commands = {
    "Linux": "kill ",
    "Windows": "taskkill /F /PID ",
    "Mac": "kill -9 "
}

# read pid from file
try:
  with open("pid", "r") as f:
    pids = [line.strip() for line in f.readlines()]
except:
  print("X Error reading 'pid' file.")
  sys.exit(1)

# run relevant terminated command
for pid in pids:
  print(u'\u2713', terminate_commands[platform.system()] + pid)
  pops.append(subprocess.Popen(terminate_commands[platform.system()] + pid, shell=True))

for pop in pops:
  pop.wait()

sys.exit(0)