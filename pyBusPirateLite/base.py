# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
# 
# This file is part of pyBusPirate.
# 
# pyBusPirate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyBusPirate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.

from time import sleep

import serial


class BPError(IOError):
    pass


class ProtocolError(IOError):
    pass


class BusPirate:
    """Base class for all modes. This contains low-level functions for direct
    hardware access.

    Note: This class also contains some of the older functions that are now
    probably outdated
    """

    """
    PICSPEED = 24MHZ / 16MIPS
    """
    # 0x01 CS
    # 0x08 - +3.3V

    PIN_CS = 0x01
    PIN_MISO = 0x02
    PIN_CLK = 0x04
    PIN_MOSI = 0x08
    PIN_AUX = 0x10
    PIN_PULLUP = 0x20
    PIN_POWER = 0x40

    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """
        This constructor by default conntects to the first buspirate it can
        find. If you don't want that, set connect to False.

        Parameters
        ----------
        portname : str
            Name of comport (/dev/bus_pirate or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply
        """

        self.minDelay = 1 / 115200
        self.mode = None
        self.port = None
        self.connected = False
        self.t = True
        self.bp_config = None
        self.bp_port = None
        self.bp_dir = None
        self.portname = ''
        self.pins_state = None
        self.pins_direction = None

        if connect is True:
            self.connect(portname, speed, timeout)
            self.enter()

    _attempts_ = 0  # global stored for use in enter

    @property
    def adc_value(self):
        """ Read and return the voltage on the analog input pin. """
        # raise error to prevent tab-completion having side-effects
        if self.mode != 'bb':
            raise TypeError("Action only valid in bitbang mode")
        self.write(0x14)
        val = int.from_bytes(self.response(2, binary=True), 'big')
        # see
        # http://dangerousprototypes.com/blog/2009/10/09/bus-pirate-raw-bitbang-mode/
        # for conversion formula.
        return (val/1024.0) * 3.3 * 2

    def set_power_on(self, val):
        self.write(0x80 | (self.PIN_POWER if val else 0))
        self.response(1, binary=True)
    power_on = property(None, set_power_on, doc="""
        Enable or disable the built-in power supplies. Note that the power
        supplies reset every time you change modes.

        This is a read-only attribute due to API limitations of the buspirate
        firmware. """)

    def enter_bb(self):
        """Enter bitbang mode

        This is the be-all-end-all restart function.  It will keep trying
        to get the bus pirate into bit bang mode even if it is stuck.  Call this
        to get the bus pirate into a known state (bb mode)

        This command resets the Bus Pirate into raw bitbang mode from the user terminal.
        It also resets to raw bitbang mode from raw SPI mode, or any other protocol mode.
        This command always returns a five byte bitbang version string "BBIOx", w
        here x is the current protocol version (currently 1).

        Some terminals send a NULL character (0x00) on start-up, causing the Bus Pirate to enter binary mode when
        it wasn't wanted. To get around this, you must now enter 0x00 at least 20 times to enter raw bitbang mode.

        Notes
        -----
        The Bus Pirate user terminal could be stuck in a configuration menu when your program attempts to enter
        binary mode. One way to ensure that you're at the command line is to send <enter> at least 10 times,
        and then send '#' to reset. Next, send 0x00 to the command line 20+ times until you get the BBIOx version string.
        After entering bitbang mode, you can enter other binary protocol modes.

        Raises
        ------
        IOError
            If device is not connected
        """
        if self.connected is not True:
            raise IOError('Device not connected')
        self.timeout(self.minDelay * 10)
        self.port.flushInput()
        for i in range(10):
            self.write(0x00)
            r = self.response(1, binary=True)
            if r:
                break
            for m in range(2):
                 self.write(0x00)

        self.timeout(self.minDelay * 10)
        self.port.flushInput()
        self.timeout(self.minDelay * 10)
        resp = self.response(200)
        self.write(0x00)
        resp =  self.response(5)
        if resp == "BBIO1":
            self.mode = 'bb'
            self.bp_config = 0x00  # configuration bits determine action of power sources and pullups
            self.bp_port = 0x00  # out_port similar to ports in microcontrollers
            self.bp_dir = 0x1F  # direction port similar to microchip microcontrollers.  (1) is input, (0) is output
            self.port.flushInput()
            return True
        raise BPError('Could not enter bitbang mode')

    def enter(self):
        """Enter bitbang mode.
           Will be overriden by other classes 
        """
        if self.mode == 'bb':
            return
        return self.enter_bb()

    def hw_reset(self):
        """Reset Bus Pirate

        The Bus Pirate responds 0x01 and then performs a complete hardware reset.
        The hardware and firmware version is printed (same as the 'i' command in the terminal),
        and the Bus Pirate returns to the user terminal interface. Send 0x00 20 times to enter binary mode again.
        """
        if self.mode != 'bb':
            self.enter_bb()
        self.write(0x0f)
        self.port.flushInput()
        self.timeout(.1)
        self.mode = None

    def get_port(self):
        """Detect Buspirate and return first detected port
        
        Returns
        -------
        str
            First valid port name
        """
        try:
            import serial.tools.list_ports as list_ports
        except ImportError:
            raise ImportError('Pyserial version with serial.tools.list_port required')

        import serial

        # the API in version 2 and 3 is different
        if serial.VERSION[0] == '2':
            ports = list_ports.comports()
            for port in ports:
                if len(port) == 3 and '0403:6001' in port[2]:
                    return port[0]
                if len(port) == 3 and 'VID_0403+PID_6001' in port[2]:
                    return port[0]
        else:
            ports = list_ports.comports()
            for port in ports:
                if hasattr(port, 'pid') and hasattr(port, 'vid'):
                    if port.vid == 1027 and port.pid == 24577:
                        return port.device

    def connect(self, portname='', speed=115200, timeout=0.1):
        """Will try to automatically find a port regardless of os

        Parameters
        ----------
        portname : str
            Name of comport (e.g. /dev/ttyUSB0 or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply

        Raises
        ------
        ImportError
            If helper function to find serial port is not available
        IOError
            If device could not be opened
        """

        if portname == '':
            portname = self.get_port()
        if portname == '':
            raise IOError('Could not autodetect a BusPirate device.')

        self.portname = portname
        try:
            self.port = serial.Serial(portname, speed, timeout=timeout)
        except serial.serialutil.SerialException:
            raise IOError('Could not open port %s' % portname)
        self.connected = True
        self.minDelay = 1 / speed

    def disconnect(self):
        """ Disconnect bus pirate, close com port """
        if self.port:
            self.port.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Disconnect bus pirate when exiting"""
        self.disconnect()

    def timeout(self, timeout = 0.1):
        sleep(timeout)

    def write(self, value):
        self.port.write(value.to_bytes(1, 'big'))
        
    def response(self, byte_count=1, binary=False):
        """Request a number of bytes

        Parameters
        ----------
        byte_count : int
            Number of bytes to read
        binary : bool
            Return binary (True) or unicode values (False)
        """
        data = self.port.read(byte_count)
        if binary is True:
            return data
        else:
            return data.decode()

    def recurse_end(self):
        self._attempts_ = 0

    def recurse(self, func, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            return func(*args)
        raise IOError('bus pirate malfunctioning')

    def recurse_flush(self, func, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            for n in range(5):
                self.write(0x00)
                self.port.flushInput()
            return func(*args)
        raise IOError('bus pirate malfunctioning')


""" General Commands for Higher-Level Modes.
Note: Some of these do not have error checking implemented
(they return a 0 or 1.  You have to do your own error
checking.  This is as planned, since all of these
depend on the device you are interfacing with)"""


def send_start_bit(self):
    self.write(0x02)
    self.response(1, True)
    if self.response(1, binary=True) == b'\x01':
        self.recurse_end()
        return 1
    return self.recurse(self.send_start_bit)


def send_stop_bit(self):
    self.write(0x03)
    if self.response(1, binary=True) == b'\x01':
        self.recurse_end()
        return 1
    return self.recurse(self.send_stop_bit)


def read_byte(self):
    """Reads a byte from the bus, returns the byte. You must ACK or NACK each
    byte manually.  NO ERROR CHECKING (obviously)"""
    if self.mode == 'raw':
        self.write(0x06)
        return self.response(1, binary=True)
    else:
        self.write(0x04)
        return self.response(1, binary=True)


def bulk_trans(self, byte_count=1, byte_string=None):
    """this is how you send data in most of the communication modes.
    See the i2c example function in common_functions.
    Send the data, and read the returned array.
    In I2C:  A '1' means that it was NOT ACKNOWLEDGED, and a '0' means that
    it WAS ACKNOWLEDGED (the reason for this is because this is what the
    bus pirate itself does...)
    In modes other than I2C I think it returns whatever data it gets while
    sending, but this feature is untested.  PLEASE REPORT so that I can
    document it."""
    if byte_string is None:
        pass
    self.write(0x10 | (byte_count - 1))
    for i in range(byte_count):
        self.write(byte_string[i])
    data = self.response(byte_count + 1, binary=True)
    if data[0] == 1:  # bus pirate sent an acknolwedge properly
        self.recurse_end()
        return data[1:]
    self.recurse(self.bulk_trans, byte_count, byte_string)
