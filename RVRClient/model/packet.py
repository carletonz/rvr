import RVRClient.constant as Constants


class Packet:
    sequenceCount = Constants.MIN_SEQUENCE_COUNT
    class Builder:
        def __init__(self):
            self._flags = 0
            self._targetId = None
            self._sourceId = None
            self._deviceId = None
            self._commandId = None
            self._sequence = Packet.getSequenceCount()
            self._error = None
            self._data = []

        def flags(self, flags):
            self._flags = flags
            return self

        def tid(self, targetId):
            self._targetId = targetId
            self._flags = Packet.setFlag(self._flags, Constants.HAS_TARGET_ID)
            return self

        def sid(self, sourceId):
            self._sourceId = sourceId
            self._flags = Packet.setFlag(self._flags, Constants.HAS_SOURCE_ID)
            return self

        def did(self, deviceId):
            self._deviceId = deviceId
            return self

        def cid(self, commandId):
            self._commandId = commandId
            return self

        def err(self, error):
            self._error = error
            return self

        def seq(self, sequence):
            self._sequence = sequence

        def data(self, packet_data):
            self._data = packet_data
            return self

        def isResponseFlag(self):
            self._flags = Packet.setFlag(self._flags, Constants.IS_RESPONSE)
            return self

        def requestResponseFlag(self):
            self._flags = Packet.setFlag(self._flags, Constants.REQUEST_RESPONSE)
            return self

        def activityFlag(self):
            self._flags = Packet.setFlag(self._flags, Constants.IS_ACTIVITY)
            return self

        def requestOnlyErrorResponseFlag(self):
            self._flags = Packet.setFlag(self._flags, Constants.RESPONSE_ON_ERROR)
            return self

        def build(self):
            # TODO: do validation checks
            if type(self._data) != list:
                raise TypeError("Data must be a list")
            for d in self._data:
                if type(d) != int:
                    raise TypeError("Data entry must be int")
            if Packet.isFlagSet(self._flags, Constants.RESPONSE_ON_ERROR) and\
                    (self._commandId is None or not Packet.isFlagSet(self._flags, Constants.IS_RESPONSE)):
                raise ValueError("To use the request only error response flag a command id must be given and the is response flag must not be set")
            return Packet(self._flags, self._targetId, self._sourceId, self._deviceId, self._commandId, self._sequence, self._error, self._data)

    @staticmethod
    def getSequenceCount():
        temp = Packet.sequenceCount
        Packet.sequenceCount += 1
        if Packet.sequenceCount == Constants.MAX_SEQUENCE_COUNT:
            Packet.sequenceCount = Constants.MIN_SEQUENCE_COUNT
        return temp

    def __init__(self, flags=0, tid=None, sid=None, did=None, cid=None, seq=0, err=None, data=[]):
        if flags is None:
            raise "flags are required"
        self._body = bytearray()
        self.flags = flags
        self.tid = tid
        self.sid = sid
        self.did = did
        self.cid = cid
        self.seq = seq
        self.err = err
        self.data = data
        self.buildBody()

    def __str__(self):
        s = "-------------Packet Start-------------\n"
        s += "Flags: {0}\n".format(format(self.flags, "08b"))
        s += "Target: {0}\n".format(str(self.tid))
        s += "Source: {0}\n".format(str(self.sid))
        s += "Device: {0}\n".format(Constants.DEVICE_TO_NAME.get(self.did, "Unknown Device (" + str(self.did) + ")"))
        s += "Command: {0}\n".format(str(self.cid) + " ({})".format(hex(self.cid) if self.cid else ""))
        s += "Sequence: {0}\n".format(str(self.seq))
        s += "Error: {0}\n".format(Constants.ERROR_TO_NAME.get(self.err, "Unknown Error (" + str(self.err) + ")"))
        s += "Data: {0}\n".format(str(self.data))
        s += "-------------Packet End-------------"
        return s

    def buildBody(self):
        self.addToBody(self.flags)
        self.addToBody(self.tid)
        self.addToBody(self.sid)
        self.addToBody(self.did)
        self.addToBody(self.cid)
        self.addToBody(self.seq)
        self.addToBody(self.err)
        self.addToBody(self.data)

    def addToBody(self, value):
        if value is not None:
            if type(value) == list:
                self._body += bytearray(value)
            else:
                self._body += bytearray([value])

    def getEncodedData(self):
        return Packet.encodeData(self._body)

    @staticmethod
    def builder():
        return Packet.Builder()

    @staticmethod
    def setFlag(flags, flag):
        return flags | flag

    @staticmethod
    def isFlagSet(flags, flag):
        return bool(flags & flag)

    @staticmethod
    def encodeData(data):
        checksum = sum(data) & 0xff ^ 0xff
        request = data + checksum.to_bytes(1, 'big')
        request = request.replace(Constants.ESC_BYTE.to_bytes(1, 'big'), Constants.ESC_ESC_BYTE.to_bytes(2, 'big'))
        request = request.replace(Constants.START_BYTE.to_bytes(1, 'big'), Constants.ESC_START_BYTE.to_bytes(2, 'big'))
        request = request.replace(Constants.END_BYTE.to_bytes(1, 'big'), Constants.ESC_END_BYTE.to_bytes(2, 'big'))
        return bytearray([0x8d]) + request + bytearray([0xd8])

    @staticmethod
    def decodeData(data):
        if type(data) is not bytearray:
            raise ValueError("data must be a bytearray")
        if data[0] != 0x8d or data[len(data) - 1] != 0xd8:
            raise ValueError(data.hex() + " does not start or end with start or end bytes")
        buf = data[1:len(data) - 1]

        buf = buf.replace(Constants.ESC_ESC_BYTE.to_bytes(2, 'big'), Constants.ESC_BYTE.to_bytes(1, 'big'))
        buf = buf.replace(Constants.ESC_START_BYTE.to_bytes(2, 'big'), Constants.START_BYTE.to_bytes(1, 'big'))
        buf = buf.replace(Constants.ESC_END_BYTE.to_bytes(2, 'big'), Constants.END_BYTE.to_bytes(1, 'big'))

        if sum(buf) & 0xff != 255:
            raise ValueError("could not validate checksum")
        buf = buf[:-1]
        flags = buf[0]
        offset = 0

        packetBuilder = Packet.builder()
        packetBuilder.flags(flags)
        if Packet.isFlagSet(flags, Constants.HAS_TARGET_ID):
            packetBuilder.tid(buf[1+offset])
            offset += 1
        if Packet.isFlagSet(flags, Constants.HAS_SOURCE_ID):
            packetBuilder.sid(buf[1+offset])
            offset += 1
        packetBuilder.did(buf[1+offset])\
            .cid(buf[2+offset])\
            .seq(buf[3+offset])
        if Packet.isFlagSet(flags, Constants.IS_RESPONSE):
            packetBuilder.err(buf[4+offset])
            offset += 1
        packetBuilder.data(list(buf[4+offset:]))
        return packetBuilder.build()

