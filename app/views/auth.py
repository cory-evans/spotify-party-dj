import json
import datetime

import requests
from urllib import parse as urlparse

from flask import (
    Blueprint,
    redirect,
    url_for,
    session,
    current_app,
    request,
    jsonify
)

from app import models
from app.exts import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login')
def login():
    # auth_manager = util.auth_manager()
    scopes = 'streaming user-read-email user-read-private'

    print(scopes)

    params = {
        'client_id': current_app.config.get('SPOTIFY_CLIENT_ID'),
        'response_type': 'code',
        'redirect_uri': 'http://' + current_app.config.get('SERVER_NAME') + '/auth/login_after',
        'state': '17e627261463283b6c61873576e1ef5c',  # TODO make this random
        'scope': scopes
    }

    url_params = urlparse.urlencode(params)
    print(url_params)

    return redirect('%s?%s' % ('https://accounts.spotify.com/authorize', url_params))

@bp.route('/login_after')
def login_after():
    if request.args.get('error'):
        return redirect(url_for('core.index'))

    code = request.args.get('code')
    state = request.args.get('state')


    headers = {
        'Authorization': current_app.config.get('SPOTIFY_AUTHORIZATION_BASE64')
    }
    params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://' + current_app.config.get('SERVER_NAME') + '/auth/login_after'
    }
    resp = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=params
    )

    if 'text/html' in resp.headers.get('Content-Type'):
        return resp.content


    data = resp.json()
    access_token = data['access_token']

    me_resp = requests.get('https://api.spotify.com/v1/me', headers={
        'Authorization': f'Bearer {access_token}'
    })

    data.update(me_resp.json())

    expires = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
    user = models.User(
        id = data['id'],
        display_name = data['display_name'],
        email = data['email'],
        href = data['href'],
        uri = data['uri'],
        images = json.dumps(data['images']),
        access_token = data['access_token'],
        refresh_token = data['refresh_token'],
        expires = expires,
        scope = data['scope'],
        token_type = data['token_type']
    )

    session['id'] = user.id

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('core.index'))

@bp.route('/logout')
def logout():
    try:
        session.clear()

    except OSError as e:
        print('Error %s - %s' % (e.filename, e.strerror))

    return redirect(url_for('core.index'))

@bp.route('/access_token')
def access_token():
    uid = session.get('id')
    user = models.User.query.get(uid)
    if user:
        return jsonify({
            'access_token': user.access_token
        })

    return jsonify({
        'access_token': None
    })

@bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    uid = session.get('id')
    user = models.User.query.get(uid)

    headers = {
        'Authorization': current_app.config.get('SPOTIFY_AUTHORIZATION_BASE64')
    }
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': user.refresh_token
    }
    resp = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=params
    )

    data = resp.json()
    user.access_token = data['access_token']
    user.token_type = data['token_type']
    user.scope = data['scope']
    user.expires = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])

    db.session.commit()

    return jsonify({
        'access_token': user.access_token
    })
