#!/usr/bin/python

# listbox.py

import wx, time, threading

import sys
import socket, select
import settings, network, models, secret, util
from models import SongRequest
from network import NetworkPacket, VoteRequest, Control
from vote import Vote
from spotify_player import PlaylistPlayer

from pyechonest import song, config
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

ID_PLAY = 1
ID_PAUSE = 2
ID_SKIP = 3
ID_RESUME = 4

class ServerGUI(wx.Frame):

    TITLE = "Musicshare Server"
    # TODO: move into network class
    RECV_BUFFER = 4096

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, ServerGUI.TITLE, size=(350, 220))

        # setup GUI
        # containers
        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # listbox for displaying playlist
        self.listbox = wx.ListBox(panel, -1)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)

        # buttons
        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        play = wx.Button(btnPanel, ID_PLAY, 'Play', size=(90, 30))
        pause = wx.Button(btnPanel, ID_PAUSE, 'Pause', size=(90, 30))
        skip = wx.Button(btnPanel, ID_SKIP, 'Skip', size=(90, 30))
        resume = wx.Button(btnPanel, ID_RESUME, 'Resume', size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.play_gui, id=ID_PLAY)
        self.Bind(wx.EVT_BUTTON, self.pause_gui, id=ID_PAUSE)
        self.Bind(wx.EVT_BUTTON, self.skip_gui, id=ID_SKIP)
        self.Bind(wx.EVT_BUTTON, self.resume_gui, id=ID_RESUME)

        vbox.Add((-1, 20))
        vbox.Add(play)
        vbox.Add(pause)
        vbox.Add(resume)
        vbox.Add(skip)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        #TODO: add audio slider

        self.Centre()
        self.Show(True)

        # start the actual server loop
        thread = threading.Thread(target=self.main)
        thread.setDaemon(True)
        thread.start()

    def main(self):
        self.player = PlaylistPlayer()
        # TODO: eventually this information will be gathered from the user
        self.player.login(secret.spotify_username, secret.spotify_password)

        # init instance variables
        self.socket_list = []
        self.socket_to_user = {}
        self.potential_songs = models.SongList.from_top_songs()
        self.master_client = None

        # setup our network connection
        host = socket.gethostname()
        port = settings.port

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(settings.max_clients)

        # add server socket object to the list of readable connections
        self.socket_list.append(server_socket)

        print("Server started on port " + str(port))

        wx.CallAfter(self.update_song_display)

        while True:
            
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [], 0)

            for sock in ready_to_read:
                # a new connection request
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    self.socket_list.append(sockfd)
                    #print("Client (%s, %s) connected" % addr)
                # a message from a client, not a new connection
                else:
                    try:
                        data = sock.recv(ServerGUI.RECV_BUFFER)
                        if data:
                            self.process(sock, data)
                        else:
                            # socket is broken
                            if sock in self.socket_list:
                                print(str(self.socket_to_user[sock]) + " disconnected ")
                                # TODO: if the disconnected user is the master
                                # client, a new master client should be chosen
                                self.socket_list.remove(sock)
                                self.socket_to_user.pop(sock, None)
                    except Exception as e:
                        print(e)
                        continue
            time.sleep(1)

            # TODO: this could be in a different thread?
            self.broadcast_service_announcement()

        server_socket.close()

    def broadcast_service_announcement(self):
        # TODO: we could reuse the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #this is a broadcast socket
        my_ip= socket.gethostbyname(socket.gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs

        data = network.Header.AUTODISCOVER+my_ip
        s.sendto(data, ('<broadcast>', network.AUTODISCOVER_PORT))
        # print("sent service announcement")

    # TODO: could we accidentally have a packet split between buffers?
    def process(self, sock, data):
        packets = data.split(NetworkPacket.DELIMITER)
        try:
            packets.remove('') # not sure why there's that blank string, but we gotta get rid of it
        except:
            pass

        for packet in packets:
            parsed_request = NetworkPacket.parse(packet)
            request_type = type(parsed_request)
            if request_type is network.VoteResponse:
                # this verdict parsing could probably go in network.VoteResponse itself
                verdict = None
                if parsed_request.verdict is 'Y':
                    verdict = Vote.YES
                elif parsed_request.verdict is 'N':
                    verdict = Vote.NO
                elif parsed_request.verdict is 'A':
                    verdict = Vote.ABSTAIN
                else:
                    # uh oh, throw an exception or sumtin'
                    pass
                voter = self.socket_to_user[sock]

                success = self.potential_songs.set_vote(parsed_request.song_id, Vote(voter, verdict))
                if success:
                    #print("Successfully saved vote")
                    song_obj = song.Song(parsed_request.song_id)
                    song_name = song_obj.artist_name + " - " + song_obj.title
                    print("The votes for " + song_name + " now looks like this: ")
                    print(self.potential_songs.get_song(parsed_request.song_id).vote_tracker)
                    wx.CallAfter(self.update_song_display)
                else:
                    print("Hmm.. couldn't save the vote. Maybe the id isn't in the list")
            elif request_type is network.Control:
                self.process_control(parsed_request, sock)
            elif request_type is network.RequestInfo:
                pass
            elif request_type is network.AddSong:
                song_obj = song.Song(parsed_request.song_id)
                song_name = song_obj.artist_name + " - " + song_obj.title
                print("Got a request for: " + song_name)
                song_request = SongRequest(song_obj, self.socket_to_user[sock])
                self.potential_songs.add_song_request(song_request)
                self.request_votes(song_request)
                wx.CallAfter(self.update_song_display)
            elif request_type is network.Register:
                # TODO: reject if same username is already in room
                self.socket_to_user[sock] = parsed_request.username
                #print(str(sock) + " is now associated with id " + str(socket_to_user[sock]))
                #print("Requesting votes on the playlist now")

                # if there's no master client yet (i.e. this is the first
                # client), make this user the master client
                if not self.master_client:
                    self.master_client = parsed_request.username

                # allow the newly connected user to vote on the songs currently
                # in the playlist
                self.request_votes_initial(sock, self.potential_songs)

                print(parsed_request.username + " is now registered!")

    def process_control(self, control_obj, socket):
        user = self.socket_to_user[socket]
        if user !=  self.master_client:
            print("Client ({0}) is trying to control playback when they're not " \
                    "the master client ({1})!".format(user, self.master_client))
            return False

        if control_obj.control is Control.PAUSE:
            print("Pausing")
            self.do_pause()
        if control_obj.control is Control.PLAY:
            print("Playing")
            self.do_play()
        if control_obj.control is Control.SKIP:
            print("Skipping")
            self.do_skip()
        if control_obj.control is Control.RESUME:
            print("Resuming")
            self.do_resume()

    def request_votes_initial(self, sock, potential_songs):
        '''Requests votes when client first connects to the server'''
        for potential_song in potential_songs.song_list:
            print("Requesting vote for " + potential_song.song.id)
            vote_request = VoteRequest(potential_song.song.id)
            vote_request.send(sock)

    def request_votes(self, song_request):
        '''Requests votes for a new song'''
        vote_request = VoteRequest(song_request.song.id)
        for sock in self.socket_to_user.keys():
            vote_request.send(sock)

    # TODO: chars aren't equal width so can't space columns using spaces
    SONG_WIDTH = 50
    VOTE_WIDTH = 30
    REQUESTER_WIDTH = 30
    def update_song_display(self):
        # TODO: we should make a method that gets called whenever the ordering
        # potentially changes. That method would then update the display, and
        # update the Player's playlist. But for now we're just going to put the
        # Player logic in here to quickly test
        self.player.update_playlist(map(util.to_spotify_track_id,
            [song_request.song for song_request in
                self.potential_songs.ordered]))
        self.listbox.Clear()

        # add header
        # HEADER = "SONG".ljust(ServerGUI.SONG_WIDTH) + " | " + "VOTES".ljust(ServerGUI.VOTE_WIDTH) + " | " + "REQUESTER".ljust(ServerGUI.REQUESTER_WIDTH)
        # self.listbox.Append(HEADER)

        # add song requests
        for song_request in self.potential_songs.ordered:
            song_obj = song_request.song
            song_name = song_obj.artist_name + " - " + song_obj.title
            # song_name = song_name.ljust(ServerGUI.SONG_WIDTH)
            vote_tracker = song_request.vote_tracker
            vote_breakdown = "Yes: {0}, No: {1}, Abstain: {2}".format(vote_tracker.number_yes, vote_tracker.number_no, vote_tracker.number_abstain)
            # vote_breakdown = vote_breakdown.ljust(ServerGUI.VOTE_WIDTH)
            requester = str(song_request.requester)
            # requester = requester..ljust(ServerGUI.REQUESTER_WIDTH)
            self.listbox.Append(song_name + " | " + vote_breakdown + " | " + requester)


    # ===== GUI callbacks =====
    def do_play(self):
        to_play = self.potential_songs.ordered[0].song
        track_id = util.to_spotify_track_id(to_play)
        self.player.play(track_id)
        # TODO: remove (or at least change position) song from playlist after played

    def do_pause(self):
        self.player.pause()

    def do_resume(self):
        self.player.resume()

    def do_skip(self):
        self.player.skip()

    def play_gui(self, event):
        self.do_play()

    def pause_gui(self, event):
        self.do_pause()

    def skip_gui(self, event):
        self.do_skip()

    def resume_gui(self, event):
        self.do_resume()

app = wx.App()
ServerGUI(None, -1)
app.MainLoop()
