import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from typing import Optional, List, Callable
from lib.errors import LastFMUserNotFound, ScrobbleFetchFailed
from lib.models import Track, Scrobble
from storage import FireStoreHelper
from flask import current_app as app
from flask import g
import sys
import os
import pickle


def _get_firestore() -> FireStoreHelper:
    fs = getattr(g, '_firestore', None)
    print('tried firestore')
    print(fs)
    if fs is None:
        print("didnt get firestore")
        fs = g._firestore = FireStoreHelper("users")
    return fs

class LastFM:
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
        self.fs = None if app.config['TESTING'] else _get_firestore()


    def get_scrobbles(self) -> List[dict]:
        """get scrobbles dict
        
        Returns:
            List[dict]: dict of scrobbles from lastfm
        """

        if self._new_lf_user():
            self.SCROBBLES_CACHE['scrobbles'] = []
            self._get_scrobbles_from_lf()
        else:
            if datetime.fromtimestamp(self.SCROBBLES_CACHE['last_update'])+relativedelta(minutes=1) <= datetime.now():
                payload = {'from':self.SCROBBLES_CACHE['last_update']}
                payload['to'] = int(datetime.now().timestamp())
                self._get_scrobbles_from_lf(payload=payload)
        """         if not self.__scrobbles_parsed:
            self.__parse_scrobbles() """
        return  self.SCROBBLES_CACHE['scrobbles']


    def _get_scrobbles_from_lf(self,payload: dict={}) -> dict:
        page, total_pages = 0,1
        print(f"downloading scrobbles for {self.username}... started at {datetime.now()}")
        while total_pages > page:
            page+=1
            scrobbles_in_page = self.__get_scrobbles_page(page=page,payload=payload)
            self.SCROBBLES_CACHE['scrobbles']+=self.__parse_scrobbles(scrobbles_in_page["recenttracks"]["track"])
            total_pages = int(scrobbles_in_page["recenttracks"]["@attr"]["totalPages"])
            progress=int(page/total_pages*100) if total_pages else 0
            print(f"\r {'=' * int(progress/2)}>  {progress}%",end="")
        print(f"downloaded, ended at {datetime.now()}")
        self.SCROBBLES_CACHE['last_update']=int(datetime.now().timestamp())
        self.__write_scrobbles_to_cache_file()
        return self.SCROBBLES_CACHE


    def __parse_scrobbles(self, scrobbles: List[dict]) -> List[Scrobble]:
        parsed_scrobbles: List[Scrobble]=[]
        for scrobble in scrobbles:
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
        return parsed_scrobbles


    def _new_lf_user(self) -> bool:
        """check if user scrobbles have been saved already
        
        Returns:
            bool:
        """

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
        if self.fs:
            self.fs.save_user_scrobbles(
                username=self.username,
                scrobbles=self.SCROBBLES_CACHE['scrobbles'],
                last_update=self.SCROBBLES_CACHE['last_update']
            )
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
    lf = LastFM(username="sonofatailor")
    tracks = lf.get_scrobbles()
    print(tracks[-1])
