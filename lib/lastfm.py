import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Callable
from errors import LastFMUserNotFound, ScrobbleFetchFailed
import sys
import os
import pickle

class LastFM:
    lastfm_api = "http://ws.audioscrobbler.com/2.0/"
    key = None

    if "LASTFM_API_KEY" in os.environ:
        key = os.environ["LASTFM_API_KEY"]

    def __init__(self, api_key: Optional[str]=key, username: str='sonofatailor') -> None:
        self.API_KEY=api_key
        self.username=username
        if not self.API_KEY: raise ValueError("No API KEY passed to LastFM or set in env")
        self.SCROBBLES_CACHE: List[dict]=[]
        self.SCROBBLE_FILE=f'{username}.scrobbles'

    def get_scrobbles(self) -> List[dict]:
        """
        get all tracks for user.

        args:
            (str) username: lastfm username to retrieve all tracks for
        returns:
            (list) tracks: dictionary representation of user's scrobbles
        """
        if self.SCROBBLES_CACHE:
            return self.SCROBBLES_CACHE
        else:
            if self.__read_scrobbles_from_cache_file(): return self.SCROBBLES_CACHE
        page, total_pages = 0,1
        print("downloading...")
        while total_pages > page:
            page+=1
            scrobbles_in_page = self.__get_scrobbles_page(page)
            self.SCROBBLES_CACHE+=scrobbles_in_page["recenttracks"]["track"]
            total_pages = int(scrobbles_in_page["recenttracks"]["@attr"]["totalPages"])
            progress=int(page/total_pages*100)
            print(f"\r {'=' * int(progress/2)}>  {progress}% done",end="")
        print("downloaded")
        self.__write_scrobbles_to_cache_file()
        return self.SCROBBLES_CACHE
    
    def __get_scrobbles_page(self,page: int) -> dict:
        """gets a single page of a request from last fm
        
        Args:
            page (int): [the page number to get]
        
        Raises:
            LastFMUserNotFound: [error]
            ScrobbleFetchFailed: [error]
        
        Returns:
            dict: [json of request result]
        """

        payload = {
            "method":"user.getRecentTracks",
            "user":self.username,
            "limit":200,
            "page":page
        }
        r = self.__do_request("GET",payload)
        if r.json()["error"] == 6:
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
            cache_age = datetime.fromtimestamp(os.path.getmtime(self.SCROBBLE_FILE))
            if cache_age + relativedelta(hours=24) > datetime.now() :
                with open(self.SCROBBLE_FILE, 'rb') as input:
                    self.SCROBBLES_CACHE = pickle.load(input)
                return True
            else: return False
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
