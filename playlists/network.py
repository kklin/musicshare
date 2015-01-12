class Header(object):
    HEADER_LENGTH = 1

    VOTE_REQUEST = '1'
    CONTROL = '2'
    REQUEST_INFO = '3'
    INFO_RESPONSE = '4'
    ADD_SONG = '5'
    REGISTER = '6'
    VOTE_RESPONSE = '7'

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
        sock.send(self.to_network_packet() + self.DELIMITER)

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
            pass
        elif RequestInfo.is_packet(data):
            pass
        elif AddSong.is_packet(data):
            pass
        elif Register.is_packet(data):
            return Register.from_network_packet(data)

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

    def __init__(self, id):
        self.id = id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.id)

    @staticmethod
    def from_network_packet(data):
        return Register(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.CONTROL

    def __str__(self):
        return self.id

class RequestInfo(NetworkPacket):

    def __init__(self, id):
        self.id = id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.id)

    @staticmethod
    def from_network_packet(data):
        return Register(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.REQUEST_INFO

    def __str__(self):
        return self.id

class AddSong(NetworkPacket):

    def __init__(self, id):
        self.id = id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.id)

    @staticmethod
    def from_network_packet(data):
        return Register(data[1:])

    @staticmethod
    def is_packet(data):
        return data[:Header.HEADER_LENGTH] is Header.ADD_SONG

    def __str__(self):
        return self.id
