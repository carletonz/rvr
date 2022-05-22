import serial
import constant as Constants
from model.packet import Packet


def getUartPort():
    return serial.Serial(Constants.UART_PORT, Constants.BAUD_RATE)


def read(uartPort):
    buf = uartPort.read_until(Constants.END_BYTE)
    return Packet.decodeData(buf)


def write(uartPort, packet):
    uartPort.write(packet.encodeData())


def wakeCommand():
    return Packet.builder()\
        .tid(0x01)\
        .did(Constants.DEVICE_POWER)\
        .cid(0x0d)\
        .requestResponseFlag()\
        .activityFlag()\
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
