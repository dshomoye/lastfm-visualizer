from datetime import datetime
from functools import total_ordering
from dateutil.tz import UTC

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
    def __init__(self, title: str, artist_name: str, album_name: str, artist = None, album = None):
        """[summary]
        
        Args:
            title (str): [description]
            artist_name (str): [description]
            album_name (str, optional): Defaults to None. [description]
            artist ([type], optional): Defaults to None. [description]
            album ([type], optional): Defaults to None. [description]
        """

        self.title = title
        self.artist_name = artist_name
        self.album_name = album_name
        self.artist: Artist = artist
        self.album: Album = album
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
            "Date":  str(self.date)
        }

    def __lt__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date < other.date
    
    def __eq__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date == other.date and self.track == other.track
    
    def __repr__(self):
        return f"{{Track: {self.track}, Date: {self.date} }}"


if __name__ == "__main__":
    test = Track(artist_name="Moelogo",title="Ireti", album_name="Ireti")
    print(test)
    