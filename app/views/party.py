import json
from flask import Blueprint, render_template, g, session

from app import models, util
from app.exts import db, socketio, cache


bp = Blueprint('party', __name__, url_prefix='/party')

@bp.route('/')
def party():
    return render_template('party.html')


@socketio.on('connect')
def on_connect():
    state = get_current_state()
    socketio.emit('state_change', state)

@socketio.on('state_change')
def state_change(state):
    cache.set('currently_playing', state)
    socketio.emit('state_change', state)


def get_current_state():
    state = cache.get('currently_playing')
    if state is None:
        return {}
    return state
