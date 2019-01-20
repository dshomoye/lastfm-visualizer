from lastfm import LastFM
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import Scrobble, Track
from collections import Counter
 
import os


class DataHelper:

    def __init__(self):
        self.API_KEY=os.environ["LASTFM_API_KEY"]
        self.lf = LastFM(api_key=self.API_KEY)
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
            t = Track(title=scrobble["name"],artist=scrobble["artist"]['#text'],album=scrobble["album"]['#text'])
            s = Scrobble(track=t,date=int(scrobble["date"]["uts"]))
            parsed_scrobbles.append(s)
        self.SCROBBLES_CACHE=parsed_scrobbles
        self.__scrobbles_parsed=True


    def get_top_tracks_for_period(self, start_period: datetime,end_period: datetime, number_of_tracks=1) -> list:
        start = datetime.now()
        print(f'time to get all tracks {datetime.now()-start}')
        print(f'start time of max {datetime.now()}')
        return self.get_tracks_for_period(start_period,end_period).most_common(number_of_tracks)


    def get_tracks_for_period(self, start_period: datetime,end_period: datetime) -> Counter:
        self.__get_scrobbles()
        return Counter((scrobble.track for scrobble in self.SCROBBLES_CACHE if start_period <= scrobble.date <= end_period ))   
        


if __name__ == "__main__":
    d = DataHelper()
    now = datetime.now()
    start = now+relativedelta(months=-10)
    end = start+relativedelta(weeks=20)
    a = d.get_top_tracks_for_period(start_period=start,end_period=end, number_of_tracks=5)
    print(f'end time of max {datetime.now()}')
    print(a)