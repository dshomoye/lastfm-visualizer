from datetime import datetime
from functools import total_ordering


class Album:
    def __init__(self,name: str):
        self.name = name

class Artist:
    def __init__(self,name: str):
        self.name = name

class Track:
    def __init__(self, title: str, artist_name: str, album_name: str = None, artist = None, album = None):
        self.title = title
        self.artist_name = artist_name
        self.album_name = album_name
        self.artist: Artist = artist
        self.album: Album = album
    

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
        if not isinstance(track, Track): raise AttributeError("must supply a track object to create scrobble!")
        self.track = track
        try:
            self.date = datetime.fromtimestamp(date)
        except ValueError:
            raise ValueError(f"failed to create Scrobble object")

    def __lt__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date < other.date
    
    def __eq__(self,other):
        if not isinstance(other, Scrobble): return NotImplemented
        return self.date == other.date and self.track == other.track
    
    def __repr__(self):
        return f"{{Track: {self.track}, Date: {self.date} }}"\
    
    def get_dict(self):
        return {
            "Title": self.track.title,
            "Artist": self.track.artist_name,
            "Album": self.track.album_name,
            "Date":  str(self.date)
        }
    


if __name__ == "__main__":
    test = Track(artist_name="Moelogo",title="Ireti")
    print(test)