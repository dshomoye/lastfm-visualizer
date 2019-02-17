from sqlalchemy import func, desc
from sqlalchemy import Column, String, Date, Time, DateTime, Integer, ForeignKey, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from flask_sqlalchemy import SQLAlchemy
from typing import List, Dict, Any
# from app import db

db = SQLAlchemy()


class Track(db.Model):
    __tablename__ = 'tracks'
    __table_args__ = (UniqueConstraint('title','album','artist'),)

    id = Column(Integer, primary_key=True)
    title = Column(String(256), index=True)
    album = Column(String(256))
    artist = Column(String(256))

    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {
            "title":self.title,
            "album":self.album,
            "artist":self.artist
        }

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (UniqueConstraint('name'),)
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    last_update = Column(DateTime)

    def __repr__(self):
        return f'<User: {self.name}'

class Scrobble(db.Model): 
    __tablename__ = 'scrobbles'
    __table_args__ = (UniqueConstraint('date','time','user_id'),)
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    date = Column(Date)
    time = Column(Time)
    datetime = Column(DateTime)
    track_id = Column(Integer, ForeignKey('tracks.id'))
    track = relationship('Track')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')

    def __init__(self,*args,**kwargs):
        super(Scrobble, self).__init__(**kwargs)
        self.timestamp = kwargs['timestamp']
        self.datetime = datetime.fromtimestamp(self.timestamp)
        self.date = self.datetime.date()
        self.time = self.datetime.time()
        self.track: Track = kwargs['track']

    def __repr__(self):
        return f"<Scrobble: Date:{self.date} {self.time} {self.track} {self.user} >"
