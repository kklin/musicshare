#!/usr/bin/python

# listbox.py

import wx, time, threading

import sys
import socket, select
import settings, network, models, secret
from network import NetworkPacket, VoteRequest
from vote import Vote

from pyechonest import song, config
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

ID_NEW = 1
ID_RENAME = 2
ID_CLEAR = 3
ID_DELETE = 4

class ListBox(wx.Frame):

    # TODO: are global variables like this the right choice?
    socket_list = []
    socket_to_user = {}

    potential_songs = models.SongList.from_top_songs()

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 220))

        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.ListBox(panel, -1)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)

        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        new = wx.Button(btnPanel, ID_NEW, 'New', size=(90, 30))
        ren = wx.Button(btnPanel, ID_RENAME, 'Rename', size=(90, 30))
        dlt = wx.Button(btnPanel, ID_DELETE, 'Delete', size=(90, 30))
        clr = wx.Button(btnPanel, ID_CLEAR, 'Clear', size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.NewItem, id=ID_NEW)
        self.Bind(wx.EVT_BUTTON, self.OnRename, id=ID_RENAME)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=ID_CLEAR)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)

        vbox.Add((-1, 20))
        vbox.Add(new)
        vbox.Add(ren, 0, wx.TOP, 5)
        vbox.Add(dlt, 0, wx.TOP, 5)
        vbox.Add(clr, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

        thread = threading.Thread(target=self.main)
        thread.setDaemon(True)
        thread.start()

    def main(self):
        RECV_BUFFER = 4096
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
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            self.process(sock, data)
                        else:
                            # socket is broken
                            if sock in self.socket_list:
                                print(str(socket_to_user[sock]) + " disconnected ")
                                self.socket_list.remove(sock)
                                self.socket_to_user.pop(sock, None)
                    except Exception as e:
                        print(e)
                        continue
            time.sleep(1)

        server_socket.close()

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
                pass
            elif request_type is network.RequestInfo:
                pass
            elif request_type is network.AddSong:
                pass
            elif request_type is network.Register:
                self.socket_to_user[sock] = parsed_request.id
                #print(str(sock) + " is now associated with id " + str(socket_to_user[sock]))
                #print("Requesting votes on the playlist now")
                print(parsed_request.id + " is now registered!")
                self.request_votes(sock, self.potential_songs)

    def request_votes(self, sock, potential_songs):
        for potential_song in potential_songs.song_list:
            print("Requesting vote for " + potential_song.song.id)
            vote_request = VoteRequest(potential_song.song.id)
            vote_request.send(sock)

    def update_song_display(self):
        self.listbox.Clear()
        for song_request in self.potential_songs.ordered:
            song_obj = song_request.song
            song_name = song_obj.artist_name + " - " + song_obj.title
            vote_tracker = song_request.vote_tracker
            vote_breakdown = "Yes: {0}, No: {1}, Abstain: {2}".format(vote_tracker.number_yes, vote_tracker.number_no, vote_tracker.number_abstain)
            self.listbox.Append(song_name + " | " + vote_breakdown)

    def NewItem(self, event):
        text = wx.GetTextFromUser('Enter a new item', 'Insert dialog')
        if text != '':
            self.listbox.Append(text)

    def OnRename(self, event):
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        renamed = wx.GetTextFromUser('Rename item', 'Rename dialog', text)
        if renamed != '':
            self.listbox.Delete(sel)
            self.listbox.Insert(renamed, sel)


    def OnDelete(self, event):
        sel = self.listbox.GetSelection()
        if sel != -1:
            self.listbox.Delete(sel)

    def OnClear(self, event):
        self.listbox.Clear()



app = wx.App()
ListBox(None, -1, 'ListBox')
app.MainLoop()
