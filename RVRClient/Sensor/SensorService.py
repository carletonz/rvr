from RVRClient.Sensor.SensorStream import SensorStream
from RVRClient.Sensor.Sensor import Sensor
import RVRClient.constant as Constants
from RVRClient.rvrClient import RVRClient

# handles multiple sensors streams
class SensorService:
    def __init__(self, rvrClient):
        self.streams = []
        self.rvrClient = rvrClient
        self.setUp()

    def setUp(self):
        ## todo: make this idiot proof
        stream_zero = SensorStream(1, Constants.ST)
        stream_zero.addSensor(Sensor(Constants.IMU, Constants.ST, Constants.ONE_BYTE_SIZE))

        self.streams.append(stream_zero)

    def start(self):
        for stream in self.streams:
            sensorStreamConfigPacket = RVRClient.getConfigureSensorStreamPacket(stream.processor, stream.streamToken, stream.getSensorIds(), stream.getDataSizes())
            self.rvrClient.writePacket(sensorStreamConfigPacket)
        sensorStreamStartPacket = RVRClient.getStartSensorStreamingPacket(Constants.ST)
        self.rvrClient.writePacket(sensorStreamStartPacket)

    def processPacket(self, packet):
        return self.streams[packet.data[0]-1].decodeData(packet.data[1:])
