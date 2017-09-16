import datetime
from socketIO_client import SocketIO

from app.routers_api import RoutersAPI


class NewsFetcherProcessor:
    def __init__(self):
        self.socket_io = None
        self.rapi = None
        self.channel_date = {}

    def process(self):
        self.socket_io = SocketIO('localhost', 8000)
        self.rapi = RoutersAPI()

        for channel in self.rapi.get_channels():

            if channel not in self.channel_date:
                self.channel_date[channel] = datetime.datetime.utcnow() - datetime.timedelta(minutes=120)

            tree = self.rapi.recent_news(channel)
            for c in tree.findall('result'):
                item_id = c.findtext('id')
                date_created = c.findtext('dateCreated')
                # story = self.rapi.get_story(item_id)
                news_date = datetime.datetime.strptime(date_created, "%Y-%m-%dT%H:%M:%SZ")

                if news_date > self.channel_date[channel]:
                    self.push_data({
                        'id': item_id,
                        'headline': c.findtext('headline'),
                        'dateCreated': date_created
                    })
                    self.channel_date[channel] = news_date


        # ## websocket: /newsfeed/
        # ### request
        # -
        # ### response
        # - id
        # - keyword
        # - image
        # - headline
        # - lastUpdated

    def push_data(self, data):
        self.socket_io.emit('new_news', {
            'data': data
        })
