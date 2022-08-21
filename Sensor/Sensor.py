import constant as Constants

class Sensor:
    ActiveSensors = {}

    def __init__(self, sensorId, processor, size):
        if (sensorId, processor) in Sensor.ActiveSensors:
            raise Exception("Sensor ID: " + sensorId + " and Processor: " + processor + " already exist")
        self.sensorId = sensorId
        self.processor = processor
        self.name = Constants.SENSOR_TO_NAME[sensorId]
        self.attributes = Constants.SENSOR_ATTRIBUTES[sensorId]
        self.streamToken = None
        self.dataSize = size
        self.attributeSize = Constants.SIZE_TO_MAX_VALUE[size] * self.attributes.length
        Sensor.ActiveSensors[(sensorId, processor)] = self

    def setStreamId(self, streamToken):
        self.streamToken = streamToken

    def decodeAttributes(self, data):
        decodedData = [0 for _ in self.attributes]
        for index, attribute in enumerate(self.attributes):
            value = int.to_bytes(data[self._getSlice(index)], "big")
            decodedData[index] = self._normalizeValue(attribute.minRange, attribute.maxRange, value)
        return decodedData

    def _normalizeValue(self, minRange, maxRange, value):
        numBytes = Constants.SIZE_TO_NUM_BYTES[self.dataSize]
        byteMax = int.to_bytes(bytearray([0xff for _ in range(numBytes)]), "big")
        return (value / byteMax) * (maxRange - minRange) + minRange

    def _getSlice(self, index):
        num_bytes = Constants.SIZE_TO_NUM_BYTES[self.dataSize]
        return slice(num_bytes*index, num_bytes*(index+1))

