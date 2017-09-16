#!/usr/bin/env python
from flask import Flask, render_template
from flask_socketio import send, emit, SocketIO
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template, Response
from os import listdir
import json
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
from app.reuters import Reuters


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
    for i in range(100):
        emit('news', f'newsflash number {i}')


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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    socketio.run(app, host='0.0.0.0', port=8000)
