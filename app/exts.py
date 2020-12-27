from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

scheduler = APScheduler()
db = SQLAlchemy()
socketio = SocketIO()
