import subprocess
import os


def main():
    subprocess.run('start-mongodb.sh', shell=True, cwd=os.path.dirname(__file__))


if __name__ == "__main__":
    main()
