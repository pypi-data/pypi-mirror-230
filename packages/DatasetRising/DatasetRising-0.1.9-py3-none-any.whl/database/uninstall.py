import subprocess
import os


def main():
    subprocess.run('stop-mongodb.sh', shell=True, cwd=os.path.dirname(__file__))
    subprocess.run('docker rm e621-rising-mongo', shell=True, cwd=os.path.dirname(__file__))


if __name__ == "__main__":
    main()

