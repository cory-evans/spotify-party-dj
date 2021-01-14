import datetime
import typing
import pydantic

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, Query

from app.database import Base

class JSONMixin(object):
    RELATIONSHIP_TO_DICT = True

    # def __iter__(self):
    #     return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None, exclude_columns=[]):
        if rel is None:
            rel = self.RELATIONSHIP_TO_DICT

        data = {
            col.key: getattr(self, attr_name)
            for attr_name, col in self.__mapper__.c.items()
            if attr_name not in exclude_columns
        }

        if rel:
            for attr_name, relation in self.__mapper__.relationships.items():
                if attr_name in exclude_columns:
                    continue

                if backref == relation.target:
                    continue

                value = getattr(self, attr_name)
                if isinstance(value, Base):
                    data[attr_name] = value.to_dict(backref=self.__table__, exclude_columns=exclude_columns)

                elif isinstance(value, (Query, list)):
                    data[attr_name] = [
                        i.to_dict(backref=self.__table__, exclude_columns=exclude_columns)
                        for i in value
                    ]
                else:
                    data[attr_name] = None

        return data

    relationship_map = {
        # 'column_name': 'class'
    }

    @classmethod
    def from_dict(cls, data: dict):
        new_cls = cls()

        for col_name, relation in cls.__mapper__.relationships.items():
            if col_name in data:
                rel_cls = globals().get(cls.relationship_map[col_name])
                if isinstance(data[col_name], list):
                    attr = [
                        rel_cls.from_dict(x)
                        for x in data[col_name]
                    ]
                else:
                    attr = rel_cls.from_dict(data[col_name])

                setattr(new_cls, col_name, attr)

        for col_name, col in cls.__mapper__.c.items():
            if col_name in data:
                setattr(new_cls, col_name, data[col_name])

        return new_cls

class ImageMixin(object):

    db_id = Column(Integer, primary_key=True)

    height = Column(Integer)
    width = Column(Integer)
    url = Column(String)

artistAlbum = Table('artistalbum', Base.metadata,
    Column('artist_id', Integer, ForeignKey('artist.db_id'), nullable=False),
    Column('album_id', Integer, ForeignKey('album.db_id'), nullable=False)
)

artistTrack = Table('artisttrack', Base.metadata,
    Column('artist_id', Integer, ForeignKey('artist.db_id'), nullable=False),
    Column('track_id', Integer, ForeignKey('track.db_id'), nullable=False)
)

class AlbumImage(JSONMixin, ImageMixin, Base):
    __tablename__ = 'albumimage'
    album_id = Column(Integer, ForeignKey('album.db_id'), nullable=False)
    album = relationship('Album')

class Album(JSONMixin, Base):
    __tablename__ = 'album'

    relationship_map = {
        'artists': 'Artist',
        'images': 'AlbumImage'
    }

    db_id = Column(Integer, primary_key=True)

    album_group = Column(String)
    album_type = Column(String)
    artists = relationship(
        'Artist',
        secondary=artistAlbum,
        back_populates='albums'
    )

    href = Column(String)
    id = Column(String)
    images = relationship('AlbumImage', lazy='dynamic')

    name = Column(String)
    type = Column(String)
    uri = Column(String)


class ArtistImage(JSONMixin, ImageMixin, Base):
    __tablename__ = 'artistimage'

    artist_id = Column(Integer, ForeignKey('artist.db_id'), nullable=False)
    artist = relationship('Artist')

class Artist(JSONMixin, Base):
    __tablename__ = 'artist'

    relationship_map = {
        'tracks': 'Track',
        'images': 'AlbumImage'
    }

    db_id = Column(Integer, primary_key=True)

    href = Column(String)
    id = Column(String)
    name = Column(String)
    type = Column(String)
    uri = Column(String)
    images = relationship('ArtistImage', lazy='dynamic')

    albums = relationship(
        'Album',
        secondary=artistAlbum,
        back_populates='artists'
    )

    tracks = relationship(
        'Track',
        secondary=artistTrack,
        back_populates='artists'
    )


class User(JSONMixin, Base):
    __tablename__ = 'user'

    relationship_map = {
        'images': 'UserImage'
    }

    db_id = Column(Integer, primary_key=True)

    authenticated = Column(Boolean, default=False)

    id = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    email = Column(String)
    href = Column(String)
    uri = Column(String)

    images = relationship('UserImage', lazy='dynamic')

    access_token = Column(String)
    refresh_token = Column(String)
    expires = Column(DateTime)
    scope = Column(String)
    token_type = Column(String)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        return self.is_authenticated

    def get_id(self):
        return self.db_id

    @property
    def is_anonymous(self):
        return self.is_authenticated


class UserImage(JSONMixin, ImageMixin, Base):
    __tablename__ = 'userimage'

    user_id = Column(Integer, ForeignKey(User.db_id), nullable=False)
    user = relationship('User')


class Track(JSONMixin, Base):
    __tablename__ = 'track'

    relationship_map = {
        'artists': 'Artist',
        'album': 'Album'
    }

    db_id = Column(Integer, primary_key=True)

    uri = Column(String, unique=True, nullable=False)

    album_id = Column(Integer, ForeignKey('album.db_id'), nullable=False)
    album = relationship('Album')

    artists = relationship(
        'Artist',
        secondary=artistTrack,
        back_populates='tracks'
    )

    duration_ms = Column(Integer)
    explicit = Column(Boolean)
    href = Column(String)
    id = Column(String)

    name = Column(String)
    type = Column(String)


class Party(JSONMixin, Base):
    __tablename__ = 'party'

    relationship_map = {
        'host': 'User',
        'currently_playing': 'Track'
    }

    db_id = Column(Integer, primary_key=True)

    id = Column(String, unique=True, nullable=False)

    host_id = Column(Integer, ForeignKey('user.db_id'), nullable=False)
    host = relationship('User')

    currently_playing_id = Column(Integer, ForeignKey('track.uri'))
    currently_playing = relationship('Track')

    next_song_is_in_queue = Column(Boolean, default=False)

class PartyMember(JSONMixin, Base):
    __tablename__ = 'partymember'

    relationship_map = {
        'party': 'Party',
        'user': 'User'
    }

    db_id = Column(Integer, primary_key=True)

    party_id = Column(Integer, ForeignKey('party.db_id'), nullable=False)
    party = relationship('Party')

    user_id = Column(Integer, ForeignKey('user.db_id'), nullable=False)
    user = relationship('User')


class QueueItem(JSONMixin, Base):
    __tablename__ = 'queue'

    db_id = Column(Integer, primary_key=True)

    track_id = Column(Integer, ForeignKey('track.db_id'), nullable=False)
    track = relationship('Track')

    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    next_playable = Column(DateTime, default=datetime.datetime.utcnow)
