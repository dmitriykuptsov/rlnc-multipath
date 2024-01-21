PACKET_TYPE_OFFSET = 0
PACKET_TYPE_LENGTH = 4
PACKET_LENGTH_OFFSET = 4
PACKET_LENGTH_LENGTH = 4

class GenericPacket():
    def __init__(self, buffer = None):
        if buffer == None:
            self.buffer = bytearray([0] * (PACKET_TYPE_LENGTH + PACKET_LENGTH_LENGTH))
        else:
            self.buffer = buffer
    def get_length(self):
        length = (self.buffer[PACKET_LENGTH_OFFSET] << 24)
        length |= (self.buffer[PACKET_LENGTH_OFFSET + 1] << 16)
        length |= (self.buffer[PACKET_LENGTH_OFFSET + 2] << 8)
        length |= (self.buffer[PACKET_LENGTH_OFFSET + 3])
        return length
    def set_length(self, length):
        self.buffer[PACKET_LENGTH_OFFSET] = (length >> 24) & 0xFF
        self.buffer[PACKET_LENGTH_OFFSET + 1] = (length >> 16) & 0xFF
        self.buffer[PACKET_LENGTH_OFFSET + 2] = (length >> 8) & 0xFF
        self.buffer[PACKET_LENGTH_OFFSET + 3] = (length >> 0) & 0xFF
    def get_type(self):
        type = (self.buffer[PACKET_TYPE_OFFSET] << 24)
        type |= (self.buffer[PACKET_TYPE_OFFSET + 1] << 16)
        type |= (self.buffer[PACKET_TYPE_OFFSET + 2] << 8)
        type |= (self.buffer[PACKET_TYPE_OFFSET + 3])
        return type
    def set_type(self, type):
        self.buffer[PACKET_TYPE_OFFSET] = (type >> 24) & 0xFF
        self.buffer[PACKET_TYPE_OFFSET + 1] = (type >> 16) & 0xFF
        self.buffer[PACKET_TYPE_OFFSET + 2] = (type >> 8) & 0xFF
        self.buffer[PACKET_TYPE_OFFSET + 3] = (type >> 0) & 0xFF

    def get_buffer(self):
        return self.buffer

TPUT_PROBE_TYPE = 1
TPUT_INDEX_LENGTH = 4
TPUT_INDEX_OFFSET = 8
TPUT_PAYLOAD_OFFSET = 12
TPUT_PAYLOAD_LENGTH = 1024

class TputProbe(GenericPacket):
    def __init__(self, buffer = None):
        if buffer == None:
            self.buffer = bytearray([0] * (PACKET_TYPE_LENGTH + PACKET_LENGTH_LENGTH + TPUT_INDEX_LENGTH))
        else:
            self.buffer = buffer
    def get_index(self):
        index = (self.buffer[TPUT_INDEX_OFFSET] << 24)
        index |= (self.buffer[TPUT_INDEX_OFFSET + 1] << 16)
        index |= (self.buffer[TPUT_INDEX_OFFSET + 2] << 8)
        index |= (self.buffer[TPUT_INDEX_OFFSET + 3])
        return index
    def set_index(self, index):
        self.buffer[TPUT_INDEX_OFFSET] = (index >> 24) & 0xFF
        self.buffer[TPUT_INDEX_OFFSET + 1] = (index >> 16) & 0xFF
        self.buffer[TPUT_INDEX_OFFSET + 2] = (index >> 8) & 0xFF
        self.buffer[TPUT_INDEX_OFFSET + 3] = (index >> 0) & 0xFF
    def set_payload(self, payload):
        self.buffer[TPUT_PAYLOAD_OFFSET:TPUT_PAYLOAD_OFFSET+TPUT_PAYLOAD_LENGTH] = payload

TPUT_ACK_TYPE = 2
TPUT_PPS_LENGTH = 4
TPUT_PPS_OFFSET = 8
TPUT_TIME_DELTA_OFFSET = 12
TPUT_TIME_DELTA_LENGTH = 4

class TputProbeACK(GenericPacket):
    def __init__(self, buffer = None):
        if buffer == None:
            self.buffer = bytearray([0] * (PACKET_TYPE_LENGTH + PACKET_LENGTH_LENGTH + TPUT_INDEX_LENGTH + TPUT_TIME_DELTA_LENGTH))
        else:
            self.buffer = buffer
    def get_pps(self):
        pps = (self.buffer[TPUT_PPS_OFFSET] << 24)
        pps |= (self.buffer[TPUT_PPS_OFFSET + 1] << 16)
        pps |= (self.buffer[TPUT_PPS_OFFSET + 2] << 8)
        pps |= (self.buffer[TPUT_PPS_OFFSET + 3])
        return pps
    def set_pps(self, pps):
        self.buffer[TPUT_PPS_OFFSET] = (pps >> 24) & 0xFF
        self.buffer[TPUT_PPS_OFFSET + 1] = (pps >> 16) & 0xFF
        self.buffer[TPUT_PPS_OFFSET + 2] = (pps >> 8) & 0xFF
        self.buffer[TPUT_PPS_OFFSET + 3] = (pps >> 0) & 0xFF
    def get_time_delta(self):
        delta = (self.buffer[TPUT_TIME_DELTA_OFFSET] << 24)
        delta |= (self.buffer[TPUT_TIME_DELTA_OFFSET + 1] << 16)
        delta |= (self.buffer[TPUT_TIME_DELTA_OFFSET + 2] << 8)
        delta |= (self.buffer[TPUT_TIME_DELTA_OFFSET + 3])
        return delta
    def set_time_delta(self, delta):
        self.buffer[TPUT_TIME_DELTA_OFFSET] = (delta >> 24) & 0xFF
        self.buffer[TPUT_TIME_DELTA_OFFSET + 1] = (delta >> 16) & 0xFF
        self.buffer[TPUT_TIME_DELTA_OFFSET + 2] = (delta >> 8) & 0xFF
        self.buffer[TPUT_TIME_DELTA_OFFSET + 3] = (delta >> 0) & 0xFF

DATA_PACKET_TYPE = 3
DATA_PACKET_GENERATION_LENGTH = 4
DATA_PACKET_GENERATION_OFFSET = 0
DATA_PACKET_GENERATION_SIZE_OFFSET = 4
DATA_PACKET_GENERATION_SIZE_LENGTH = 4
DATA_PACKET_SYMBOLS_NUM_LENGTH = 4
DATA_PACKET_COEF_OFFSET = 8

class DataPacket(GenericPacket):
    def __init__(self, buffer = None):
        if buffer == None:
            self.buffer = bytearray([0] * (PACKET_TYPE_LENGTH + PACKET_LENGTH_LENGTH + TPUT_INDEX_LENGTH))
        else:
            self.buffer = buffer
    def get_generation(self):
        gen = (self.buffer[DATA_PACKET_GENERATION_OFFSET] << 24)
        gen |= (self.buffer[DATA_PACKET_GENERATION_OFFSET + 1] << 16)
        gen |= (self.buffer[DATA_PACKET_GENERATION_OFFSET + 2] << 8)
        gen |= (self.buffer[DATA_PACKET_GENERATION_OFFSET + 3])
        return gen
    def set_generation(self, gen):
        self.buffer[DATA_PACKET_GENERATION_OFFSET] = (gen >> 24) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_OFFSET + 1] = (gen >> 16) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_OFFSET + 2] = (gen >> 8) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_OFFSET + 3] = (gen >> 0) & 0xFF
    def get_generation_size(self):
        size = (self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET] << 24)
        size |= (self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 1] << 16)
        size |= (self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 2] << 8)
        size |= (self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 3])
        return size
    def set_generation_size(self, size):
        self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET] = (size >> 24) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 1] = (size >> 16) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 2] = (size >> 8) & 0xFF
        self.buffer[DATA_PACKET_GENERATION_SIZE_OFFSET + 3] = (size >> 0) & 0xFF
    def get_coefs(self):
        size = self.get_generation_size()
        coefs = self.buffer[DATA_PACKET_COEF_OFFSET:DATA_PACKET_COEF_OFFSET + size]
        return coefs
    def set_coefs(self, coefs):
        size = len(coefs)
        self.set_generation_size(size)
        self.buffer[DATA_PACKET_COEF_OFFSET:DATA_PACKET_COEF_OFFSET + size] = coefs
    def get_symbols(self):
        size = self.get_generation_size()
        symbols = self.buffer[DATA_PACKET_COEF_OFFSET + size:]
        return symbols
    def set_symbols(self, symbols):
        size = self.get_generation_size()
        self.buffer[DATA_PACKET_COEF_OFFSET + size:DATA_PACKET_COEF_OFFSET + size + len(symbols)] = bytearray([0]*len(symbols))
        self.buffer[DATA_PACKET_COEF_OFFSET + size:DATA_PACKET_COEF_OFFSET + size + len(symbols)] = symbols