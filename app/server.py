import uuid

import spotipy
from flask import session, g
from app import (
    create_app,
    models,
    util
)

from app.exts import db, scheduler

app = create_app()

@app.after_request
def after_request(resp):
    resp.headers['Cache-Control'] = 'no-store'

    return resp

@app.before_request
def before_request():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    spotify = util.spotify()
    if spotify:
        g.user = spotify.me()
    else:
        g.user = None

@app.before_first_request
def before_first_request():
    db.drop_all()
    db.create_all()
    db.session.commit()
    # util.refresh_client_access_token()

# @scheduler.task('interval', id='refresh_spotify_token', seconds=50*60)
# def interval_50_mins():
#     # util.refresh_client_access_token()
#     pass
