from celery import Celery
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='secret!',
))

# Initialize Celery
# celery = Celery(app.name, broker='redis://localhost:6379',
#                 backend='sqlite:///database.sqlite')

celery = Celery('fb_processor', broker='redis://localhost:6379',
                backend='redis://localhost:6379',
                include=['fb_processor.fb_sentiment_analyser'])

socketio = SocketIO(app)

from app import resources
from app import app_controller
