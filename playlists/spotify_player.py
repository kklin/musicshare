import threading

import spotify

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
        self.curr_playing = None

    def on_connection_state_updated(self,session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()

    def play(self, track_uri):
        '''Plays the given track, regardless of whether or not there is a song
        currently playing'''
        track = self.session.get_track(track_uri).load()
        self.session.player.load(track)
        self.session.player.play()
        # TODO: look at return value player.play() ?
        self.is_playing = True
        self.curr_playing = track_uri # TODO: fill in with pyechonest obj?
        return self.is_playing

    def stop(self):
        pass

    def skip(self):
        pass

    def play_state(self):
        pass

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
