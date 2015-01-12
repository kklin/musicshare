import sys
import socket, select
import settings
import network
from network import Register, NetworkPacket

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

    print("Connected! Going to try registering")

    register_obj = Register("kklin")
    register_packet_data = register_obj.to_network_packet()
    s.send(register_packet_data)

    while True:
        ready_to_read, ready_to_write, in_error = select.select([s], [], [], 0)

        # TODO: could we just read directly without polling?
        for sock in ready_to_read:
            try:
                data = sock.recv(RECV_BUFFER)
                if data:
                    process(data)
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

def process(data):
    parsed_request = NetworkPacket.parse(data)
    request_type = type(parsed_request)
    if request_type is network.VoteRequest:
        print("Got a vote request from the server for: " + parsed_request.song_id)
    else:
        print("Err not sure what that was..")

if __name__ == "__main__":
    host = socket.gethostname()
    if len(sys.argv) is 2: # if hostname is specified
        host = sys.argv[1]
    sys.exit(main(host))
