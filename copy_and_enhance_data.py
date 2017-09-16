#!/usr/bin/env python
import datetime
import json

import sqlite3
from time import sleep

from app.reuters import Reuters, ReutersPermid

app_db = sqlite3.connect('app_db.sqlite')
db = sqlite3.connect('database.sqlite')

rapi = Reuters()

for news in db.execute("SELECT item_id, channel, date_created, headline, language, id FROM news WHERE id < 922 ORDER BY id desc;").fetchall():
    item_id = news[0]
    item = rapi.get_story(item_id)

    print(news[5])
    keywords = ReutersPermid.get_tags(item['body_xhtml'].replace('<p/>', '').replace('<p>', '').replace('</p>', ''))

    while keywords == 'Invalid response':
        sleep(1)
        print("Retry")
        keywords = ReutersPermid.get_tags(
            item['body_xhtml'].replace('<p/>', '').replace('<p>', '').replace('</p>', ''))

    app_db.execute("INSERT OR REPLACE INTO news(item_id, channel, date_created, date_created_timestamp, headline, keywords) \
                  VALUES (?, ?, ?, ?, ?, ?)",
                   (item_id, news[1], news[2], int(datetime.datetime.strptime(news[2], "%Y-%m-%dT%H:%M:%SZ").timestamp()), news[3], json.dumps(keywords)))
    app_db.commit()

app_db.close()
db.close()


