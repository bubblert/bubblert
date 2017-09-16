#!/usr/bin/env python
from flask import Flask, render_template
from flask_socketio import send, emit, SocketIO
from os import listdir

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
    print("connect ")


@socketio.on('disconnect')
def disconnect():
    print('disconnect ')


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    emit('message', 'server says hello back!')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
