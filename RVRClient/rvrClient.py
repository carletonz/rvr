import serial
import RVRClient.constant as Constants
from RVRClient.model.packet import Packet
from threading import Lock

class RVRClient:
    def __init__(self, serialPort, debug = False):
        self.debugLog = debug
        self.serialPort = serialPort
        self.readLock = Lock()
        self.writeLock = Lock()

    def __del__(self):
        self.closePort()

    def closePort(self):
        if self.debugLog:
            print("closing port")
        if self.serialPort.is_open:
            self.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.NORDIC))
            self.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.ST))
            self.serialPort.close()

    def writePacket(self, packet):
        with self.writeLock:
            if self.debugLog:
                print('Writing bytes: [{}]'.format(', '.join('0x{:02x}'.format(x) for x in packet.getEncodedData())))
            self.serialPort.write(packet.getEncodedData())

    def readPackets(self, maxPackets=Constants.MAX_PACKETS_TO_READ):
        output = []
        for i in range(maxPackets):
            if self.serialPort.in_waiting > 0:
                with self.readLock:
                    raw_data = self.serialPort.read_until(bytearray([Constants.END_BYTE]))
                try:
                    if self.debugLog:
                        print('Read bytes: [{}]'.format(', '.join('0x{:02x}'.format(x) for x in raw_data)))
                    start_index = raw_data.index(Constants.START_BYTE)
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
            .activityFlag() \
            .data([token] + sensorConfigs) \
            .build()

    @staticmethod
    def getStartSensorStreamingPacket(processor):
        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_SENSOR) \
            .cid(0x3a) \
            .activityFlag() \
            .data(Constants.SENSOR_PUBLISH_RATE) \
            .build()

    @staticmethod
    def getSetRawMotorsPacket(leftMode, leftDutyCycle, rightMode, rightDutyCycle, processor):
        #TODO: add data validation to make sure that data is correct size
        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_DRIVE) \
            .cid(0x01) \
            .requestResponseFlag() \
            .activityFlag() \
            .data([leftMode, leftDutyCycle, rightMode, rightDutyCycle]) \
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

    @staticmethod
    def getClearSensorStreamingPacket(processor):
        return Packet.builder() \
            .tid(processor) \
            .did(Constants.DEVICE_SENSOR) \
            .cid(0x3c) \
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