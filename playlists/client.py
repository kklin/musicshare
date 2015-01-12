import sys
import socket, select
import network, secret, settings
from network import Register, NetworkPacket, VoteResponse

from pyechonest import song, config
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

RECV_BUFFER = 4096

def main(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to server
    try:
        s.connect((host, settings.port))
    except:
        print("Unable to connect")
        sys.exit()

    username = raw_input("Hi! Pick a username: ")
    register_obj = Register(username)
    register_packet_data = register_obj.to_network_packet()
    s.send(register_packet_data)

    while True:
        ready_to_read, ready_to_write, in_error = select.select([s], [], [], 0)

        # TODO: could we just read directly without polling?
        for sock in ready_to_read:
            try:
                data = sock.recv(RECV_BUFFER)
                if data:
                    process(sock, data)
                else:
                    # socket is broken
                    print("Lost connection to server")
                    # TODO: instead we should break out of the inner for loop
                    s.close()
                    sys.exit(1)
            except Exception as e:
                print(e)
                continue

    s.close()

def process(sock, data):
    packets = data.split(NetworkPacket.DELIMITER)
    try:
        packets.remove('') # not sure why there's that blank string, but we gotta get rid of it
    except:
        pass
    for packet in packets:
        parsed_request = NetworkPacket.parse(packet)
        request_type = type(parsed_request)
        if request_type is network.VoteRequest:
            song_obj = song.Song(parsed_request.song_id)
            song_name = song_obj.artist_name + " - " + song_obj.title
            print("Got a vote request from the server for: " + song_name)
            verdict = raw_input("Do you like it? (Y/N/A) ")
            response = VoteResponse(parsed_request.song_id, verdict)
            response.send(sock)
        else:
            print("Err not sure what that was..")

if __name__ == "__main__":
    host = socket.gethostname()
    if len(sys.argv) is 2: # if hostname is specified
        host = sys.argv[1]
    sys.exit(main(host))
