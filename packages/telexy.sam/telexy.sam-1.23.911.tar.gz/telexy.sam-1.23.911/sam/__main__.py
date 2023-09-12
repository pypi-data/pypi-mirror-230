from mars import *
from subprocess import STDOUT, check_call
import os

print("installing dependencies")
print("installing git")
check_call(['sudo', 'apt', 'install', '-y', 'git'], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
print("git installed")
print("git sam")
check_call(['pip', 'install', 'git+https://github.com/facebookresearch/segment-anything.git'], stdout=open(os.devnull, 'wb'), stderr=STDOUT)
print("sam installed")

register(MarsApplicationRegistryPlugin("SamPlugin", "sam", "sam"))

print("Registration with Mars complete")