class Header(object):
    HEADER_LENGTH = 1

    VOTE = '1'
    CONTROL = '2'
    REQUEST_INFO = '3'
    INFO_RESPONSE = '4'
    ADD_SONG = '5'
    REGISTER = '6'

    @staticmethod
    def prepend_header(header, data):
        return header + data

#### MODELS ####
class Register(object):

    def __init__(self, id):
        self.id = id

    def to_network_packet(self):
        return Header.prepend_header(Header.REGISTER, self.id)

    @staticmethod
    def from_network_packet(data):
        return Register(data[1:])

    def __str__(self):
        return self.id
