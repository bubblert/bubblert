import os
import sqlite3
from socketIO_client import SocketIO

APP_DB_SQLITE = 'app_db.sqlite'


class NewsAggregationProcessor:
    def __init__(self):
        self.socket_io = None

    def process(self):
        if self.socket_io is None:
            self.socket_io = SocketIO('localhost', 8000)

        if not os.path.exists(APP_DB_SQLITE):
            return

        res = self.db().execute("SELECT * FROM news")

        print("Test of agg proc")

    def push_data(self, data):
        self.socket_io.emit('new_news', data)

    def db(self):
        return sqlite3.connect(APP_DB_SQLITE)
