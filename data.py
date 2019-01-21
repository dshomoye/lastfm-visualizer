from lastfm import LastFM
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from models import Scrobble, Track
from collections import Counter
import os


class Scrobbleswrangler:

    def __init__(self):
        self.lf = LastFM()
        self.SCROBBLES_CACHE=None
        self.__scrobbles_parsed = False
    
    def __get_scrobbles(self, end=None):
        if not self.SCROBBLES_CACHE:
            self.SCROBBLES_CACHE = self.lf.get_scrobbles()
        if not self.__scrobbles_parsed:
            self.__parse_scrobbles()

    def __parse_scrobbles(self):
        parsed_scrobbles=[]
        for scrobble in self.SCROBBLES_CACHE:
            t = Track(title=scrobble["name"],artist_name=scrobble["artist"]['#text'],album_name=scrobble["album"]['#text'])
            if "date" in scrobble:
                s = Scrobble(track=t,date=int(scrobble["date"]["uts"]))
            #set currently playing to now
            else:
                try:
                    if scrobble["@attr"]["nowplaying"] == 'true': 
                        s = Scrobble(track=t,date=int(datetime.now().timestamp()))
                except:
                    continue
            parsed_scrobbles.append(s)
        self.SCROBBLES_CACHE=parsed_scrobbles
        self.__scrobbles_parsed=True


    def get_top_tracks_for_period(self, start_period: datetime,end_period: datetime, number_of_tracks=1) -> list:
        return self.get_tracks_for_period(start_period,end_period).most_common(number_of_tracks)
    
    def get_track_count_in_period(self,start_period: datetime,end_period: datetime, unit="days", calibrate=True) -> Counter:
        valid_date_units = [
            "weekdays",
            "days",
            "weeks",
            "months",
            "years"
        ]
        valid_time_units = ["hours"]
        if unit in valid_date_units:
            return self.get_track_count_in_date_period(start_period,end_period,unit,calibrate)
        elif unit in valid_time_units:
            return self.get_track_count_in_time_period(start_period,end_period,unit)
        else: 
            raise ValueError(f"Unsupported unit type {unit}")
    
    def get_track_count_in_date_period(self,start_period: datetime,end_period: datetime,calibrate: bool, unit="days") -> Counter:
        if calibrate:
            start_date = datetime.combine(start_period.date(), datetime.min.time())
            end_date = datetime.combine(end_period.date(), datetime.min.time())
        period_increment = {
            "weekdays": relativedelta(weeks=1, weekday=0),
            "days": relativedelta(days=1),
            "weeks":relativedelta(weeks=1),
            "months":relativedelta(months=1),
            "years":relativedelta(years=1)
        }
        return self.__get_track_count_with_delta(start_date,end_date,period_increment[unit])
    
    def get_track_count_in_time_period(self,start_period: datetime,end_period: datetime, calibrate: bool, unit="hours") -> Counter:
        if calibrate: start_period+=relativedelta(minute=0,second=0,microsecond=0)
        period_increment = {
            "hours":relativedelta(hours=1,)
        }
        return self.__get_track_count_with_delta(start_period,end_period,period_increment=period_increment[unit])

    def __get_track_count_with_delta(self,start_period: datetime,end_period: datetime,period_increment: relativedelta):
        track_count = Counter()
        while end_period >= start_period:
            track_count[start_period]= sum(self.get_tracks_for_period(start_period,end_period).values())
            start_period+=period_increment
        return track_count


    def get_tracks_for_period(self, start_period: datetime,end_period: datetime) -> Counter:
        self.__get_scrobbles()
        return Counter((scrobble.track for scrobble in self.SCROBBLES_CACHE if start_period <= scrobble.date <= end_period ))   
    
    def get_top_artists_for_period(self, start_period: datetime,end_period: datetime, number_of_artists=1) -> list:
        return list(map(lambda track: (track[0].artist_name,track[1]), 
                        self.get_tracks_for_period(start_period,end_period).most_common(number_of_artists)))
    
    def get_top_albums_for_period(self, start_period: datetime,end_period: datetime, number_of_albums=1) -> list:
        return list(map(lambda track: (track[0].album_name, track[1]), 
                        self.get_tracks_for_period(start_period,end_period).most_common(number_of_albums)))
        


if __name__ == "__main__":
    d = Scrobbleswrangler()
    now = datetime.now()
    start = now+relativedelta(months=-6)
    end = start+relativedelta(hours=5)
    a = d.get_top_tracks_for_period(start_period=start,end_period=end, number_of_tracks=2)
    b = d.get_top_artists_for_period(start_period=start,end_period=end, number_of_artists=2)
    c = d.get_top_albums_for_period(start_period=start,end_period=end, number_of_albums=2)
    print(b)
    print(c)
    a = d.get_track_count_in_period(start,end,unit="hours")
    print(a)