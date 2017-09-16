#!/usr/bin/env python
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)


@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@sio.on('connect', namespace='/chat')
def connect(sid, environ):
    print("connect ", sid)


@sio.on('chat message', namespace='/chat')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)


@sio.on('disconnect', namespace='/chat')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
