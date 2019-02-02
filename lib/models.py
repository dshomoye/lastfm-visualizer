from datetime import datetime
from functools import total_ordering
from dateutil.tz import UTC # type: ignore
from typing import Optional

class Artist:
    def __init__(self,name: str):
        self.name = name

class Album:
    def __init__(self,name: str, artist: Artist):
        self.artist = artist
        self.name = name
    
    def __repr__(self):
        return f'{{Album: {self.name}, Artist: {self.artist.name} }}'

    def __hash__(self):
        return hash(repr(self))


class Track:
    def __init__(self, title: str, artist_name: str, album_name: str, artist: Artist = None, album: Album = None):
        '''Track object with track info
        
        Args:
            title (str): [description]
            artist_name (str): [description]
            album_name (str): [description]
            artist (Artist, optional): Defaults to None. [description]
            album (Album, optional): Defaults to None. [description]
        '''


        self.title = title
        self.artist_name = artist_name
        self.album_name = album_name
        self.artist: Optional[Artist] = artist
        self.album: Optional[Album] = album
        self.dict = {
            "title": self.title,
            "artist": self.artist_name,
            "album": self.album_name
        }
    

    def __eq__(self,other):
        if not isinstance(other, Track): return NotImplemented
        if ( self.title == other.title and 
                self.album_name == other.album_name and 
                self.artist_name == self.artist_name):
            #only match if all attribute are same
            return True
        
    def __repr__(self):
        return f"{{Title: {self.title}, Album: {self.album_name}, Artist: {self.artist_name}  }}"

    def __hash__(self):
        return hash(repr(self))


@total_ordering
class Scrobble:

    def __init__(self,track: Track, date: int):
        """[summary]
        
        Args:
            track (Track): [description]
            date (int): [description]
        
        Raises:
            AttributeError: 
            ValueError: when getting datetime failes
        """

        if not isinstance(track, Track): raise AttributeError("must supply a track object to create scrobble!")
        self.track = track
        try:
            self.date = datetime.fromtimestamp(date,tz=UTC)
        except ValueError:
            raise ValueError(f"failed to create Scrobble object")
        self.dict = {
            "track": self.track.dict,
            "date":  self.date
        }

    @staticmethod
    def from_dict(scrobble: dict):
        t= Track(
            title=scrobble['track']['title'],
            artist_name=scrobble['track']['artist'],
            album_name=scrobble['track']['album']
        )
        return Scrobble(track=t,date=scrobble['date'].timestamp())

    def __lt__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date < other.date
    
    def __eq__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date == other.date and self.track == other.track
    
    def __repr__(self):
        return f"{self.dict}"
    
    def __hash__(self):
        return hash(self.__repr__())


if __name__ == "__main__":
    test = Track(artist_name="Moelogo",title="Ireti", album_name="Ireti")
    print(test)
    