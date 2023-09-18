import subprocess
import os

def main():
    username = os.environ.get('DB_USERNAME', 'root')
    password = os.environ.get('DB_PASSWORD', 'root')
    port = int(os.environ.get('DB_PORT', '27017'))

    subprocess.run(
        f'docker start e621-rising-mongo || docker run --name e621-rising-mongo --restart always -e "MONGO_INITDB_ROOT_USERNAME={username}" -e "MONGO_INITDB_ROOT_PASSWORD={password}" -p "${port}:${port}" -d mongo:6',
        shell=True, cwd=os.path.dirname(__file__)
    )


if __name__ == "__main__":
    main()
