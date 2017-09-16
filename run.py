#!/usr/bin/env python
import json
import logging
import werkzeug

from flask import Flask, render_template, Response
from flask.ext.apscheduler import APScheduler
from flask_socketio import emit, SocketIO

from app.news_fetcher_processor import NewsFetcherProcessor
from app.reuters import Reuters

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

news_processor = NewsFetcherProcessor()

app.config.update(JOBS=[
    {
        'id': 'news_fetching_job',
        'func': news_processor.process,
        'trigger': 'interval',
        'seconds': 2
    }
], SCHEDULER_JOBSTORES={}, SCHEDULER_API_ENABLED=True)


@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@socketio.on('connect')
def connect():
    print("connected")


@socketio.on('disconnect')
def disconnect():
    print('disconnected')


@socketio.on('new_news')
def new_news(message):
    emit('news', message['data'], broadcast=True)


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

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    socketio.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    runserver()
