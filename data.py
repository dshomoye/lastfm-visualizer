from lastfm import LastFM
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import Scrobble, Track
 
import os


class DataHelper:

    def __init__(self):
        self.API_KEY=os.environ["LASTFM_API_KEY"]
        self.lf = LastFM(api_key=self.API_KEY)
        self.SCROBBLES_CACHE=None
        self.__scrobbles_parsed = False
    
    def __get_scrobbles(self, end=None):
        if not self.SCROBBLES_CACHE:
            self.SCROBBLES_CACHE = self.lf.get_user_scrobbles()
        if not self.__scrobbles_parsed:
            self.__parse_scrobbles()

    def __parse_scrobbles(self):
        parsed_scrobbles=[]
        for scrobble in self.SCROBBLES_CACHE:
            t = Track(title=scrobble["name"],artist=scrobble["artist"]['#text'],album=scrobble["album"]['#text'])
            s = Scrobble(track=t,date=int(scrobble["date"]["uts"]))
            parsed_scrobbles.append(s)
        self.SCROBBLES_CACHE=parsed_scrobbles
        print("parsing done")
        self.__scrobbles_parsed=True


    def get_top_track_for_period(self, start_period: datetime,end_period: datetime):
        tracks = self.get_tracks_for_period(start_period,end_period)
        print(len(tracks))
        return max(tracks,key=tracks.count)


    def get_tracks_for_period(self, start_period: datetime,end_period: datetime):
        self.__get_scrobbles()
        return list((scrobble.track for scrobble in self.SCROBBLES_CACHE if start_period <= scrobble.date <= end_period ))   
        


if __name__ == "__main__":
    d = DataHelper()
    now = datetime.now()
    start = now+relativedelta(months=-5)
    end = start+relativedelta(weeks=5)
    print(f"start {start} and end {end} ")
    a = d.get_top_track_for_period(start_period=start,end_period=end)
    print(a)