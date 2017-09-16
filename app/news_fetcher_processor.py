import datetime
import json
import os
from urllib.error import HTTPError

import sqlite3

from socketIO_client import SocketIO

from app.reuters import Reuters, ReutersPermid


class NewsFetcherProcessor:
    def __init__(self):
        self.socket_io = None
        self.rapi = None
        self.channel_date = {}

    def process(self):
        self.socket_io = SocketIO('localhost', 8000)
        if self.socket_io is None:
            self.socket_io = SocketIO('localhost', 8000)

        self.rapi = Reuters()

        try:
            self.process_channels()
            self.test_news_for_frontend() # TODO
        except HTTPError:
            print("Error occurred when fetching latest news data")

    def test_news_for_frontend(self):
        data = {
            'item_id': 'tag:reuters.com,2017:newsml_ISS910541:849023734',
            'headline': 'this is a new headline',
            'dateCreated': '2017-01-01 12:12:12',
            'image': 'https://images.pexels.com/photos/365434/pexels-photo-365434.jpeg',
            'keywords': ['keyword', 'other keyword']
        }
        print('sending new data to client: ')
        self.socket_io.emit('new_news', data)

    def process_channels(self):
        for channel in self.rapi.get_channels():

            if channel not in self.channel_date:
                self.channel_date[channel] = datetime.datetime.utcnow() - datetime.timedelta(minutes=120)

            tree = self.rapi.recent_news(channel)
            for c in tree.findall('result'):
                item_id = c.findtext('id')
                date_created = c.findtext('dateCreated')
                headline = c.findtext('headline')

                story = self.rapi.get_story_highlight(item_id)
                image = story['image']
                keywords = ReutersPermid.get_tags(story['body'])

                news_date = datetime.datetime.strptime(date_created, "%Y-%m-%dT%H:%M:%SZ")

                if news_date > self.channel_date[channel]:
                    self.push_data({
                        'id': item_id,
                        'item_id': item_id, # which one ? legacy
                        'headline': headline,
                        'dateCreated': date_created,
                        'image': image,
                        'keywords': keywords
                    })
                    self.channel_date[channel] = news_date
                    if os.path.exists('app_db.sqlite'):
                        self.save_news_to_db(item_id, channel, news_date, headline, keywords)

    def save_news_to_db(self, item_id, channel, date_created, headline, keywords):
        db = sqlite3.connect('app_db.sqlite')
        db.execute(
            "INSERT OR REPLACE INTO news(item_id, channel, date_created, date_created_timestamp, headline, keywords) \
            VALUES (?, ?, ?, ?, ?, ?)",
            (item_id, channel, date_created, int(date_created.timestamp()), headline, json.dumps(keywords)))
        db.commit()

    def push_data(self, data):
        self.socket_io.emit('new_news', data)
