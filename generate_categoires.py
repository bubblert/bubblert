#!/usr/bin/env python
import datetime
import json
from collections import defaultdict

import sqlite3

db = sqlite3.connect('app_db.sqlite')

MINIMAL_NUMBER_OF_NEWS_TO_CREATE_GROUP = 3
MINIMAL_ENTITY_SIMILARITY = 3

TIME_WINDOW_BOX = 86400 * 3
TIME_WINDOW_STEP = 3600 * 2

now = int(db.execute("SELECT max(date_created_timestamp) FROM news").fetchone()[0]) + 86400

time_window_beginning = int(db.execute("SELECT min(date_created_timestamp) FROM news").fetchone()[0]) - 86400


def similarity_measure(keywords_set1, keywords_set2):
    if keywords_set1 is None or keywords_set2 is None:
        return 0
    else:
        return len(list(set(json.loads(keywords_set1)).intersection(json.loads(keywords_set2))))


def get_similar_entities(news, list_of_entities):
    res = []
    for e in list_of_entities:
        if similarity_measure(news[1], e[1]) > MINIMAL_ENTITY_SIMILARITY:
            res.append(e)
    return res


def create_group():
    utc_now = datetime.datetime.utcnow()

    db.execute("INSERT INTO groups (date_created, date_created_timestamp) VALUES \
                (?, ?)", (utc_now.strftime("%Y-%m-%dT%H:%M:%SZ"), int(utc_now.timestamp())))

    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def assign_news_to_group(item_id, group_id):
    db.execute("UPDATE news set group_id = ? WHERE item_id = ?", (group_id, item_id))
    db.commit()


def is_assign_to_group(item_id):
    return db.execute("SELECT group_id from news where item_id ='{}'".format(item_id)).fetchone()[0] is not None


def get_not_assigned_news(time_window_beginning):
    return db.execute("""SELECT item_id, keywords, group_id, date_created, date_created_timestamp, headline
                                                   FROM news
                                                   WHERE date_created_timestamp > ? AND date_created_timestamp < ? + ? AND group_id IS NULL
                                                   ORDER BY date_created_timestamp ASC""",
               (time_window_beginning, time_window_beginning, TIME_WINDOW_STEP)).fetchall()



def leaders(xs, top=10):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    return sorted(counts.items(), reverse=True, key=lambda tup: tup[1])[:top]


def update_groups_keywords(ids):

    for id in ids:
        all_keywords = []
        for keywords in db.execute("""SELECT keywords \
                           FROM news \
                           WHERE group_id = {}""".format(id)).fetchall():
            all_keywords = all_keywords + json.loads(keywords[0])

        lead = leaders(all_keywords)

        new_keywords = list(map(lambda x: x[0], lead))

        db.execute("UPDATE groups SET keywords = ? WHERE id = ?", (json.dumps(new_keywords), id))



while time_window_beginning < now:

    not_assigned_news_in_window = get_not_assigned_news(time_window_beginning)

    groups_to_refresh = set()

    # First. Try tp assign to existing groups
    groups = db.execute("""SELECT id, keywords, date_created, date_created_timestamp, headline \
                           FROM groups \
                           WHERE date_created_timestamp > {}""".format(time_window_beginning)).fetchall()

    for news in not_assigned_news_in_window:
        for g in groups:
            if similarity_measure(g[1], news[1]):
                assign_news_to_group(news[0], g[0])
                groups_to_refresh.add(g[0])

    not_assigned_news_in_window = get_not_assigned_news(time_window_beginning)

    # Second. Search for new groups
    for news in not_assigned_news_in_window:
        if is_assign_to_group(news[0]):
            continue

        similar = get_similar_entities(news, not_assigned_news_in_window)

        if len(similar) > MINIMAL_NUMBER_OF_NEWS_TO_CREATE_GROUP:
            grp_id = create_group()
            assign_news_to_group(news[0], grp_id)
            groups_to_refresh.add(grp_id)

            for sim in similar:
                assign_news_to_group(sim[0], grp_id)

    update_groups_keywords(groups_to_refresh)

    # time passing by
    time_window_beginning = time_window_beginning + TIME_WINDOW_STEP


db.close()
