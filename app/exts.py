from flask_socketio import SocketIO
from flask_login import LoginManager


login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins='https://dj.corye.me')
