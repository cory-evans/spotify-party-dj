import json
import random
import string
import datetime
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
    state = get_current_state(session['code'])
    socketio.emit('state_change', state)


@socketio.on('state_change')
def state_change(currently_playing):
    track = current_app.db.query(models.Track)\
        .filter_by(uri=currently_playing['uri'])\
        .first()

    if not track:
        # Download track from spotify
        track_data_from_spotify = spotify.get_track(currently_playing['id'])

        # Insert into db
        track = models.Track.from_dict(track_data_from_spotify)
        current_app.db.add(track)

    party = current_app.db.query(models.Party)\
        .filter_by(id=session['code'])\
        .first()

    # If track not in database download on add it


    if party.currently_playing and party.currently_playing.uri != track.uri:
        # The song has changed
        party.next_song_is_in_queue = False
        socketio.emit('state_change', track.to_dict(exclude_columns=['db_id']))

    elif not party.currently_playing:
        socketio.emit('state_change', track.to_dict(exclude_columns=['db_id']))

    if track.duration_ms - currently_playing['progress_ms'] <= 10000 and not party.next_song_is_in_queue:
        # queue next song
        print('add next song to queue')
        party.next_song_is_in_queue = True

    party.currently_playing = track
    current_app.db.commit()


# @socketio.on('queue add item')
# def queue_item(uri):
#     add_song_to_queue(uri)
#     socketio.emit('queue get', get_queue())


def get_current_state(party_id):
    party = current_app.db.query(models.Party)\
        .filter_by(id=party_id)\
        .first()

    if party is None:
        return {}

    if party.currently_playing is None:
        return {}

    return party.currently_playing.to_dict(exclude_columns=['db_id'])


# def get_queue(party_id):
#     q = models.Queue.query\
#         .filter(models.Queue.party_id == party_id)\
#         .order_by(models.Queue.date_added)\
#         .all()

#     data = [
#         t.data
#         for t in q
#     ]

#     return data

# def add_song_to_queue(party_id, song_uri):
#     queue_item = models.Queue(
#         party_id=party_id,
#         track_uri=song_uri
#     )

#     current_app.db.add(queue_item)
#     current_app.db.commit()

# def get_next_song_in_queue(party: models.Party) -> str:
#     queue_item = models.Queue.query\
#         .filter(models.Queue.party_id==party.id)\
#         .order_by(models.Queue.date_added)\
#         .filter(models.Queue.next_playable > datetime.datetime.utcnow())\
#         .first()

#     if queue_item is None:
#         return ''

#     # Pick a song based on
#     track_uri = queue_item.track_uri

#     models.Queue.query\
#         .filter(models.Queue.id==queue_item.id)\
#         .delete()

#     current_app.db.commit()

#     return track_uri
