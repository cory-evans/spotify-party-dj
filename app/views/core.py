from flask import (
    Blueprint,
    render_template,
    current_app,
    jsonify
)

from flask_login import current_user
from app import models, spotify

bp = Blueprint('core', __name__)

@bp.route('/')
def index():
    parties = current_app.db.query(models.Party).all()
    parties_models = [
        p.to_dict()
        for p in parties
    ]

    print(current_user)

    return render_template('index.html', user=current_user, parties=parties_models)

@bp.route('/track/<id>')
def download_track(id):
    track_json = spotify.get_track(id)

    track = models.Track.from_dict(track_json)
    exists = current_app.db.query(models.Track)\
        .filter_by(uri=track.uri)\
        .scalar()
    print(exists)
    if not exists:
        current_app.db.add(track)
        current_app.db.commit()

    return jsonify(track.to_dict())

@bp.route('/tracks')
def get_all_tracks():
    tracks = current_app.db.query(models.Track).all()

    return jsonify([
        t.to_dict()
        for t in tracks
    ])
