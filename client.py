import serial
import constant as Constants
from rvrClient import RVRClient
from Sensor.SensorService import SensorService

port = None
lastResult = None


def getUartPort():
    global port
    port = serial.Serial(Constants.UART_PORT, Constants.BAUD_RATE)
    port.flushInput()
    return port


rvr = RVRClient(getUartPort())
sensors = SensorService(rvr)
rvr.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.ST))
sensors.start()

leftSpeed = 0
rightSpeed = 0


while True:
    rvr.writePacket(RVRClient.getWakeCommandPacket())

    if leftSpeed == 100:
        leftSpeed = 0
        rightSpeed = 0
        rvr.writePacket(RVRClient.getSetRawMotorsPacket(Constants.MODE_OFF, leftSpeed,
                                                        Constants.MODE_OFF, rightSpeed,
                                                        Constants.ST))
    else:
        rvr.writePacket(RVRClient.getSetRawMotorsPacket(Constants.MODE_FORWARD, leftSpeed,
                                                        Constants.MODE_FORWARD, rightSpeed,
                                                        Constants.ST))
    leftSpeed += 1
    rightSpeed += 1
    rvr.readPackets(10)
