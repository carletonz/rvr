from RVRClient.model.attribute import Attribute

# UART Port Settings
UART_PORT = "/dev/ttyS0"
BAUD_RATE = 115200

MAX_PACKETS_TO_READ = 5

# Processors
NORDIC = 0X01
ST = 0X02

# Packet flags
IS_RESPONSE = 1
REQUEST_RESPONSE = 2
RESPONSE_ON_ERROR = 4
IS_ACTIVITY = 8
HAS_TARGET_ID = 16
HAS_SOURCE_ID = 32
# These flags are not currently used
#UNUSED_FLAG = 64
#HAS_EXTENDED_FLAGS = 128

# Packet Constants
START_BYTE = 0x8d
END_BYTE = 0xd8
ESC_BYTE = 0xab
ESC_ESC_BYTE = (ESC_BYTE*0x100)+0x23
ESC_START_BYTE = (ESC_BYTE*0x100)+0x05
ESC_END_BYTE = (ESC_BYTE*0x100)+0x50

# Device Ids
DEVICE_API_AND_SHELL = 0x10
DEVICE_SYSTEM_INFO = 0x11
DEVICE_POWER = 0x13
DEVICE_DRIVE = 0x16
DEVICE_SENSOR = 0x18
DEVICE_CONNECTION = 0x19
DEVICE_IO = 0x1a
DEVICE_TO_NAME = {
    DEVICE_API_AND_SHELL: "API and Shell",
    DEVICE_SYSTEM_INFO: "System Info",
    DEVICE_POWER: "Power",
    DEVICE_DRIVE: "Drive",
    DEVICE_SENSOR: "Sensor",
    DEVICE_CONNECTION: "Connection",
    DEVICE_IO: "IO"
}

# Errors
ERROR_SUCCESS = 0x00
ERROR_BAD_DEVICE_ID = 0x01
ERROR_BAD_COMMAND_ID = 0x02
ERROR_NOT_IMPLEMENTED = 0x03
ERROR_RESTRICTED_COMMAND = 0x04
ERROR_BAD_DATA_LENGTH = 0x05
ERROR_COMMAND_FAILED = 0x06
ERROR_BAD_PARAMETER_VALUE = 0x07
ERROR_BUSY = 0x08
ERROR_BAD_TARGET_ID = 0x09
ERROR_TARGET_UNAVAILABLE = 0x0a
ERROR_TO_NAME = {
    ERROR_SUCCESS: "Command executed successfully",
    ERROR_BAD_DEVICE_ID: "Device ID is invalid (or is invisible with current permissions)",
    ERROR_BAD_COMMAND_ID: "Command ID is invalid (or is invisible with current permissions)",
    ERROR_NOT_IMPLEMENTED: "Command is not yet implemented or has a null handler",
    ERROR_RESTRICTED_COMMAND: "Command cannot be executed in the current state or mode",
    ERROR_BAD_DATA_LENGTH: "Payload data length is invalid",
    ERROR_COMMAND_FAILED: "Command failed to execute for a command-specific reason",
    ERROR_BAD_PARAMETER_VALUE: "At least one data parameter is invalid",
    ERROR_BUSY: "The operation is already in progress or the module is busy",
    ERROR_BAD_TARGET_ID: "Target does not exist",
    ERROR_TARGET_UNAVAILABLE: "Target exists but is unavailable (e.g., it is asleep or disconnected)"
}

# Sensors
COLOR_DETECTION = (0X00, 0x03)
AMBIENT_LIGHT = (0x00, 0x0A)
QUATERNION = (0x00, 0x00)
IMU = (0x00, 0x01)
ACCELEROMETER = (0x00, 0x02)
GYROSCOPE = (0x00, 0x04)
LOCATOR = (0x00, 0x06)
VELOCITY = (0x00, 0x07)
SPEED = (0x00, 0x08)
ENCODERS = (0x00, 0x0B)
CORE_TIME = (0x00, 0x09)
SENSOR_ATTRIBUTES = {
    COLOR_DETECTION: [Attribute(0, 255), Attribute(0, 255), Attribute(0, 255), Attribute(0, 255), Attribute(0, 1)],  # [R, G, B, Index, Confidence]
    AMBIENT_LIGHT: [Attribute(0, 120000)],  # [Light]
    QUATERNION: [Attribute(-1, 1), Attribute(-1, 1), Attribute(-1, 1), Attribute(-1, 1)],  # [W, X, Y, Z]
    IMU: [Attribute(-180, 180), Attribute(-90, 90), Attribute(-180, 180)],  # [Pitch, Roll, Yaw]
    ACCELEROMETER: [Attribute(-16, 16), Attribute(-16, 16), Attribute(-16, 16)],  # [X, Y, Z]
    GYROSCOPE: [Attribute(-2000, 2000), Attribute(-2000, 2000), Attribute(-2000, 2000)],  # [X, Y, Z]
    LOCATOR: [Attribute(-16000, 16000), Attribute(-16000, 16000)],  # [X, Y]
    VELOCITY: [Attribute(-5, 5), Attribute(-5, 5)],  # [X, Y]
    SPEED: [Attribute(0, 5)],  # [Speed]
    ENCODERS: [Attribute(0, 4294967295), Attribute(0, 4294967295)],  # [LeftTicks, RightTicks]
    CORE_TIME: [Attribute(0, 4294967295), Attribute(0, 4294967295)]  # [TimeUpper, TimeLower]
}
SENSOR_TO_NAME = {
    COLOR_DETECTION: "Color Detection",
    AMBIENT_LIGHT: "Ambient Light",
    QUATERNION: "Quaternion",
    IMU: "IMU",
    ACCELEROMETER: "Accelerometer",
    GYROSCOPE: "Gyroscope",
    LOCATOR: "Locator",
    VELOCITY: "Velocity",
    SPEED: "Speed",
    ENCODERS: "Encoders",
    CORE_TIME: "Core Time"
}
ONE_BYTE_SIZE = 0X00
TWO_BYTE_SIZE = 0X01
FOUR_BYTE_SIZE = 0X02
SIZE_TO_MAX_VALUE = {
    ONE_BYTE_SIZE: 1,
    TWO_BYTE_SIZE: 2,
    FOUR_BYTE_SIZE: 4,
}
MAX_SENSORS_PER_STREAM = 5
SENSOR_PUBLISH_RATE = [0x07, 0xd0]  # 2000 milliseconds

# Motors
MODE_OFF = 0X00
MODE_FORWARD = 0X01
MODE_REVERSE = 0X02

