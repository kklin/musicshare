# The way network communication works is hacky, to say the least. Basically, a
# packet is defined as what's inbetween NetworkPacket.DELIMITER
# Each packet starts with a header of a defined length that signifies the type
# of packet it is. This determines how the data payload following the header is
# parsed
# To add a new network packet, first add a new entry to the Header class. Then,
# create a new class to represent the packet. Follow the structure of one of the
# other classes, such as Register. Finally, add the appropriate parsing logic to
# NetworkPacket.parse()

class Header(object):
    HEADER_LENGTH = 1

    VOTE_REQUEST = '1'
    CONTROL = '2'
    REQUEST_INFO = '3'
    INFO_RESPONSE = '4'
    ADD_SONG = '5'
    REGISTER = '6'
    VOTE_RESPONSE = '7'
    NOTIFY_EVENT = '8'

    @staticmethod
    def prepend_header(header, data):
        return header + data

#### MODELS ####

class NetworkPacket(object):

    DELIMITER = '                     '

    def __init__(self):
        pass

    def to_network_packet(self):
        raise NotImplementedError()

    # send this object as a network packet over the given socket
    def send(self, sock):
        sock.send(self.to_network_packet() + NetworkPacket.DELIMITER)

    @staticmethod
    def from_network_packet(data):
        raise NotImplementedError()

    @staticmethod
    def is_packet(data):
        raise NotImplementedError()

    @staticmethod
    def parse(data):
        if VoteResponse.is_packet(data):
            return VoteResponse.from_network_packet(data)
        elif VoteRequest.is_packet(data):
            return VoteRequest.from_network_packet(data)
        elif Control.is_packet(data):
            return Contro.from_network_packet(data)
        elif RequestInfo.is_packet(data):
            return RequestInfo.from_network_packet(data)
        elif AddSong.is_packet(data):
            return AddSong.from_network_packet(data)
        elif Register.is_packet(data):
            return Register.from_network_packet(data)

class NotifyEvent(NetworkPacket):
    '''For notifying the client of some kind of event, such as when a new client
    joins or the playlist ordering changes'''

    # TODO: consider enum
    CLIENT_JOINED = '0'
    CLIENT_DISCONNECTED = '1'
    PLAYLIST_REORDERED = '2'

    def __init__(self, event_type):
        self.event_type = event_type

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.event_type)

    @staticmethod
    def from_network_packet(data):
        return NotifyEvent(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.NOTIFY_EVENT

    def __str__(self):
        return self.event_type

class Register(NetworkPacket):

    def __init__(self, id):
        self.id = id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.id)

    @staticmethod
    def from_network_packet(data):
        return Register(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.REGISTER

    def __str__(self):
        return self.id

class VoteResponse(NetworkPacket):

    def __init__(self, song_id, verdict):
        self.song_id = song_id
        self.verdict = verdict

    def to_network_packet(self):
        data = self.verdict + self.song_id
        return Header.prepend_header(Header.VOTE_RESPONSE, data)

    @staticmethod
    def from_network_packet(data):
        return VoteResponse(data[2:], data[1])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.VOTE_RESPONSE

    def __str__(self):
        return self.song_id + " : " + self.verdict

class VoteRequest(NetworkPacket):

    def __init__(self, song_id):
        self.song_id = song_id

    def to_network_packet(self):
        return Header.prepend_header(Header.VOTE_REQUEST, self.song_id)

    @staticmethod
    def from_network_packet(data):
        return VoteRequest(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.VOTE_REQUEST

    def __str__(self):
        return self.id

class Control(NetworkPacket):
    # TODO: consider enum
    PAUSE = 0
    PLAY = 1
    SKIP = 2

    def __init__(self, control):
        self.control = control

    def to_network_packet(self):
        return Header.prepend_header(Header.CONTROL, self.control)

    @staticmethod
    def from_network_packet(data):
        return Control(int(data[1:]))

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.CONTROL

    def __str__(self):
        return self.control

class AddSong(NetworkPacket):

    def __init__(self, song_id):
        self.song_id = song_id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.song_id)

    @staticmethod
    def from_network_packet(data):
        return AddSong(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.ADD_SONG

    def __str__(self):
        return self.song_id

### FOR OBTAINING INFORMATION ABOUT STATE ###
class RequestInfo(NetworkPacket):
    # TODO: consider enum
    CLIENTS = 0
    SONGS = 1

    def __init__(self, request_type):
        self.request_type = request_type

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.request_type)

    @staticmethod
    def from_network_packet(data):
        return RequestInfo(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.REQUEST_INFO

    def __str__(self):
        return self.request_type

class InfoResponse(NetworkPacket):
    pass

class GetClientsResponse(InfoResponse):
    pass

class GetSongsResponse(InfoResponse):
    pass

