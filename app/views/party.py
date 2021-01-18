import json
import random
import string
import datetime
from typing import List
from flask import (
    Blueprint,
    render_template,
    g,
    session,
    redirect,
    url_for,
    current_app
)
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room

from app import models, spotify
from app.exts import socketio


bp = Blueprint('party', __name__, url_prefix='/party')

@bp.route('/<code>')
def party(code):
    user = current_user

    if user.is_authenticated:
        party_member = current_app.db.query(models.PartyMember)\
            .filter_by(user_id=user.db_id)\
            .first()

        is_host = party_member.party.host.db_id == user.db_id
    else:
        is_host = False

    session['code'] = code

    return render_template(
        'party.html',
        user=current_user,
        is_host=is_host
    )

@bp.route('/host')
@login_required
def host():
    code = ''.join([
        random.choice(string.ascii_uppercase)
        for _ in range(6)
    ])

    user_model = current_user
    user = current_app.db.query(models.User)\
        .get(user_model.db_id)

    party = models.Party(
        id=code,
        host=user
    )
    party_member = models.PartyMember(
        party=party,
        user=user
    )

    current_app.db.add_all([party, party_member])
    current_app.db.commit()

    return redirect(url_for('party.party', code=code))

@bp.route('/join/<code>')
def join(code: str):
    user = current_user

    if user.is_anonymous:
        pass
    else:
        user_row = current_app.db.query(models.User)\
            .get(user.db_id)

        party = current_app.db.query(models.Party)\
            .filter_by(id=code)\
            .first()

        pm = models.PartyMember(
            party=party,
            user=user_row
        )
        current_app.db.add(pm)
        current_app.db.commit()

    return redirect(url_for('party.party', code=code))

@socketio.on('connect')
def on_connect():
    join_room(session['code'])
    party = get_party_from_code(session['code'])
    state = get_current_state(party)
    socketio.emit('state_change', state)
    socketio.emit('queue update', get_queue(party))


@socketio.on('state_change')
def state_change(currently_playing):
    track = ensure_song_exists(currently_playing['uri'])
    party = get_party_from_code(session['code'])

    if party.currently_playing and party.currently_playing.uri != track.uri:
        party.next_song_is_in_queue = False
        current_app.db.commit()
        socketio.emit('state_change', track.to_dict(exclude_columns=['db_id', 'album_id']))
        socketio.emit('queue update', get_queue(party))

        party.currently_playing = track
        current_app.db.commit()
        return

    if not party.currently_playing:
        socketio.emit('state_change', track.to_dict(exclude_columns=['db_id', 'album_id']))
        party.currently_playing = track
        current_app.db.commit()
        return

    if not party.next_song_is_in_queue and track.duration_ms - currently_playing['progress_ms'] <= 10000:
        # queue next song
        track = get_next_song_in_queue(party)
        if track is not None:
            spotify.queue_song(track.uri)
        party.next_song_is_in_queue = True
        current_app.db.commit()



@socketio.on('queue add item')
def queue_item(uri):
    party = get_party_from_code(session['code'])
    add_song_to_queue(party, uri)
    socketio.emit('queue update', get_queue(party))


def get_current_state(party):
    if party is None:
        return {}

    if party.currently_playing is None:
        return {}

    return party.currently_playing.to_dict(exclude_columns=['db_id', 'album_id'])


def get_queue(party) -> List[models.Track]:
    items_in_queue = [
        qi.track.to_dict(exclude_columns=['db_id', 'album_id'])
        for qi in party.queue.order_by(models.QueueItem.next_playable.asc())
    ]

    return items_in_queue

def add_song_to_queue(party, song_uri):
    track = ensure_song_exists(song_uri)

    queue_item = models.QueueItem(
        party=party,
        track=track
    )

    current_app.db.add(queue_item)
    current_app.db.commit()

def get_next_song_in_queue(party: models.Party) -> models.Track:
    queue_item = current_app.db.query(models.QueueItem)\
        .filter_by(party=party)\
        .order_by(models.QueueItem.next_playable)\
        .filter(models.QueueItem.next_playable < datetime.datetime.utcnow())\
        .first()

    if queue_item is None:
        return None

    next_song = queue_item.track

    current_app.db.delete(queue_item)
    current_app.db.commit()

    return next_song

def get_party_from_code(code) -> models.Party:
    return current_app.db.query(models.Party)\
        .filter_by(id=code)\
        .first()

def ensure_song_exists(uri) -> models.Track:
    track = current_app.db.query(models.Track)\
        .filter_by(uri=uri)\
        .first()

    if track is not None:
        return track

    track_json = spotify.get_track(uri.split(':')[-1])
    track = models.Track.from_dict(track_json)
    current_app.db.add(track)
    current_app.db.commit()

    return track
