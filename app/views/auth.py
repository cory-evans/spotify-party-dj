import json
import uuid
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

from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user
)

from app import models

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login')
def login():
    scopes = 'user-read-playback-state user-modify-playback-state user-read-email user-read-private'

    params = {
        'client_id': current_app.config.get('SPOTIFY_CLIENT_ID'),
        'response_type': 'code',
        'redirect_uri': 'https://' + current_app.config.get('SERVER_NAME') + '/auth/login_after',
        'state': '17e627261463283b6c61873576e1ef5c',  # TODO make this random
        'scope': scopes
    }

    url_params = urlparse.urlencode(params)

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
        'redirect_uri': 'https://' + current_app.config.get('SERVER_NAME') + '/auth/login_after'
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

    # does the user exist?
    user = current_app.db.query(models.User)\
        .filter_by(id=data['id'])\
        .first()

    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=data['expires_in'])
    if not user:
        user = models.User(
            id = data['id']
        )

        add_user = True
    else:
        add_user = False

    user.display_name = data['display_name']
    user.email = data['email']
    user.href = data['href']
    user.uri = data['uri']

    user.access_token = data['access_token']
    user.refresh_token = data['refresh_token']
    user.expires = expires
    user.scope = data['scope']
    user.token_type = data['token_type']

    user.authenticated = True

    if add_user:
        current_app.db.add(user)

    # drop all images belonging to the user
    current_app.db.query(models.UserImage)\
        .filter_by(user_id=user.db_id)\
        .delete()

    for img in data['images']:
        new_img = models.UserImage(
            height=img.get('height'),
            width=img.get('width'),
            url=img['url'],
            user=user
        )
        current_app.db.add(new_img)

    current_app.db.commit()

    # user_model = user.to_dict()

    login_user(user, remember=True)

    return redirect(url_for('core.index'))

@bp.route('/logout')
@login_required
def logout():
    user = current_user
    # user = current_app.db.query(models.User)\
    #     .get(user_model.db_id)

    user.authenticated = False
    current_app.db.commit()

    logout_user()

    return redirect(url_for('core.index'))

@bp.route('/refresh_token')
@login_required
def refresh_token():
    user = current_user

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
    user.expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=data['expires_in'])

    current_app.db.commit()

    return jsonify({
        'access_token': user.access_token
    })
