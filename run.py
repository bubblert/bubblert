#!/usr/bin/env python
import json
import logging
import werkzeug

from flask import Flask, render_template, Response
from flask_socketio import emit, SocketIO
from os import listdir
from app.reuters import Reuters


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@app.route('/components/<name>')
def components(name):
    if '..' not in name and name in listdir("./templates/components"):
        return render_template(f'/components/{name}')
    return 'Not found', 404


@socketio.on('connect')
def connect():
    print("connected")


@socketio.on('disconnect')
def disconnect():
    print('disconnected')


@socketio.on('start_news_stream')
def handle_news_stream_start():
    for i in range(10):
        emit('news_add', json.dumps({
                'id': i,
                'keyword': i,
                'image': None,
                'headline': f'newsflash number {i}',
                'lastUpdated': 'now'
            }
        ))


@app.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    if not story_id:
        return http_500('No story ID given')
    reuters = Reuters()
    story = reuters.get_story(story_id)
    if not story:
        return http_500('Story ID not found')

    return json.dumps(story)


def http_500(msg):
    return Response(json.dumps({'error': msg}), 500)


@werkzeug.serving.run_with_reloader
def runserver():
    socketio.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    runserver()
