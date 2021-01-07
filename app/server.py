from flask import session, g, request
from app import (
    create_app,
    models
)

from app.exts import db

app = create_app()

@app.after_request
def after_request(resp):
    resp.headers['Cache-Control'] = 'no-store'

    return resp

@app.before_request
def before_request():
    # TODO optimize this
    g.user = None
    if session.get('id'):
        u = models.User.query.get(session.get('id'))
        if u:
            g.user = u.to_dict()


@app.before_first_request
def before_first_request():
    db.drop_all()
    db.create_all()
    db.session.commit()
