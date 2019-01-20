import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
import os
import pickle

class LastFM:
    lastfm_api = "http://ws.audioscrobbler.com/2.0/"
    key = None
    SCROBBLE_FILE="scrobble_cache"

    if "LASTFM_API_KEY" in os.environ:
        key = os.environ["LASTFM_API_KEY"]

    def __init__(self,api_key=key):
        self.API_KEY=api_key
        if not self.API_KEY: raise ValueError("No API KEY passed to LastFM or set in env")
        self.SCROBBLES_CACHE=[]

    def get_user_scrobbles(self, username='sonofatailor'):
        """
        get all tracks for user.

        args:
            (str) username: lastfm username to retrieve all tracks for
        returns:
            (dict) tracks: dictionary representation of user's scrobbles
        """
        if self.SCROBBLES_CACHE:
            return self.SCROBBLES_CACHE
        else:
            if self.__read_scrobbles_from_cache_file(): return self.SCROBBLES_CACHE
        page, total_pages = 0,1
        print("downloading...")
        while total_pages > page:
            page+=1
            t = self.__get_user_track_page(username,page)
            self.SCROBBLES_CACHE+=t["recenttracks"]["track"]
            total_pages = int(t["recenttracks"]["@attr"]["totalPages"])
            progress=int(page/total_pages*100)
            print(f"\r {'=' * int(progress/2)}>  {progress}% done",end="")
        print("downloaded")
        self.__write_scrobbles_to_cache_file()
        return self.SCROBBLES_CACHE
    
    def __get_user_track_page(self,username,page):
        payload = {
            "method":"user.getRecentTracks",
            "user":username,
            "limit":200,
            "page":page
        }
        r = self.__do_request("GET",payload)
        return r.json() 
    
    def __write_scrobbles_to_cache_file(self):
        with open(self.SCROBBLE_FILE, 'wb') as output:
            pickle.dump(self.SCROBBLES_CACHE, output, pickle.HIGHEST_PROTOCOL)
    
    def __read_scrobbles_from_cache_file(self):
        try:
            cache_age = datetime.fromtimestamp(os.path.getmtime(self.SCROBBLE_FILE))
            if cache_age + relativedelta(hours=1) > datetime.now() :
                with open(self.SCROBBLE_FILE, 'rb') as input:
                    self.SCROBBLES_CACHE = pickle.load(input)
                return True
            else: return False
        except:
            return False
        

    def __do_request(self,http_method,payload):
        request_methods = {
            "GET":requests.get,
            "POST":requests.post
        }
        payload["format"]="json"
        payload["api_key"]=self.API_KEY
        r = request_methods[http_method]
        request = r(self.lastfm_api,params=payload)
        return request  

if __name__=="__main__":
    lf = LastFM()
    start = datetime.now()
    tracks = lf.get_user_scrobbles("sonofatailor")
    end = datetime.now()
    print(f'started at {start} and ended at {end}')
    size = sys.getsizeof(tracks)
    print(f'size of scrobble list is {size}')
    print(tracks[-1])
