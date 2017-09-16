from socketIO_client import SocketIO

from app.routers_api import RoutersAPI


class NewsFetcherProcessor:
    def __init__(self):
        self.socket_io = None
        self.rapi = None

    def process(self):
        self.socket_io = SocketIO('localhost', 8000)
        self.rapi = RoutersAPI()

        for channel in self.rapi.get_channels():
            tree = self.rapi.recent_news(channel)
            for c in tree.findall('result'):
                self.push_data({
                    'id': c.findtext('id'),
                    'headline': c.findtext('headline'),
                    'dateCreated': c.findtext('dateCreated')
                })

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
