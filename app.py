from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from modules.utils import get_config
from modules.database import get_players, add_click, get_needed, get_player

app = Flask(__name__)

app.config['SECRET'] = get_config()['secret']

cors = CORS(app, supports_credentials=True)


@app.route('/api/')
def root():
    """
    Root of API, good place for future documentation.
    :return:
    """
    return 'Welcome to ButtonGameAPI!'


@app.route('/api/v1.0/players/', methods=['GET'])
def players():
    """
    Get one player or all if username is provided
    :return:
    """
    username = request.args.get("username")

    # Check if username is defined
    if username:
        return jsonify(get_player(username))
    return jsonify(get_players())


@app.route('/api/v1.0/click/', methods=['POST'])
def click():
    """
    Update click to server.
    :return:
    """
    if not request.json:
        abort(400)

    # If username wasn't provided, use 'NO NAME' instead
    if 'username' not in request.json:
        username = "NO NAME"
    else:
        username = request.json['username']
    return jsonify(add_click(username))


@app.route('/api/v1.0/needed-clicks/', methods=['GET'])
def to_go():
    """
    Get next goal and amount of clicks needed
    :return:
    """
    return jsonify(get_needed())


if __name__ == '__main__':
    app.run()
