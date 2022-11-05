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
            self.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.ST))
            self.serialPort.close()

    def writePacket(self, packet):
        with self.writeLock:
            if self.debugLog:
                print("Writing packet:", packet.encodeData())
            self.serialPort.write(packet.getEncodedData())

    def readPackets(self, maxPackets=Constants.MAX_PACKETS_TO_READ):
        output = []
        for i in range(maxPackets):
            if self.serialPort.in_waiting > 0:
                with self.readLock:
                    raw_data = self.serialPort.read_until(bytearray([Constants.END_BYTE]))
                try:
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

Sphero's sdk
---------------
Sending message: COMMAND DID: 0x13 CID: 0x0d Sequence: 0x01 Payload:  Error: None
Writing bytes: [0x8d, 0x18, 0x01, 0x13, 0x0d, 0x01, 0xc5, 0xd8]
Adding IMU service handler
Attempted to disable all services for Slot (token:1, processor:1), but none are enabled.
Attempted to disable all services for Slot (token:3, processor:1), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:1), but none are enabled.
Slot has no enabled services
Slot has no enabled services
Slot has no enabled services
Slot has no enabled services
No services enabled during configuration.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:3, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Sending message: COMMAND DID: 0x18 CID: 0x39 Sequence: 0x02 Payload: 0x01,0x00,0x01,0x02 Error: None
Slot has no enabled services
Writing bytes: [0x8d, 0x18, 0x02, 0x18, 0x39, 0x02, 0x01, 0x00, 0x01, 0x02, 0x8e, 0xd8]
Slot has no enabled services
Slot has no enabled services
Sending message: COMMAND DID: 0x18 CID: 0x3a Sequence: 0x03 Payload: 0x27,0x10 Error: None
Sending message: COMMAND DID: 0x18 CID: 0x3a Sequence: 0x04 Payload: 0x27,0x10 Error: None
Writing bytes: [0x8d, 0x18, 0x01, 0x18, 0x3a, 0x03, 0x27, 0x10, 0x5a, 0xd8]
Writing bytes: [0x8d, 0x18, 0x02, 0x18, 0x3a, 0x04, 0x27, 0x10, 0x58, 0xd8]
Read 1 bytes: [0x8d]
Appending bytes: [0x8d]
Packet missing SOP/EOP!
Read 14 bytes: [0x28, 0x02, 0x18, 0x3d, 0xff, 0x01, 0x86, 0x55, 0xd3, 0x00, 0x81, 0x4c, 0x13, 0x00]
Appending bytes: [0x8d, 0x28, 0x02, 0x18, 0x3d, 0xff, 0x01, 0x86, 0x55, 0xd3, 0x00, 0x81, 0x4c, 0x13, 0x00]
Packet missing SOP/EOP!
Read 6 bytes: [0x87, 0x94, 0xeb, 0x00, 0xec, 0xd8]
Appending bytes: [0x8d, 0x28, 0x02, 0x18, 0x3d, 0xff, 0x01, 0x86, 0x55, 0xd3, 0x00, 0x81, 0x4c, 0x13, 0x00, 0x87, 0x94, 0xeb, 0x00, 0xec, 0xd8]
Parsing packet complete: COMMAND DID: 0x18 CID: 0x3d Sequence: 0xff Payload: 0x01,0x86,0x55,0xd3,0x00,0x81,0x4c,0x13,0x00,0x87,0x94,0xeb,0x00 Error: None
Looking for entries with key (CID: 0x18, DID: 0x3d, Source: 2)
Entry found, dispatching!
Unpacking output from message
Invoking callback with response data: {'token': 1, 'sensor_data': [134, 85, 211, 0, 129, 76, 19, 0, 135, 148, 235, 0]}
Token: 1, Processor: 2 Status: 0, Sensor Data: [0x86, 0x55, 0xd3, 0x00, 0x81, 0x4c, 0x13, 0x00, 0x87, 0x94, 0xeb, 0x00]
Sensor: IMU Attribute: Pitch Bytes: [0x86, 0x55, 0xd3, 0x00], Int Value: 2253771520, Normalized Value: 8.908946558113428
Sensor: IMU Attribute: Roll Bytes: [0x81, 0x4c, 0x13, 0x00], Int Value: 2169246464, Normalized Value: 0.9120691034272426
Sensor: IMU Attribute: Yaw Bytes: [0x87, 0x94, 0xeb, 0x00], Int Value: 2274683648, Normalized Value: 10.661780878589894
Sensor data response:  {'IMU': {'is_valid': True, 'Pitch': 8.908946558113428, 'Roll': 0.9120691034272426, 'Yaw': 10.661780878589894}}
Consuming bytes in packet.
from sphero_sdk.common.log_level import LogLevel^C
Program terminated with keyboard interrupt.
Disabling all streaming services.
Sending message: COMMAND DID: 0x18 CID: 0x3c Sequence: 0x05 Payload:  Error: None
Sending message: COMMAND DID: 0x18 CID: 0x3c Sequence: 0x06 Payload:  Error: None
Writing bytes: [0x8d, 0x18, 0x01, 0x18, 0x3c, 0x05, 0xab, 0x05, 0xd8]
Attempted to disable all services for Slot (token:1, processor:1), but none are enabled.
Attempted to disable all services for Slot (token:3, processor:1), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:1), but none are enabled.
Writing bytes: [0x8d, 0x18, 0x02, 0x18, 0x3c, 0x06, 0x8b, 0xd8]
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:1, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:3, processor:2), but none are enabled.
Attempted to disable all services for Slot (token:2, processor:2), but none are enabled.
Read/Write thread joining.
Closing serial port.



My SDK
------------------------


'''