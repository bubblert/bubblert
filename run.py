#!/usr/bin/env python
from app import socketio, app


if __name__ == '__main__':
    socketio.run(app, port=5000)
