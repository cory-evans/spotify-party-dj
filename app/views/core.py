import uuid
import os

from flask import (
    Blueprint,
    flash,
    render_template,
    session,
    g,
    request,
    redirect,
    url_for
)

import spotipy

from app import util

bp = Blueprint('core', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login')
def login():
    auth_manager = util.auth_manager()

    return redirect(auth_manager.get_authorize_url())

@bp.route('/login_after')
def login_after():
    auth_manager = util.auth_manager()
    code = request.args.get('code')
    auth_manager.get_access_token(code)

    return redirect(url_for('core.index'))

@bp.route('/logout')
def logout():
    try:
        os.remove(util.session_cache_path())
        session.clear()

    except OSError as e:
        print('Error %s - %s' % (e.filename, e.strerror))

    return redirect(url_for('core.index'))
