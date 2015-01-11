from vote import VoteTracker
import secret

from pyechonest import config, artist, playlist
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

class SongRequest(object):

    def __init__(self, song, requester):
        self.requester = requester
        self.song = song
        self.vote_tracker = VoteTracker()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0} requests {1}:  {2}".format(self.requester.__repr__(),
                self.song.__repr__(), self.vote_tracker.__repr__())


class Playlist(object):

    def __init__(self):
        self.contributors = []
        self.song_list = SongList()
        self.current_song = None
        
    def add_contributor(self, contributor):
        self.contributors.append(contributor)

    def remove_contributor(self, contributor):
        self.contributors.remove(contributor)

class SongList(object):

    def __init__(self):
        self.song_list = []

    def add_song_request(self, song_request):
        self.song_list.append(song_request)

    def remove_song(self, song_id):
        # TODO
        self.song_list.remove(song_id)

    def set_vote(self, song_id, vote):
        """Registers the vote for the given song if it is in the song list.
        Returns True if the vote was updated, and False otherwise
        """
        # TODO: could turn song_list into dict for faster lookup

        for song_request in song_list:
            if song_request.song.id is song_id:
                song_request.vote_tracker.register_vote(vote)
                return True
        return False

    def get_ordered(self):
        pass

    @staticmethod
    def from_top_songs():
        hot_artists = artist.top_hottt()
        hottest_artist = hot_artists[0]
        hot_playlist = playlist.basic(artist_id = hottest_artist.id)
        song_list = SongList()
        for song in hot_playlist:
            song_list.add_song_request(SongRequest(song, None))

        return song_list

    @staticmethod
    def from_spotify_accounts(accounts):
        return SongList()

    def __str__(self):
        return self.song_list.__str__()

    def __repr__(self):
        return self.song_list.__repr__()

class Contributor(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name
