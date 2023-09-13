import subprocess
import os

subprocess.run('stop-mongodb.sh', shell=True, cwd=os.path.dirname(__file__))
