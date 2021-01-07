import os
from flask import session, current_app

import spotipy

from app import models
from app.exts import db


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

def cache_path_for_user(uuid: str):
    return caches_folder + uuid


def auth_manager(cache_path=None):
    if not cache_path:
        cache_path = session_cache_path()

    return spotipy.oauth2.SpotifyOAuth(
        scope='streaming user-read-email user-read-private',
        cache_path=cache_path,
        show_dialog=True,
        client_id=current_app.config.get('SPOTIFY_CLIENT_ID'),
        client_secret=current_app.config.get('SPOTIFY_CLIENT_SECRET'),
        redirect_uri='http://' + current_app.config.get('SERVER_NAME') + '/login_after'
    )

def spotify(cache_path=None):
    am = auth_manager(cache_path)

    if not am.get_cached_token():
        return None

    return spotipy.Spotify(auth_manager=am)

def get_party_host_spotify(code=None):
    if not code:
        code = session.get('code')

    with db.app.app_context():
        party = models.Party.query.get(code)
        return spotify(cache_path_for_user(party.host))
