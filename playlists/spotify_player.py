import threading

import spotify

# TODO: allow support for callbacks
# e.g. the server can subscribe to receive a callback when the song finishes
# playing
class Player(object):
    '''There should only be one instance of this class. It handles playing
    Spotify tracks'''
    # TODO: could we use a singleton design pattern or something to enforce the
    # fact that there's only one Player?

    def __init__(self):
        # Assuming a spotify_appkey.key in the current dir
        self.session = spotify.Session()
        self.audio = spotify.PortAudioSink(self.session)

        loop = spotify.EventLoop(self.session)
        loop.start()

        # self.logged_in = threading.Event()

        # Assuming a previous login with remember_me=True and a proper logout
        # Right now, to login you have to first login through the shell in
        # /spotify/shell.py
        # self.session.on(
        #     spotify.SessionEvent.CONNECTION_STATE_UPDATED, self.on_connection_state_updated)
        # self.session.relogin()
        # self.logged_in.wait()

        self.is_logged_in = False
        self.is_playing = False
        # self.curr_song = None
        self.track_time = -1

    def on_connection_state_updated(self,session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()

    def play_uri(self, track_uri):
        '''Plays the given track, regardless of whether or not there is a song
        currently playing'''
        track = self.session.get_track(track_uri).load()
        self.session.player.load(track)
        self.session.player.play()
        # TODO: look at return value player.play() ?
        self.is_playing = True
        #self.curr_song = track_uri # TODO: fill in with pyechonest obj?
        return self.is_playing

    def play(self, song_request):
        # figure out the track_uri from the song_request and call play_uri
        # just going to make it call play_uri directly for now so it doesn't
        # break other stuff
        self.play_uri(song_request)

    def pause(self):
        self.session.player.play(False)

    def resume(self):
        self.session.player.play()

    def stop(self):
        self.session.player.play(False)
        self.session.player.unload()

    def seek(self, seconds):
        # TODO Check if playing
        self.session.player.seek(int(seconds) * 1000)

    def login(self, username, password):
        '''Authenticate the session using the given username and password'''
        # TODO: return info on whether login successful
        self.session.login(username, password, remember_me=True)

class PlayerState(object):
    '''A class that encapsulates the current state of the player'''

    def __init__(self, playing, time, song):
        self.playing = playing
        self.time = time
        self.song = song

class PlaylistPlayer(Player):
    '''A player that knows about other songs, and can do things like skip to the
    next song'''
    
    def __init__(self, playlist=[]):
        Player.__init__(self)
        self.playlist = playlist
        self.playlist_index = 0

        self.session.on(spotify.SessionEvent.END_OF_TRACK, self.on_end_of_track)

    # TODO: define this for other events too
    def end_track_function(self, function):
        '''This allows an arbitrary function to be run at the end of a track. In
        this way we can do stuff like automatically go to the next song, or
        remove the finished song
        TODO: define some generic functions so that programmers don't always
        have to write their own'''
        self.end_track_function = function

    def on_end_of_track(self, session):
        self.skip()

    def skip(self):
        #  loop back to beginning if at end
        self.playlist_index = (self.playlist_index + 1) % len(self.playlist)
        self.play(self.playlist[self.playlist_index])
        return True

    def update_playlist(self, playlist, playlist_index=None):
        # assign default here because we can't reference self in the arguments
        if not playlist_index:
            playlist_index = self.playlist_index
        # haven't quite figured out how updating playlists is going to work.. we
        # can't just throw in a new playlist because then the indices might be
        # shifted
        self.playlist = playlist
        self.playlist_index = playlist_index

    @property
    def curr_song(self):
        return self.playlist[self.playlist_index]

    def play(self, uri):
        self.playlist_index = self.playlist.index(uri)
        Player.play(self, uri)

    # TODO: the user shouldn't be able to directly call PlaylistPlayer.play()
    # because then the index gets screwed up

