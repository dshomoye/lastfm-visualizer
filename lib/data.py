from lib.lastfm import LastFM
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from lib.models import Scrobble, Track, Artist, Album
from collections import Counter
from typing import List, Tuple
import typing
import os


class Scrobbleswrangler:

    def __init__(self,lastfm_username="sonofatailor"):
        """class for processing scrobble data from lastfm
            lastfm_username (str, optional): Defaults to "sonofatailor".
        """

        self.lf = LastFM(username=lastfm_username)
        self.SCROBBLES_CACHE=None
        self.__scrobbles_parsed = False
    
    def __get_scrobbles(self):
        if not self.SCROBBLES_CACHE:
            self.SCROBBLES_CACHE = self.lf.get_scrobbles()
        if not self.__scrobbles_parsed:
            self.__parse_scrobbles()

    def __parse_scrobbles(self):
        """parses the returned dict/json from lastfm into required format
        """

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

    def get_track_count_in_period(self,start_period: datetime,end_period: datetime, unit="days") -> typing.Counter[datetime]:
        """gets the number of tracks listened to within a given time range/unit
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
            unit (str, optional): Defaults to "days". -
        
        Raises:
            ValueError: -
        
        Returns:
            typing.Counter[datetime]: -
        """

        valid_date_units = [
            "days",
            "weeks",
            "months",
            "years"
        ]
        valid_time_units = ["hours"]
        if unit in valid_date_units:
            return self._get_track_count_in_date_period(start_period,end_period,unit)
        elif unit in valid_time_units:
            return self._get_track_count_in_time_period(start_period,end_period,unit)
        else: 
            raise ValueError(f"Unsupported unit type {unit}")
    
    def _get_track_count_in_date_period(self,start_period: datetime,end_period: datetime, unit="days") -> typing.Counter[datetime]:
        # reset the dates to midnight
        start_date = datetime.combine(start_period.date(), datetime.min.time())
        end_date = datetime.combine(end_period.date(), datetime.min.time())
        period_increment = {
            "days": relativedelta(days=1),
            "weeks":relativedelta(weeks=1),
            "months":relativedelta(months=1),
            "years":relativedelta(years=1)
        }
        return self.__get_track_count_with_delta(start_date,end_date,period_increment[unit])

    def get_top_tracks_for_period(self, start_period: datetime,end_period: datetime, number_of_tracks=5) -> List[typing.Dict[str,typing.Any]]:
        """returns most scrobbled tracks within given time period)
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
            number_of_tracks (int, optional): Defaults to 5. -
        
        Returns:
            List[typing.Dict[str,typing.Any]]: -
        """

        return list({"track":t.dict,"played":c} for t,c in 
            self.get_tracks_and_count_for_period(start_period,end_period)
            .most_common(number_of_tracks))
    
    def _get_track_count_in_time_period(self,start_period: datetime,end_period: datetime, unit="hours") -> Counter:
        period_increment = {
            "hours":relativedelta(hours=1)
        }
        return self.__get_track_count_with_delta(start_period,end_period,period_increment=period_increment[unit])


    def __get_track_count_with_delta(self,start_period: datetime,end_period: datetime, period_increment: relativedelta) -> typing.Counter[datetime]:
        track_count: Counter = Counter()
        while end_period >= start_period:
            track_count[start_period]= sum(self.get_tracks_and_count_for_period(start_period,end_period).values())
            start_period+=period_increment
        return track_count
    
    def get_scrobbles_in_period(self, start_period: datetime, end_period: datetime) -> List[Scrobble]:
        """get the tracks and datetime, "Scrobbles" for given period
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
        
        Returns:
            List[Scrobble]: -
        """

        self.__get_scrobbles()
        return [ scrobble.dict for scrobble in self.SCROBBLES_CACHE if start_period <= scrobble.date <= end_period]


    def get_tracks_and_count_for_period(self, start_period: datetime, end_period: datetime) -> typing.Counter[Track]:
        """gets all the tracks withing given period and returns Counter of how many times each were scrobbled
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
        
        Returns:
            typing.Counter[Track]: -
        """

        self.__get_scrobbles()
        return Counter((scrobble.track for scrobble in self.SCROBBLES_CACHE if start_period <= scrobble.date <= end_period ))   
    
    def get_top_artists_for_period(self, start_period: datetime, end_period: datetime, number_of_artists=5) -> List[typing.Dict[str,typing.Any]]:
        """[summary]
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
            number_of_artists (int, optional): Defaults to 5. -
        
        Returns:
            List[typing.Dict[str,typing.Any]]: -
        """

        return list( {"artist": track.artist_name, "played":count} for track, count in self.get_tracks_and_count_for_period(start_period,end_period)
        .most_common(number_of_artists) )
    
    def get_top_albums_for_period(self, start_period: datetime, end_period: datetime, number_of_albums=5) -> List[typing.Dict[str,typing.Any]]:
        """[summary]
        
        Args:
            start_period (datetime): -
            end_period (datetime): -
            number_of_albums (int, optional): Defaults to 5. -
        
        Returns:
            List[typing.Dict[str,typing.Any]]: -
        """
        return list( {"album": track.album_name, "album artist": track.artist_name, "played":count} for track, count in self.get_tracks_and_count_for_period(start_period,end_period)
        .most_common(number_of_albums) )

        #return list(map(lambda track: ({"album":track[0].album_name}, track[1]), 
         #               self.get_tracks_and_count_for_period(start_period,end_period).most_common(number_of_albums)))
        


if __name__ == "__main__":
    d = Scrobbleswrangler()
    now = datetime.now()
    start = now+relativedelta(months=-5)
    end = start+relativedelta(days=5)
    a = d.get_top_tracks_for_period(start_period=start,end_period=end, number_of_tracks=2)
    b = d.get_top_artists_for_period(start_period=start,end_period=end, number_of_artists=2)
    c = d.get_top_albums_for_period(start_period=start,end_period=end, number_of_albums=2)
    print(b)
    print(c)
    #a = d.get_track_count_in_period(start,end,unit="hours")
    print(a)