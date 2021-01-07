from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_caching import Cache

cache = Cache()
db = SQLAlchemy()
socketio = SocketIO()
