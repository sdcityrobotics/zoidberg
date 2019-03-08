"""
===================================
Doppler velocity log interface node
===================================
THIS CODE IS COMPLETELY UNTESTED AND IS MEANT AS A TEMPLATE ONLY

Interface with the Zoidberg DVL
"""
import serial, time
from zoidberg import empty_value

class DVLNode:
    """
    Persistant object to handle serial comunications with DVL over serial
    """
    def __init__(self, port):
        """
        Function to Initialize the Serial Port
        Linux port: '/dev/serial/by-id/usb-FTDI_US232R_FT0TFKDN-if00-port0'
        """
        self.port = port
        # open a non-blocking serial port
        self._ser = serial.Serial(timeout=0, baudrate=115200)

        # DVL readings, initialize to empty values
        self._msg = None
        self.x_velocity = empty_value
        self.y_velocity = empty_value
        self.z_velocity = empty_value
        self.x_position = empty_value
        self.y_position = empty_value
        self.altitude = empty_value

    def is_active(self, is_start):
        """Send startup or shutdown message to dvl over serial port"""
        if is_start:
            self._ser.port = self.port
            self._ser.port.open()
            # break and then wait before sending start message
            self._ser.send_break(duration=1)
            time.sleep(5)
            # send start message
            self._ser.write(bytes(b'start\r\n'))
            time.sleep(5)
            # flush out the buffer
            self._ser.read_all()
            for _ in range(5):
                # check for valid message
                outputCheck = self._ser.readline()
                splitLine = outputCheck.split(bytes(b','))
                if splitLine[0] == b'$DVLNAV':
                    return
            # if none of the messages are valid, error out
            raise(IOError('Communication not initialized'))
        else:
            self._ser.send_break(1)
            self._ser.write(bytes(b'stop\r\n'))
            self._ser.close()


    def check_readings(self):
        """Update to most recent DVL message"""
        isnew = self._read_buffer()
        if not isnew:
            return
        # velocity estimates have error codes
        sl = self._msg.split(bytes(b','))
        self.x_velocity = float(sl[4]) if sl[4] else empty_value
        self.y_velocity = float(sl[5]) if sl[5] else empty_value
        self.z_velocity = float(sl[6]) if sl[6] else empty_value
        # no error codes for x,y & alt coordinates, reading starts at 0
        self.x_position = float(sl[7])
        self.y_position = float(sl[8])
        self.altitude = float(sl[9])

    def _read_buffer(self):
        """Basic loop to read to latest reading on a non-blocking buffer"""
        isnew = False  # assume there won't be any messages
        try:
            msg = self._ser.readline()
        except:
            print("Reading from a closed serial port")
            return
        # readline is non-blocking, can return None
        while msg is not None:
            if msg[:7] == b'$DVLNAV':
                # The message was good
                self._msg = msg
                isnew = True  # got something
        return isnew
