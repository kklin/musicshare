import sys
import socket
import settings
from network import Register

def main():
    host = socket.gethostname()
    port = settings.port
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to server
    try:
        s.connect((host, port))
    except:
        print("Unable to connect")
        sys.exit()

    print("Connected! Going to try registering")

    register_obj = Register("kklin")
    register_packet_data = register_obj.to_network_packet()
    s.send(register_packet_data)

    s.close()

if __name__ == "__main__":
    sys.exit(main())
