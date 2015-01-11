import sys
import socket, select
import settings
from network import Header, Register

RECV_BUFFER = 4096
host = socket.gethostname()
port = settings.port
socket_list = []
socket_to_user = {}

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

def process(sock, data):
    header = data[0]
    if header is Header.VOTE:
        pass
    elif header is Header.CONTROL:
        pass
    elif header is Header.REQUEST_INFO:
        pass
    elif header is Header.ADD_SONG:
        pass
    elif header is Header.REGISTER:
        socket_to_user[sock] = Register.from_network_packet(data)
        print(str(sock) + " is now associated with id " + str(socket_to_user[sock]))

if __name__ == "__main__":
    sys.exit(main())
