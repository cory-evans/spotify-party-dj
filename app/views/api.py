from flask import (
    Blueprint,
    jsonify,
    current_app,
    request
)

import requests

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/search')
def index():
    header = {
        'Authorization': 'Bearer ' + str(current_app.config.get('SPOTIFY_ACCESS_TOKEN'))
    }

    sq = request.args.get('q', None)
    if sq is None:
        return jsonify({})

    r = requests.get(f'https://api.spotify.com/v1/search?q={sq}&type=track', headers=header)

    d = r.json()
    tracks = d.get('tracks')
    if tracks is None:
        return jsonify({'error': 'tracks is none'})

    return jsonify(tracks['items'])
