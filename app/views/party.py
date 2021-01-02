import json
import string
import random
import datetime

import spotipy
from flask import Blueprint, url_for, redirect, render_template, session
from flask_socketio import join_room

from app import models, util
from app.exts import db, socketio, scheduler


bp = Blueprint('party', __name__, url_prefix='/party')

@bp.route('/<code>')
def party(code: str):
    return render_template('party.html')

@bp.route('/host')
def host():
    # create party
    code = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
    party = models.Party(
        id=code,
        host=session['uuid']
    )

    scheduler.add_job(
        f'{code}-current',
        update_currently_playing,
        args=(code,),
        trigger='interval',
        seconds=5,
        next_run_time=datetime.datetime.now()
    )

    db.session.add(party)
    db.session.commit()

    session['code'] = code
    return redirect(url_for('party.party', code=code))

@bp.route('/join/<code>')
def join(code: str):

    session['code'] = code

    return redirect(url_for('party.party', code=code))

@socketio.on('connect')
def on_connect():
    join_room(session.get('code'))

@socketio.on('player current')
def currently_playing():
    p = models.Party.query.get(session.get('code'))
    if p and p.currently_playing:
        track = json.loads(p.currently_playing)

        socketio.emit('player current', track, room=session.get('code'))
    else:
        print('no track')

@socketio.on('vote skip')
def vote_to_skip(state):
    spotify = util.spotify()
    user = spotify.me()['display_name']
    print(user, 'is skipping:', state)
    if state:
        v = models.VoteToSkip(
            party_id=session.get('code'),
            user=user
        )

        db.session.add(v)
    else:
        db.session.query(models.VoteToSkip).filter_by(
            user=user
        ).delete()
    db.session.commit()

    socketio.emit('vote skip', user, room=session.get('code'))

def update_currently_playing(room):
    spotify = util.get_party_host_spotify(room)

    track = spotify.current_user_playing_track()

    socketio.emit('player current', track, room=room)

    party = models.Party.query.get(room)

    if party.currently_playing and json.loads(party.currently_playing)['item']['uri'] != track['item']['uri']:
        db.session.query(models.VoteToSkip).filter_by(
            party_id=room
        ).delete()

    party.currently_playing = json.dumps(track)

    db.session.commit()
