from datetime import datetime
import json
import requests
import os


class LastFM:
    lastfm_api = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self):
        self.API_KEY=os.environ["LASTFM_API_KEY"]

    def get_user_tracks(self, username):
        """
        get all tracks for user.

        args:
            (str) username: lastfm username to retrieve all tracks for
        returns:
            (dict) tracks: dictionary representation of user's scrobbles
        """
        page=0
        total_pages = 1
        tracks={}
        print("downloading....")
        while total_pages > page:
            page+=1
            t = self.__get_user_track_page(username,page)
            total_pages = int(t["recenttracks"]["@attr"]["totalPages"])
            tracks = {**t,**tracks}
            progress=int(page/total_pages*100)
            print(f"\r {'=' * int(progress/2)}>  {progress}% done",end="")
        return tracks
    
    def __get_user_track_page(self,username,page):
        payload = {
            "method":"user.getRecentTracks",
            "user":username,
            "limit":200,
            "page":page
        }
        r = self.__do_request("GET",payload)
        return r.json()

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
    tracks = lf.get_user_tracks("sonofatailor")
    print(tracks["recenttracks"]["track"][0]['name'])
