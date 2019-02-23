import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from typing import Optional, List, Callable
from lib.errors import LastFMUserNotFound, ScrobbleFetchFailed, FireStoreError
from lib.models import Track, Scrobble
from flask import current_app as app
from flask import g
import sys
import os
import pickle
from lib.database import DbHelper

class LastFMHelper:
    lastfm_api = "http://ws.audioscrobbler.com/2.0/"
    key = None

    key = os.getenv('LASTFM_API_KEY')

    def __init__(self, api_key: Optional[str]=key, username: str='sonofatailor') -> None:
        self.API_KEY=api_key
        self.username=username
        self.SCROBBLES_CACHE: dict={}
        self.__scrobbles_parsed = False
        self.SCROBBLE_FILE=f'{username}.scrobbles'
        if not self.API_KEY and not app.config['TESTING']: raise ValueError("No API KEY passed to LastFM or set in env")
        self.db = DbHelper(self.username)
        # self.get_or_update_user_scrobbles()


    def get_or_update_user_scrobbles(self) -> List[dict]:
        """get scrobbles dict
        
        Returns:
            List[dict]: dict of scrobbles from lastfm
        """

        if self._is_new_lf_user():
            print("Initializing new User!")
            self.SCROBBLES_CACHE['scrobbles'] = []
            self.db.add_user_to_db()
            s = self._get_scrobbles_from_lf()
        else:
            last_update = self.db.get_last_update()
            if last_update <= datetime.now():
                payload = {'from': int(last_update.timestamp())}
                payload['to'] = datetime.now()
                s =self._get_scrobbles_from_lf(payload=payload)
        return  s
    
    def get_scrobbles_in_period(self,start_period: datetime, end_period: datetime) -> List[Scrobble]:
        return [ scrobble for scrobble in self.SCROBBLES_CACHE['scrobbles'] if start_period <= scrobble.date <= end_period]

    def _get_scrobbles_from_lf(self,payload: dict={}) -> dict:
        page, total_pages = 0,1
        if 'scrobbles' not in self.SCROBBLES_CACHE: self.SCROBBLES_CACHE['scrobbles'] = []
        print(f"downloading scrobbles for {self.username}... started at {datetime.now()}")
        while total_pages > page:
            page+=1
            try:
                scrobbles_in_page = self.__get_scrobbles_page(page=page,payload=payload)
            except ScrobbleFetchFailed:
                self.db.set_user_update_to_min()
                raise ScrobbleFetchFailed
            parsed_scrobbles = self.__parse_scrobbles(scrobbles_in_page["recenttracks"]["track"])
            self.SCROBBLES_CACHE['scrobbles']+= parsed_scrobbles
            self._write_scrobbles_to_db(parsed_scrobbles)
            total_pages = int(scrobbles_in_page["recenttracks"]["@attr"]["totalPages"])
            progress=int(page/total_pages*100) if total_pages else 0
            print(f"\r {'=' * int(progress/2)}>  {progress}%",end="")
        print(f"downloaded, ended at {datetime.now()}")
        if self.SCROBBLES_CACHE['scrobbles']:
            self.SCROBBLES_CACHE['last_update']=int(datetime.now().timestamp())
        if not self.db: self.__write_scrobbles_to_cache_file()
        return self.SCROBBLES_CACHE
    
    def _write_scrobbles_to_db(self, scrobbles: List[Scrobble]) -> None:
        self.db.write_scrobbles_to_db(scrobbles)


    def __parse_scrobbles(self, scrobbles: List[dict]) -> List[Scrobble]:
        parsed_scrobbles: List[Scrobble]=[]
        for scrobble in scrobbles:
            t = Track(title=scrobble["name"],artist=scrobble["artist"]['#text'],album=scrobble["album"]['#text'])
            if "date" in scrobble:
                s = Scrobble(track=t,timestamp=int(scrobble["date"]["uts"])) #type:ignore
            #set currently playing to now
            else:
                try:
                    if scrobble["@attr"]["nowplaying"] == 'true': 
                        s = Scrobble(track=t,timestamp=int(datetime.now().timestamp())) #type:ignore
                except:
                    continue
            parsed_scrobbles.append(s)
        return parsed_scrobbles


    def _is_new_lf_user(self) -> bool:
        """check if user scrobbles have been saved already
        
        Returns:
            bool:
        """
        try:
            return self.db.is_new_user(self.username)
        except Exception:
            return not self.__read_scrobbles_from_cache_file()
    

    def __get_scrobbles_page(self,page: int, payload: dict = {}) -> dict:
        """gets a single page of a request from last fm
        
        Args:
            page (int): [the page number to get]
        
        Raises:
            LastFMUserNotFound: [error]
            ScrobbleFetchFailed: [error]
        
        Returns:
            dict: [json of request result]
        """
        payload['method'] = "user.getRecentTracks"
        payload['user'] = self.username
        payload['limit'] = 200
        payload['page'] = page
        r = self.__do_request("GET",payload)
        if 'error' in r.json() and r.json()["error"] == 6:
            raise LastFMUserNotFound("the username is not found on LastFM")
        elif r.status_code != 200:
            raise ScrobbleFetchFailed(f"An error occured getting srobbles from LastFM, response:{r.text}")
        return r.json() 


    def __write_scrobbles_to_cache_file(self) -> None:
        with open(self.SCROBBLE_FILE, 'wb') as output:
            pickle.dump(self.SCROBBLES_CACHE, output, pickle.HIGHEST_PROTOCOL)
    
    
    def __read_scrobbles_from_cache_file(self) -> bool:
        """read scrobble from cache file and save to instance cache dict
        
        Returns:
            bool: if read and save was successful
        """

        try:
            with open(self.SCROBBLE_FILE, 'rb') as input:
                self.SCROBBLES_CACHE = pickle.load(input)
            return True
        except:
            return False
        

    def __do_request(self, http_method, payload):
        """makes a `request` call using the provided data:
        
        Args:
            http_method (str): 
            payload (str): the payload to encode as part of request, 
            format and api_key are auto appended
        
        Returns:
            [type]: [description]
        """

        request_methods = {
            "GET":requests.get,
            "POST":requests.post
        }
        payload["format"]="json"
        payload["api_key"]=self.API_KEY
        r: function = request_methods[http_method]
        return r(self.lastfm_api,params=payload)


if __name__=="__main__":
    lf = LastFMHelper(username="sonofatailor")
    tracks = lf.get_or_update_user_scrobbles()
    print(tracks[-1])
