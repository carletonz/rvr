import RVRClient.constant as Constants

# handles multiple sensors in a stream
class SensorStream:
    def __init__(self, token, processor):
        self.sensors = []
        self.streamToken = token
        self.processor = processor

    def addSensor(self, sensor):
        sensor.setStreamId(self.streamToken)
        self.sensors.append(sensor)

    def getSensorIds(self):
        return [sensor.sensorId for sensor in self.sensors]

    def getDataSizes(self):
        return [sensor.dataSize for sensor in self.sensors]

    def decodeData(self, data):
        decodedData = []
        startIndex = 0
        for index, sensor in enumerate(self.sensors):
            decodedData.append(sensor.decodeAttributes(data[startIndex:startIndex+sensor.attributeSize]))
            startIndex += sensor.attributeSize
        return decodedData
