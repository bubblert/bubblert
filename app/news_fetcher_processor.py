import datetime
from urllib.error import HTTPError

from socketIO_client import SocketIO

from app.routers_api import RoutersAPI
from app.reuters_api import ReutersApi


class NewsFetcherProcessor:
    def __init__(self):
        self.socket_io = None
        self.rapi = None
        self.channel_date = {}

    def process(self):
        self.socket_io = SocketIO('localhost', 8000)
        self.rapi = ReutersApi()

        try:
            self.process_channels()
        except HTTPError:
            print("Error occurred when fetching latest news data")

    def process_channels(self):
        for channel in self.rapi.get_channels():

            if channel not in self.channel_date:
                self.channel_date[channel] = datetime.datetime.utcnow() - datetime.timedelta(minutes=120)

            tree = self.rapi.recent_news(channel)
            for c in tree.findall('result'):
                item_id = c.findtext('id')
                date_created = c.findtext('dateCreated')

                story = self.rapi.get_story_highlight(item_id)

                news_date = datetime.datetime.strptime(date_created, "%Y-%m-%dT%H:%M:%SZ")

                if news_date > self.channel_date[channel]:
                    self.push_data({
                        'id': item_id,
                        'headline': c.findtext('headline'),
                        'dateCreated': date_created,
                        'image': story['image'],
                        'keywords': story['keywords']
                    })
                    self.channel_date[channel] = news_date

    def push_data(self, data):
        self.socket_io.emit('new_news', data)
