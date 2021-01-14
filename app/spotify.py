import requests
from flask import current_app

from app import models

def make_request(endpoint, method='GET', headers=None, params=None, data=None):
    base_url = 'https://api.spotify.com/v1'

    user = current_app.db.query(models.User).first()
    raw_headers = {
        'Authorization': f'Bearer {user.access_token}'
    }

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
