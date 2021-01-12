import datetime
import typing
import pydantic

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, Query

from app.database import Base


artistAlbumTable = Table('artistalbum', Base.metadata,
    Column('artist_id', Integer, ForeignKey('artist.db_id'), nullable=False),
    Column('album_id', Integer, ForeignKey('album.db_id'), nullable=False)
)

artistTrackTable = Table('artisttrack', Base.metadata,
    Column('artist_id', Integer, ForeignKey('artist.db_id'), nullable=False),
    Column('track_id', Integer, ForeignKey('track.db_id'), nullable=False)
)

class AlbumImageTable(Base):
    __tablename__ = 'albumimage'

    db_id = Column(Integer, primary_key=True)

    height = Column(Integer)
    width = Column(Integer)
    url = Column(String)

    album_id = Column(Integer, ForeignKey('album.db_id'), nullable=False)

class AlbumTable(Base):
    __tablename__ = 'album'

    db_id = Column(Integer, primary_key=True)

    album_group = Column(String)
    album_type = Column(String)
    artists = relationship(
        'ArtistTable',
        secondary=artistAlbumTable,
        back_populates='albums'
    )

    href = Column(String)
    id = Column(String)
    images = relationship('AlbumImageTable', lazy='dynamic')

    name = Column(String)
    type = Column(String)
    uri = Column(String)


class ArtistImageTable(Base):
    __tablename__ = 'artistimage'

    db_id = Column(Integer, primary_key=True)

    height = Column(Integer)
    width = Column(Integer)
    url = Column(String)

    artist_id = Column(Integer, ForeignKey('artist.db_id'), nullable=False)
    artist = relationship('ArtistTable')

class ArtistTable(Base):
    __tablename__ = 'artist'

    db_id = Column(Integer, primary_key=True)

    href = Column(String)
    id = Column(String)
    name = Column(String)
    type = Column(String)
    uri = Column(String)
    images = relationship('ArtistImageTable', lazy='dynamic')

    albums = relationship(
        'AlbumTable',
        secondary=artistAlbumTable,
        back_populates='artists'
    )

    tracks = relationship(
        'TrackTable',
        secondary=artistTrackTable,
        back_populates='artists'
    )


class UserTable(Base):
    __tablename__ = 'user'

    db_id = Column(Integer, primary_key=True)

    authenticated = Column(Boolean, default=False)

    id = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    email = Column(String)
    href = Column(String)
    uri = Column(String)

    images = relationship('UserImageTable', lazy='dynamic')

    access_token = Column(String)
    refresh_token = Column(String)
    expires = Column(DateTime)
    scope = Column(String)
    token_type = Column(String)


class UserImageTable(Base):
    __tablename__ = 'userimage'

    db_id = Column(Integer, primary_key=True)

    height = Column(Integer)
    width = Column(Integer)
    url = Column(String)

    user_id = Column(Integer, ForeignKey(UserTable.db_id), nullable=False)
    user = relationship('UserTable')

class TrackTable(Base):
    __tablename__ = 'track'

    db_id = Column(Integer, primary_key=True)

    uri = Column(String)

    album_id = Column(Integer, ForeignKey('album.db_id'), nullable=False)
    album = relationship('AlbumTable')

    artists = relationship(
        'ArtistTable',
        secondary=artistTrackTable,
        back_populates='tracks'
    )

    duration_ms = Column(Integer)
    explicit = Column(Boolean)
    href = Column(String)
    id = Column(String)

    name = Column(String)
    type = Column(String)


class PartyTable(Base):
    __tablename__ = 'party'

    db_id = Column(Integer, primary_key=True)

    id = Column(String, unique=True, nullable=False)

    host_id = Column(Integer, ForeignKey('user.db_id'), nullable=False)
    host = relationship('UserTable')

    currently_playing_id = Column(Integer, ForeignKey(TrackTable.db_id))
    currently_playing = relationship('TrackTable')

class PartyMemberTable(Base):
    __tablename__ = 'partymember'
    db_id = Column(Integer, primary_key=True)

    party_id = Column(Integer, ForeignKey('party.db_id'), nullable=False)
    party = relationship('PartyTable')

    user_id = Column(Integer, ForeignKey('user.db_id'), nullable=False)
    user = relationship('UserTable')

class QueueItemTable(Base):
    __tablename__ = 'queue'

    db_id = Column(Integer, primary_key=True)

    track_id = Column(Integer, ForeignKey('track.db_id'), nullable=False)
    track = relationship('TrackTable')

    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    next_playable = Column(DateTime, default=datetime.datetime.utcnow)


###################################################
#                PYDANTIC MODELS                  #
###################################################
class OrmBaseModel(pydantic.BaseModel):
    db_id: typing.Optional[int]

    @pydantic.validator('*', pre=True)
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()

        return v

    class Config:
        orm_mode = True

class Image(OrmBaseModel):
    height: typing.Optional[int] = None
    width : typing.Optional[int] = None
    url   : str


class User(OrmBaseModel):
    id: typing.Optional[str] = None
    authenticated: typing.Optional[bool] = False

    display_name: typing.Optional[str] = None
    email: typing.Optional[str] = None
    href: typing.Optional[str] = None
    uri: typing.Optional[str] = None

    images: typing.Optional[typing.List[Image]] = None

    access_token: typing.Optional[str] = None
    refresh_token: typing.Optional[str] = None
    expires: typing.Optional[datetime.datetime] = None
    scope: typing.Optional[str] = None
    token_type: typing.Optional[str] = None

    @property
    def is_authenticated(self):
        return self.authenticated


    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return self.id is not None

    def get_id(self):
        return self.db_id


class Artist(OrmBaseModel):
    '''Simplified'''
    href: str
    id: str
    name: str
    type: str
    uri: str


class Album(OrmBaseModel):
    '''Simplified'''
    album_group: str
    album_type: str
    artists: typing.List[Artist]

    href: str
    id: str
    images: typing.List[Image]

    name: str
    type: str
    uri: str

class Track(OrmBaseModel):
    uri: str
    album: Album
    artists: typing.List[Artist]

    duration_ms: int
    explicit: bool
    href: str
    id: str

    name: str
    type: str


class QueueItem(OrmBaseModel):
    track: Track
    date_added: datetime.datetime
    next_playable: datetime.datetime


class Party(OrmBaseModel):
    id : str
    currently_playing: typing.Optional[Track] = None

    queue: typing.Optional[typing.List[QueueItem]] = None

class PartyMember(OrmBaseModel):
    party: Party
    user: User
