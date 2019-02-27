import json


def get_config():
    """
    Get config from config/config.json
    :return:
    """
    with open("config/config.json", "r") as conf:
        data = json.load(conf)

    return data

