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

def _make_headers_for_party_host():
    # get the party of the current user

    party_member = current_app.db.query(models.PartyMember)\
        .filter_by(user=current_user)\
        .first()

    user = party_member.party.host

    raw_headers = {
        'Authorization': f'Bearer {user.access_token}'
    }

    return raw_headers

def make_request(endpoint, method='GET', headers=None, params=None, data=None, as_party_host=False) -> requests.Response:
    base_url = 'https://api.spotify.com/v1'

    if as_party_host:
        raw_headers = _make_headers_for_party_host()
    else:
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

    return resp

def get_track(id: str):
    endpoint = f'/tracks/{id}'
    return make_request(endpoint).json()


def queue_song(uri: str):
    params = {
        'uri': uri
    }
    resp = make_request(
        '/me/player/queue',
        method='POST',
        params=params,
        as_party_host=True
    )

    return resp.status_code == 204
