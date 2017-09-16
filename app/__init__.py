from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='secret!',
))

socketio = SocketIO(app)

from app import resources
from app import app_controller
