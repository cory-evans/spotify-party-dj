import bcrypt
from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(300), unique=True)
    _password = db.Column(db.Binary(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.hashpw(value.encode(), bcrypt.gensalt())

    def check_password(self, passwd):
        return bcrypt.checkpw(passwd.encode(), self.password)

    def __bool__(self):
        return bool(self.email)
