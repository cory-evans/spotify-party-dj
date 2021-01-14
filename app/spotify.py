import requests
from flask import current_app
from flask_login import current_user

from app import models

def _make_headers_for_user():
    user = current_user

    raw_headers = {
        'Authorization': f'Bearer {user.access_token}'
    }

    return raw_headers

def make_request(endpoint, method='GET', headers=None, params=None, data=None):
    base_url = 'https://api.spotify.com/v1'

    raw_headers = _make_headers_for_user()

    if isinstance(headers, dict):
        headers.update(raw_headers)
    else:
        headers = raw_headers


    req = requests.Request(
        method=method,
        url=base_url + endpoint,
        headers=headers,
        params=params,
        data=data
    )

    session = requests.Session()
    resp = session.send(
        req.prepare()
    )

    return resp.json()

def get_track(id: str):
    endpoint = f'/tracks/{id}'
    return make_request(endpoint)


def store_track(track_json: dict):
    track_obj = models.Track.from_dict(track_json)
    current_app.db.add(track_json)
