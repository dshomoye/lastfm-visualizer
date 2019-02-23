from sqlalchemy import create_engine, func, desc
from sqlalchemy import Column, String, Date, Time, DateTime, Integer, ForeignKey, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from flask_sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any
from lib.models import Scrobble, Track, User, db


class DbHelper():

    def __init__(self,username: str):
        from app import db
        db.create_all()
        if not db:
            raise ValueError("DB Initialization failed")
        else:
            self.session = db.session
        self.user = self.session.query(User).filter_by(name = username).first()
        if not self.user: self.user = User(name=username)


    def add_user_to_db(self):
        self.session.add(self.user)
        self.session.commit()
        self.user = self.session.query(User).filter_by(name = self.user.name).first()
    
    def get_last_update(self):
        return self.session.query(User).filter_by(name=self.user.name).first().last_update

            
    def get_all_scrobbles_from_db(self) -> List[Scrobble]:
        return self.session.query(Scrobble).all()

    def get_scrobbles_in_period(self, start_period: datetime, end_period: datetime) -> List[Scrobble]:
        result = self.session.query(Scrobble)\
            .filter(Scrobble.datetime>=start_period)\
                .filter(Scrobble.datetime<=end_period)\
                    .filter(Scrobble.user==self.user).all()
        return [ scrobble.to_dict() for scrobble in result ]

    
    def get_top_tracks_for_period(self,start_period: datetime, end_period: datetime, limit: int=5) -> List[Dict[str,Any]]:
        result = self.session.query(Track, func.count(Scrobble.timestamp).label('qty'))\
            .join(Scrobble.track)\
            .filter(Scrobble.datetime>=start_period).filter(Scrobble.datetime<=end_period)\
            .filter(Scrobble.user==self.user)\
            .group_by(Track.title).order_by(desc('qty'))\
            .limit(limit).all()
        
        results: List[Dict] = []
        for r in result:
            results.append({
                "played" : r[1],
                "track" : r[0].title,
                "album" : r[0].album,
                "artist": r[0].artist
            })
        
        return results

    def get_top_albums_for_period(self,start_period: datetime, end_period: datetime, limit: int=5) -> List[Dict[str,Any]]:
        result = self.session.query(Track.album, Track.artist, func.count(Scrobble.timestamp).label('qty'))\
            .join(Scrobble.track)\
            .filter(Scrobble.datetime>=start_period).filter(Scrobble.datetime<=end_period)\
                 .filter(Scrobble.user==self.user)\
            .group_by(Track.album).order_by(desc('qty'))\
            .limit(limit).all()
        results: List[Dict] = []

        for r in result:
            results.append({
                "played": r[2],
                "album": r[0],
                "artist": r[1]
            })
        return results
    
    def get_top_artists_for_period(self,start_period: datetime, end_period: datetime, limit: int=5) -> List[Dict[str,Any]]:

        result = self.session.query(Track.artist, func.count(Scrobble.timestamp).label('qty'))\
            .join(Scrobble.track)\
            .filter(Scrobble.datetime>=start_period).filter(Scrobble.datetime<=end_period)\
                 .filter(Scrobble.user==self.user)\
            .group_by(Track.title).order_by(desc('qty'))\
            .limit(limit).all()

        results: List[Dict] = []
        
        for r in result:
            results.append({
                "played": r[1],
                "artist": r[0]
            })
        return results
    
    def get_track_count_in_period(self,start_period: datetime,end_period: datetime, unit="days") -> Dict[str,int]:
        unit_map = {
            'hours': [ Scrobble.date, func.extract('hour',Scrobble.time)],
            'days': [func.extract('day',Scrobble.date), Scrobble.date],
            #weekday broken for now
            'weekdays':[func.extract('year',Scrobble.date),func.extract('month',Scrobble.date),func.extract('dayofweek',Scrobble.date).label('weekday')],
            'months':[func.extract('year',Scrobble.date),func.extract('month',Scrobble.date)],
            'years':[func.extract('year',Scrobble.date)]
        }
        count = func.count(Scrobble.timestamp).label('count')

        r = self.session.query(*unit_map[unit],count)\
            .filter(self.user==Scrobble.user)\
            .filter(Scrobble.datetime>=start_period).filter(Scrobble.datetime<=end_period)\
                 .filter(Scrobble.user==self.user)\
            .group_by(*unit_map[unit])\
            .order_by(desc(count)).all()
        
        transform_map: Dict[str,DateTime]= {
                'hours': lambda d,h: d + relativedelta(hour=h),
                'days' : lambda d,date: date,
                'weekdays': lambda y,m,w: datetime(y,m,1) + relativedelta(day=1,weekday=w),
                'months': lambda y,m: datetime(y,m,1),
                'years': lambda y: datetime(y,1,1)
            }
        results: Dict = {}
        for result in r:
            f = transform_map[unit]
            temp = list(result)
            c = temp.pop()
            results[str(f(*temp))]=c
        
        return results
    
    def add_track_to_db(self,track,title,album,artist) -> Track:
        t = self.session.query(Track).filter_by(title=title,album=album,artist=artist).first()
        if t: 
            return t
        else:
            self.session.add(track)
            # self.session.commit()
            return track

    def _add_or_ignore_to_db(self, model, object, **kwargs):
        r = self.session.query(model).filter_by(**kwargs).first()
        if not r:
            self.session.add(object)
            return object
        else: 
            return r

    def write_scrobbles_to_db(self, scrobbles: List[Scrobble]) -> None:
        i=0
        for scrobble in scrobbles:
            track=scrobble.track
            t = self._add_or_ignore_to_db(Track,track,title=track.title,artist=track.artist,album=track.album)
            # t = self.add_track_to_db(track,title=track.title,artist=track.artist,album=track.album)
            scrobble.track=None
            self._add_or_ignore_to_db(Scrobble,scrobble,date=scrobble.date,time=scrobble.time)
            scrobble.track = t
            scrobble.user = self.user
            self.session.commit()
            i+=1
        self.user.last_update = datetime.now()
        self.session.commit()
    
    def is_new_user(self,username: str) -> bool:
        r = self.session.query(User).filter_by(name = username).first()
        return r is None
    
    def set_user_update_to_min(self):
        self.user.last_update = datetime(1999,1,1)
        self.session.commit()

if __name__ == "__main__":
    helper = DbHelper(username='testuser')
