import sqlite3
import logging
from flask import Flask, g
from r53dyndns import settings

app = Flask(__name__)
app.debug = settings.debug
log = logging.getLogger('default')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(settings.database)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
