from app.exts import db

class Party(db.Model):
    __tablename__ = 'party'
    id = db.Column(db.String, primary_key=True)
    host = db.Column(db.String)
    currently_playing = db.Column(db.String)

class VoteToSkip(db.Model):
    __tablename__ = 'votetoskip'

    user = db.Column(db.String, primary_key=True)
    party_id = db.Column(db.String, db.ForeignKey('party.id'))
