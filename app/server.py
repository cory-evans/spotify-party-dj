import os
from flask import session, g
from app import create_app, models


app = create_app()

@app.after_request
def after_request(resp):
    resp.headers['Cache-Control'] = 'no-store'

    return resp

@app.before_request
def before_request():
    u = session.get('user', None)
    g.user = None
    if u:
        g.user = models.User(
            **u
        )
