from flask import Flask

from app.views import core, party
from app.exts import scheduler, db, socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings.DevelopmentConfig')

    # Register views
    for package in [core, party]:
        app.register_blueprint(package.bp)

    db.app = app
    db.init_app(app)
    socketio.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    return app
