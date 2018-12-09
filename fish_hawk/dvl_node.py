"""
===================================
Doppler velocity log interface node
===================================
THIS CODE IS COMPLETELY UNTESTED AND IS MEANT AS A TEMPLATE ONLY

Interface with the Zoidberg DVL
"""

import serial, time
from zoidberg_nav.msg import DVL

class DVLNode:
    """
    Persistant object to handle serial comunications with DVL over serial
    """
    def __init__(self):
        """
        Function to Initialize the Serial Port
        """
        # open a non-blocking serial port
        ser = serial.Serial(timeout=0)
        ser.baudrate = 115200
        ser.port = '/dev/serial/by-id/usb-FTDI_US232R_FT0TFKDN-if00-port0'
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        self.errNum = 9999

        # Specify the TimeOut in seconds, so that SerialPort doesn't hang
        ser.timeout = 1
        ser.open()  # Opens SerialPort
        self.ser = ser  # make serial port persistant

        # DVL readings
        self.x_velocity = 0
        self.y_velocity = 0
        self.z_velocity = 0
        self.x_position = 0
        self.y_position = 0
        self.altitude = 0

    def is_active(self, is_start):
        """Send startup or shutdown message to dvl over serial port"""
        if is_start:
            # break and then wait before sending start message
            self.ser.send_break(duration=1)
            time.sleep(5)
            # send start message
            self.ser.write(bytes(b'start\r\n'))
            time.sleep(5)
            # flush out the buffer
            self.ser.read_all()
            for _ in range(5):
                # check for valid message
                outputCheck = self.ser.readline()
                splitLine = outputCheck.split(bytes(b','))
                if splitLine[0] == b'$DVLNAV':
                    return
            # if none of the messages are valid, error out
            raise(IOError('Communication not initialized'))
        else:
            self.ser.send_break(1)
            self.ser.write(bytes(b'stop\r\n'))
            self.ser.close()


    def check_readings(self):
        """Update to most recent DVL message"""
        isnew = False  # assume there won't be any messages
        # readline is non-blocking, can return None
        msg = self.ser.readline()
        while msg is not None:
            splitLine = lineRead.split(bytes(b','))

            if splitLine[0] != b'$DVLNAV':
                # This is not the message of interest, moving along
                msg = self.ser.readline()
                continue
            # The message was good
            isnew = True  # got something
            # velocity estimates have error codes
            self.x_velocity = float(splitLine[4]) if splitLine[4] else self.errNum
            self.y_velocity = float(splitLine[5]) if splitLine[5] else self.errNum
            self.z_velocity = float(splitLine[6]) if splitLine[6] else self.errNum
            # no error codes for x,y & alt coordinates, reading starts at 0
            self.x_position = float(splitLine[7])
            self.y_position = float(splitLine[8])
            self.altitude = float(splitLine[9])
        return isnew
