import json


def get_config():
    with open("config/config.json", "r") as conf:
        data = json.load(conf)

    return data

