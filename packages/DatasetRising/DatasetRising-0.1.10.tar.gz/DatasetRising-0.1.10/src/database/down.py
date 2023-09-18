import subprocess
import os


def main():
    subprocess.run('docker stop e621-rising-mongo || echo "no instance to stop"', shell=True, cwd=os.path.dirname(__file__))


if __name__ == "__main__":
    main()

