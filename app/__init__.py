import logging
from flask import Flask, _app_ctx_stack

from sqlalchemy.orm import scoped_session

from app.views import core, party, auth
from app.exts import socketio, login_manager
from app.database import SessionLocal, engine
from app import models

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

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
        user = app.db.query(models.UserTable).get(user_id)
        user_model = models.User.from_orm(user)
        return user_model


    return app
