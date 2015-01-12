import sys
import socket, select
import settings, network, models
from network import NetworkPacket, VoteRequest

# TODO: are global variables like this the right choice?
RECV_BUFFER = 4096
host = socket.gethostname()
port = settings.port
socket_list = []
socket_to_user = {}

potential_songs = models.SongList.from_top_songs()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(settings.max_clients)

    # add server socket object to the list of readable connections
    socket_list.append(server_socket)

    print("Server started on port " + str(port))

    while True:
        
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)

        for sock in ready_to_read:
            # a new connection request
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                socket_list.append(sockfd)
                print("Client (%s, %s) connected" % addr)
            # a message from a client, not a new connection
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        process(sock, data)
                    else:
                        # socket is broken
                        if sock in socket_list:
                            print(str(socket_to_user[sock]) + " disconnected ")
                            socket_list.remove(sock)
                            socket_to_user.pop(sock, None)
                except Exception as e:
                    print(e)
                    continue

    server_socket.close()

# TODO: could we accidentally have a packet split between buffers?
def process(sock, data):
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

            success = song_list.set_vote(parsed_request.song_id, verdict)
            if success:
                print("Successfully saved vote")
            else:
                print("Hmm.. couldn't save the vote. Maybe the id isn't in the list")
        elif request_type is network.Control:
            pass
        elif request_type is network.RequestInfo:
            pass
        elif request_type is network.AddSong:
            pass
        elif request_type is network.Register:
            socket_to_user[sock] = parsed_request.id
            print(str(sock) + " is now associated with id " + str(socket_to_user[sock]))
            print("Requesting votes on the playlist now")
            request_votes(sock, potential_songs)

def request_votes(sock, potential_songs):
    for potential_song in potential_songs.song_list:
        print("Requesting vote for " + potential_song.song.id)
        vote_request = VoteRequest(potential_song.song.id)
        vote_request.send(sock)

if __name__ == "__main__":
    sys.exit(main())
