import serial
import constant as Constants
from model.packet import Packet


class RVRClient:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def writePacket(self, packet):
        self.serialPort.write(packet.getEncodedData())

    def readPackets(self):
        output = []
        for i in range(Constants.MAX_PACKETS_TO_READ):
            if self.serialPort.in_waiting > 0:
                raw_data = self.serialPort.read_until(bytearray([Constants.END_BYTE]))
                decoded_data = Packet.decodeData(bytearray(raw_data))
                output.append(decoded_data)
        return output

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
