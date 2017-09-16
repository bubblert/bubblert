#!/usr/bin/env python
import json
import logging
import sqlite3
import datetime

import werkzeug
from flask import Flask, render_template, Response, request
from flask.ext.apscheduler import APScheduler
from flask_socketio import emit, SocketIO

from app.news_aggregation_processor import NewsAggregationProcessor
from app.news_fetcher_processor import NewsFetcherProcessor
from app.reuters import Reuters
from app.knowledge_graph import get_facts_for_keyword
from app.reuters import ReutersPermid


def init_db():
    db = sqlite3.connect('app_db.sqlite')
    res = db.execute('SELECT count(*) '
                     'FROM sqlite_master '
                     'WHERE type=\'table\' '
                     'AND name=\'change_table\'').fetchone()

    if res[0] == 0:
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.execute('CREATE TABLE \'change_table\' '
                   '(cht_id INTEGER PRIMARY KEY DESC)')
        db.commit()

    db.close()


init_db()

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
# app.config.from_object({
#     'debug': True
# })
socketio = SocketIO(app)

news_processor = NewsFetcherProcessor()
reuters = Reuters()

aggregation_processor = NewsAggregationProcessor()

app.config.update(JOBS=[
    {
        'id': 'news_fetching_job',
        'func': news_processor.process,
        'trigger': 'interval',
        'seconds': 10
    },
    {
        'id': 'news_aggregation_job',
        'func': aggregation_processor.process,
        'trigger': 'interval',
        'seconds': 2
    }
], SCHEDULER_JOBSTORES={}, SCHEDULER_API_ENABLED=True)


def respond_with_json(obj):
    return Response(json.dumps(obj, indent=4, separators=(',', ': '))
                    , content_type='application/json; charset=utf-8')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/zoom/<story_id>')
def zoom(story_id):
    story = reuters.get_story(story_id)
    return render_template('zoom.html', story=story)


@app.route('/detail/<story_id>')
def detail(story_id):
    story = reuters.get_story(story_id)
    return render_template('detail.html', story=story)


@socketio.on('connect')
def connect():
    print("connected")


@socketio.on('disconnect')
def disconnect():
    print('disconnected')


@socketio.on('new_news')
def new_news(message):
    emit('news', message, broadcast=True)

@socketio.on('start_news_stream')
def handle_news_stream_start():
    emit('news_add', stories_until(0, False))

@app.route('/stories_until/<end_timestamp>', methods=['GET'])
def stories_until(end_timestamp, use_response=True):
    if end_timestamp is None or int(end_timestamp) == 0:
        end_timestamp = int(datetime.datetime.utcnow().timestamp())
    else:
        end_timestamp = int(end_timestamp)

    db = sqlite3.connect('app_db.sqlite')
    res = db.execute("""SELECT
                          type,
                          item_id,
                          date_created_timestamp,
                          headline,
                          keywords
                        FROM (
                          SELECT
                            'news' as type,
                            item_id,
                            date_created,
                            date_created_timestamp,
                            headline,
                            keywords
                          FROM news
                          WHERE group_id IS NULL AND date_created_timestamp > ? - 43200 AND ? > date_created_timestamp

                          UNION ALL

                          SELECT
                            'group' as type,
                            id AS item_id,
                            date_created,
                            date_created_timestamp,
                            headline,
                            keywords
                          FROM groups as g
                          WHERE date_created_timestamp > ? - 43200 AND ? > date_created_timestamp
                        )
                        ORDER BY date_created_timestamp
                          DESC;""", (end_timestamp, end_timestamp, end_timestamp, end_timestamp))

    resp = []
    for r in res.fetchall():
        resp.append({
            'type': r[0],
            'item_id': r[1],  # group id
            'date_created': r[2],
            'headline': r[3],
            'keywords': r[4]
        })

    return respond_with_json(resp) if use_response else resp


@app.route('/group/<group_id>', methods=['GET'])
def group_by_id(group_id):
    if not group_id:
        return http_500('No group ID given')
    else:
        db = sqlite3.connect('app_db.sqlite')
        res = db.execute("""
                SELECT item_id, date_created, headline, keywords
                FROM news
                WHERE group_id = {}
            """.format(group_id))

        resp = []
        for r in res.fetchall():
            resp.append({
                'type': 'news',
                'item_id': r[0],
                'date_created': r[1],
                'headline': r[2],
                'keywords': r[3]
            })

        return respond_with_json(resp) 


@app.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    if not story_id:
        return http_500('No story ID given')
    story = reuters.get_story(story_id)
    if not story:
        return http_500('Story ID not found')

    return respond_with_json(story)


@app.route('/stories/<story_id>/facts', methods=['GET'])
def get_facts(story_id):
    story = reuters.get_story(story_id)
    if not story:
        return http_500('Story ID not found')

    article = story.get('body_xhtml')
    article = article if article else ''
    tags = ReutersPermid.get_tags(article)
    result = []

    LIMIT = 2
    i = 0
    for tag in tags:
        facts = get_facts_for_keyword(tag)
        if facts: 
            result = result + facts
            i = i + 1
            if i > LIMIT: break

    print(result)
    return respond_with_json(result)


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
