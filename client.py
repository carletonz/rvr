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

while True:
    rvr.writePacket(RVRClient.getWakeCommandPacket())
    packets = rvr.readPackets(1)
    if len(packets) > 0 and packets[0].did == Constants.DEVICE_SENSOR and packets[0].seq != 0:
        print(sensors.processPacket(packets[0]))
