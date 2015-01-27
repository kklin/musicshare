import sys, threading
import socket, select
import network, secret, settings
from network import Register, NetworkPacket, VoteResponse, AddSong

from pyechonest import song, config
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

RECV_BUFFER = 4096
pending_votes = []

class Client:
    QUIT = 'quit'

    def __init__(self, host):
        self.main(host)

    def main(self, host):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)

        # connect to server
        try:
            self.socket.connect((host, settings.port))
        except:
            print("Unable to connect")
            sys.exit()

        self.register_user()


        # TODO: can't Ctrl-C to kill because of threads
        # start the main threads
        network_thread_obj = threading.Thread(target=self.network_thread)
        network_thread_obj.daemon = True
        network_thread_obj.start()

        console_thread_obj = threading.Thread(target=self.console_thread)
        console_thread_obj.daemon = True
        console_thread_obj.start()
        
        # stay alive while console_thread is still going
        console_thread_obj.join()


    def register_user(self):
        self.username = raw_input("Hi! Pick a username: ")
        register_obj = Register(self.username)
        register_packet_data = register_obj.to_network_packet()
        self.socket.send(register_packet_data)

    def network_thread(self):
        self.pending_votes = [] # init vote queue
        while True:
            # TODO: there's only one socket we care about
            ready_to_read, ready_to_write, in_error = select.select([self.socket], [], [], 0)

            # TODO: could we just read directly without polling?
            for sock in ready_to_read:
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        self.process(data)
                    else:
                        # socket is broken
                        print("Lost connection to server")
                        # TODO: instead we should break out of the inner for loop
                        self.socket.close()
                except Exception as e:
                    print(e)
                    continue
        # TODO: how to make sure we're cleanly closing socket when we exit?

    def console_thread(self):
        commands = ['vote', 'add_song', Client.QUIT]
        print("Available commands: {0}".format(commands))
        while True:
            command = raw_input(">>> ")
            if command.lower() == 'vote':
                self.vote_on_pending()
            elif command.lower() == 'add_song':
                self.add_song()
            elif command.lower() == Client.QUIT:
                sys.exit()

    def process(self, data):
        packets = data.split(NetworkPacket.DELIMITER)
        try:
            packets.remove('') # not sure why there's that blank string, but we gotta get rid of it
        except:
            pass
        for packet in packets:
            parsed_request = NetworkPacket.parse(packet)
            request_type = type(parsed_request)
            if request_type is network.VoteRequest:
                self.pending_votes.append(parsed_request)
            else:
                print("Err not sure what that was..")

    def vote_on_pending(self):
        if self.pending_votes:
            # TODO: need to iterate over copy because we're changing length
            # within
            for vote_request in list(self.pending_votes):
                # TODO: instantiating an object for every vote is using up too many
                # API calls
                song_obj = song.Song(vote_request.song_id)
                song_name = song_obj.artist_name + " - " + song_obj.title
                verdict = raw_input(song_name.encode('utf-8') + " (Y/N/A): ")
                # TODO: loop until we get valid response
                if verdict == Client.QUIT:
                    return
                response = VoteResponse(vote_request.song_id, verdict)
                response.send(self.socket)
                self.pending_votes.remove(vote_request)
        else:
            print("No songs to vote on")


    def add_song(self):
        # TODO: loop until we get valid response
        search_query = raw_input("Enter search query: ")
        # TODO: only search in spotify bucket
        results = song.search(combined=search_query)
        for i, result in enumerate(results):
            # TODO: this is in a couple places, we could throw it in a method
            result_string = result.artist_name + " - " + result.title
            print("{0}. {1}".format(i, result_string))
        result_num = raw_input("Enter desired result number: ")
        # TODO: allow user to reject all choices, and don't add anything
        desired_song = results[int(result_num)] # TODO: sanitize result_num
        addSongPacket = AddSong(desired_song.id)
        addSongPacket.send(self.socket)

if __name__ == "__main__":
    host = socket.gethostname()
    if len(sys.argv) is 2: # if hostname is specified
        host = sys.argv[1]
    client = Client(host)
