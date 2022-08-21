import serial
import constant as Constants
from model.packet import Packet


class RVRClient:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def writePacket(self, packet):
        self.serialPort.write(packet.getEncodedData())

    def readPackets(self, maxPackets=Constants.MAX_PACKETS_TO_READ):
        output = []
        for i in range(maxPackets):
            if self.serialPort.in_waiting > 0:
                raw_data = self.serialPort.read_until(bytearray([Constants.END_BYTE]))
                start_index = raw_data.index(Constants.START_BYTE)
                try:
                    decoded_data = Packet.decodeData(bytearray(raw_data[start_index:]))
                    output.append(decoded_data)
                except Exception as e:
                    print("Error while parsing raw data: " + str(e))
                    print(raw_data)
        return output

    @staticmethod
    def getWakeCommandPacket():
        return Packet.builder() \
            .tid(Constants.NORDIC) \
            .did(Constants.DEVICE_POWER) \
            .cid(0x0d) \
            .requestResponseFlag() \
            .activityFlag() \
            .build()

    @staticmethod
    def getConfigureSensorStreamPacket(processor, token, sensors, dataSizes):
        sensorConfigs = []
        for i in range(min(len(sensors), Constants.MAX_SENSORS_PER_STREAM)):
            sensorConfigs += list(sensors[i]) + [dataSizes[i]]

        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_SENSOR) \
            .cid(0x39) \
            .requestResponseFlag() \
            .activityFlag() \
            .data([token] + sensorConfigs) \
            .build()

    @staticmethod
    def getStartSensorStreamingPacket(processor):
        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_SENSOR) \
            .cid(0x3a) \
            .requestResponseFlag() \
            .activityFlag() \
            .data(Constants.SENSOR_PUBLISH_RATE) \
            .build()

    @staticmethod
    def getStopSensorStreamingPacket(processor):
        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_SENSOR) \
            .cid(0x3b) \
            .requestResponseFlag() \
            .activityFlag() \
            .build()


"""
streaming service configuration for RVR:
| Id     | Processor          | Token | Service            | Attributes                 |
| ------ | ------------- -----| ----- | ------------------ | -------------------------- |
| 0x0003 | Nordic (1)         | 1     | ColorDetection     | R, G, B, Index, Confidence |
| 0x000A | Nordic (1)         | 2     | AmbientLight       | Light                      |
-----------------------------------------------------------------------------------------
| 0x0000 | ST (2)             | 1     | Quaternion         | W, X, Y, Z                 |
| 0x0001 | ST (2)             | 1     | IMU                | Pitch, Roll, Yaw           |
| 0x0002 | ST (2)             | 1     | Accelerometer      | X, Y, Z                    |
| 0x0004 | ST (2)             | 1     | Gyroscope          | X, Y, Z                    |
| 0x0006 | ST (2)             | 2     | Locator            | X, Y                       |
| 0x0007 | ST (2)             | 2     | Velocity           | X, Y                       |
| 0x0008 | ST (2)             | 2     | Speed              | Speed                      |
| 0x000B | ST (2)             | 2     | Encoders           | Left, Right                |
-----------------------------------------------------------------------------------------
| 0x0009 | Nordic (1), ST (2) | 3     | CoreTime           | TimeUpper, TimeLower       |
-----------------------------------------------------------------------------------------
"""
# [0x8d, 0x18, 0x02, 0x18, 0x39, 0x02, 0x01, 0x00, 0x02, 0x02, 0xab, 0x05, 0xd8]
# - data = 4 unsigned bytes: token, [sensor id (take up 2 bytes), data size] x 5
# - in ex above token = 0x01, sensor id = 0x0002 = accelerometer, data size = 0x02 = 32 bit
# - token is any number and is used to identify which data stream the response packet is for
# [0x8d, 0x18, 0x01, 0x18, 0x3a, 0x03, 0x07, 0xd0, 0xba, 0xd8]
# - data = 2 unsigned bytes representing rate data should be published at
# - in ex above rate is 2000 (2 seconds)


'''
Design

Inputs: RVR serial port, camera, ros topics/services, etc

data processors: distributors (breaks down data from different inputs and directs them to the next data processor),
sensor service, sensor stream, sensors, etc

outputs: RVR serial port, ros topics/services, etc


321676fd0842c0b407119310a3
320e65fa35ff321666fd08448377138f6d08f9


'''