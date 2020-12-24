from werkzeug.utils import import_string

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.views import core, api


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.settings.DevelopmentConfig')

    # Register views
    app.register_blueprint(
        core.bp
    )
    app.register_blueprint(
        api.bp
    )

    db.init_app(app)

    return app
