#!/usr/bin/env python
import datetime

import sqlite3
from time import sleep

from app.reuters import Reuters


db = sqlite3.connect('database.sqlite')

db.execute("DROP TABLE IF EXISTS news;")
db.commit()
db.execute("CREATE TABLE news ( \
  id     INTEGER PRIMARY KEY AUTOINCREMENT, \
  item_id VARCHAR(50), \
  channel VARCHAR(50), \
  date_created VARCHAR(50), \
  headline VARCHAR(50), \
  language VARCHAR(50));")
db.commit()



rapi = Reuters()

date_format = "%Y-%m-%dT%H:%M:%SZ"

start_date = datetime.datetime.strptime("2017-09-10T00:00:00Z", date_format)
end_date = datetime.datetime.utcnow() + datetime.timedelta(hours=10)

for channel in rapi.get_channels():
    while start_date < end_date:
        res = rapi._call_xml('items',
                             {'channel': channel,
                              'dateRange': "%s-%s" % (start_date.strftime("%Y.%m.%d.%H.%M"),
                                                      (start_date + datetime.timedelta(hours=3)).strftime(
                                                          "%Y.%m.%d.%H.%M")),
                              'mediaType': 'T'})
        sleep(2)
        for c in res.findall('result'):
            item_id = c.findtext('id')
            channel = c.findtext('channel')
            date_created = c.findtext('dateCreated')
            headline = c.findtext('headline')
            language = c.findtext('language')

            db.execute("INSERT INTO news (item_id, channel, date_created, headline, language) VALUES (?, ?, ?, ?, ?);",
                       (item_id, channel, date_created, headline, language))
            db.commit()

        start_date = start_date + datetime.timedelta(hours=3)

    start_date = datetime.datetime.strptime("2017-09-10T00:00:00Z", date_format)
    end_date = datetime.datetime.utcnow() + datetime.timedelta(hours=10)


