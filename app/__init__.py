import logging
from flask import Flask, _app_ctx_stack

from sqlalchemy.orm import scoped_session

from app.views import core, party, auth
from app.exts import socketio, login_manager
from app.database import SessionLocal, engine
from app import models

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings.DevelopmentConfig')

    # Register views
    for package in [core, party, auth]:
        app.register_blueprint(package.bp)

    app.db = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
    socketio.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return app.db.query(models.User).get(user_id)

    return app
