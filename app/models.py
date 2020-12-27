from app.exts import db

class Party(db.Model):
    __tablename__ = 'party'
    id = db.Column(db.String, primary_key=True)
    host = db.Column(db.String)
    currently_playing = db.Column(db.String)
