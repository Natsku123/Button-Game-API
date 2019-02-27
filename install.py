import random
import string
import json
import os
import pymysql
import urllib.request


def generate_secret():
    """
    Generate secret for Flask.
    :return:
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(64))


def main():
    print("Starting setup for Button-Game-API...")

    # Create directories and notify if permissions needed
    try:
        config_dir = "config/"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    except OSError:
        print("No permissions to create a directory for configurations!")
        return

    print("\nLoading files...")

    try:
        config_dir = "modules/"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    except OSError:
        print("No permissions to create a directory for files!")
        return

    # Download files from dl.meckl.in
    try:
        with urllib.request.urlopen("https://dl.meckl.in/button-game-api/modules/__init__.py") as response:
            with open("modules/__init__.py", "w") as module_init:
                module_init.write(response.read().decode('utf-8'))

        with urllib.request.urlopen("https://dl.meckl.in/button-game-api/modules/database.py") as response:
            with open("modules/database.py", "w") as module_database:
                module_database.write(response.read().decode('utf-8'))

        with urllib.request.urlopen("https://dl.meckl.in/button-game-api/modules/utils.py") as response:
            with open("modules/utils.py", "w") as module_utils:
                module_utils.write(response.read().decode('utf-8'))

        with urllib.request.urlopen("https://dl.meckl.in/button-game-api/app.py") as response:
            with open("app.py", "w") as app_file:
                app_file.write(response.read().decode('utf-8'))

        with urllib.request.urlopen("https://dl.meckl.in/button-game-api/wsgi.py") as response:
            with open("wsgi.py", "w") as wsgi_file:
                wsgi_file.write(response.read().decode('utf-8'))

    except OSError:
        print("No permissions to create needed files!")
        return

    # Database configuration
    print("\nConfigure database:")
    host = input("Database host (default: 127.0.0.1): ")
    if host == "":
        host = "127.0.0.1"
    username = input("Database username: ")
    password = input("Database password: ")
    name = input("Database name: ")

    secret = generate_secret()

    # Create config
    config = {
        "database": {
            "host": host,
            "username": username,
            "password": password,
            "name": name
        },
        "secret": secret
    }

    try:
        with open("config/config.json", "w") as conf_file:
            json.dump(config, conf_file)
    except OSError:
        print("No permission to write config files!")
        return

    print("\nConfig file created...")

    print("\nConfigure uWSGI:")

    directory = input("Working directory: ")

    if directory.endswith("/"):
        directory = directory[:len(directory)-1]

    uwsgi_conf = "[uwsgi]\n" \
                 "module = wsgi\n" \
                 "uid = www-data\n" \
                 "base = {0}\n" \
                 "chdir = %(base)\n" \
                 "master = true\n" \
                 "processes = 5\n" \
                 "socket = %(base)/config/uwsgi.sock\n" \
                 "chown-socket = %(uid):www-data\n" \
                 "chmod-socket = 666\n" \
                 "vacuum = true\n" \
                 "logger = file:%(base)/config/errlog".format(directory)

    try:
        with open("config/uwsgi.ini", "w") as uwsgi_file:
            uwsgi_file.write(uwsgi_conf)
    except OSError:
        print("No permission to write config files!")
        return

    print("\nuWSGI configured.")

    print("\nCreating tables...")

    with urllib.request.urlopen('https://dl.meckl.in/button-game-api/config/init_database.sql') as response:
        sql = response.read().decode('utf-8')

    sql = sql.split("#")

    for command in sql:
        db = pymysql.connect(host, username, password, name,
                             cursorclass=pymysql.cursors.DictCursor)
        try:
            with db.cursor() as cursor:
                cursor.execute(command)

            db.commit()
            db.close()
        except pymysql.MySQLError as e:
            db.rollback()
            db.close()
            print(e, e.args)
            return

    print("\nDatabase configured and tables created.\n")

    print("Now you need to configure your nginx to serve this application (", directory + "/config/uwsgi.sock", ")")


if __name__ == '__main__':
    main()
