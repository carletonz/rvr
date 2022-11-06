# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray

import serial
import RVRClient.constant as Constants
from RVRClient.rvrClient import RVRClient
from RVRClient.Sensor.SensorService import SensorService
from RVRClient.Sensor.Sensor import Sensor


class MinimalPublisher(Node):

    def __init__(self, rvrClient):
        super().__init__('minimal_publisher')
        self.rvrClient.writePacket(RVRClient.getWakeCommandPacket())
        self.publisherImuSensor = self.create_publisher(Float32MultiArray, Constants.SENSOR_TO_NAME[Constants.GYROSCOPE], 10)
        self.rvrClient = rvrClient
        self.sensors = SensorService(rvrClient)
        rvrClient.writePacket(RVRClient.getStopSensorStreamingPacket(Constants.ST))
        self.sensors.start()
        timer_period = 1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        packets = self.rvrClient.readPackets(1)
        if len(packets) > 0 and packets[0].did == Constants.DEVICE_SENSOR and packets[0].seq != 0:
            print('sensor packet: [{}]'.format(', '.join('0x{:02x}'.format(x) for x in packets[0].getEncodedData())))
            self.sensors.processPacket(packets[0])

        if Sensor.ActiveSensors[(Constants.GYROSCOPE, Constants.ST)]:
            msg = Float32MultiArray()
            print(Sensor.ActiveSensors[(Constants.GYROSCOPE, Constants.ST)].decodedData)
            msg.data = Sensor.ActiveSensors[(Constants.GYROSCOPE, Constants.ST)].decodedData
            self.publisherImuSensor.publish(msg)



def getUartPort():
    port = serial.Serial(Constants.UART_PORT, Constants.BAUD_RATE)
    port.flushInput()
    return port

def main(args=None):
    rclpy.init(args=args)
    rvr = RVRClient(getUartPort(), True)
    minimal_publisher = MinimalPublisher(rvr)

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
    rvr.closePort()


if __name__ == '__main__':
    main()
