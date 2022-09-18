import serial
import constant as Constants
from rvrClient import RVRClient
from Sensor.SensorService import SensorService
import time
import psutil

port = None
lastResult = None


def getUartPort():
    global port
    port = serial.Serial(Constants.UART_PORT, Constants.BAUD_RATE)
    port.flushInput()
    return port


rvr = RVRClient(getUartPort())
# sensors = SensorService(rvr)
# rvr.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.ST))
# sensors.start()

leftSpeed = 50
rightSpeed = 50

try:
    while True:
        # rvr.writePacket(RVRClient.getWakeCommandPacket())

        if leftSpeed == 75:
            leftSpeed = 0
            rightSpeed = 0
            rvr.writePacket(RVRClient.getSetRawMotorsPacket(Constants.MODE_OFF, leftSpeed,
                                                            Constants.MODE_OFF, rightSpeed,
                                                            Constants.ST))
            leftSpeed = 50
            rightSpeed = 50
        else:
            rvr.writePacket(RVRClient.getSetRawMotorsPacket(Constants.MODE_FORWARD, leftSpeed,
                                                            Constants.MODE_FORWARD, rightSpeed,
                                                            Constants.ST))
        leftSpeed += 1
        rightSpeed += 1
        packets = rvr.readPackets(10)
        for p in packets:
            print(p)
        time.sleep(1)
finally:
    print("error happened, in finally section")
    rvr.writePacket(RVRClient.getSetRawMotorsPacket(Constants.MODE_OFF, 0,
                                                    Constants.MODE_OFF, 0,
                                                    Constants.ST))

