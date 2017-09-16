import sqlite3
from configparser import ConfigParser

from flask import g
from app import app


@app.before_first_request
def init_db_if_needed():
    db = get_db()
    res = db.execute('SELECT count(*) '
                     'FROM sqlite_master '
                     'WHERE type=\'table\' '
                     'AND name=\'change_table\'').fetchone()

    if res[0] == 0:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.execute('CREATE TABLE \'change_table\' '
                   '(cht_id INTEGER PRIMARY KEY DESC)')
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.sqlite')
    return db


def get_fb():
    cfg_dict = ConfigParser()
    cfg_dict.read('config.ini')
    cfg_dict = cfg_dict['default']
    return None


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
