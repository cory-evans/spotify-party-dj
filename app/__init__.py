import logging
from flask import Flask

from app.views import core, party, auth
from app.exts import cache, db, socketio

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings.DevelopmentConfig')

    # Register views
    for package in [core, party, auth]:
        app.register_blueprint(package.bp)

    db.app = app
    db.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)

    return app
