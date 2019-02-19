from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from modules.utils import get_config
from modules.database import get_players, add_click, get_needed

app = Flask(__name__)

app.config['SECRET'] = get_config()['secret']

cors = CORS(app, supports_credentials=True)


@app.route('/')
def hello_world():
    return 'Welcome to ButtonGameAPI!'


@app.route('/api/v1.0/players/', methods=['GET'])
def players():
    return jsonify(get_players())


@app.route('/api/v1.0/click/', methods=['POST'])
def click():
    if not request.json:
        abort(400)
    if 'username' not in request.json:
        username = "NO NAME"
    else:
        username = request.json['username']
    return jsonify(add_click(username))


@app.route('/api/v1.0/needed-clicks/', methods=['GET'])
def to_go():
    return jsonify(get_needed())


if __name__ == '__main__':
    app.run()
