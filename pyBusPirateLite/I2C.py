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

from __future__ import annotations
from typing import List, Optional, Union, ClassVar
from .base import BusPirate


class I2C(BusPirate):
    """I2C interface for Bus Pirate.

    This class provides access to the Bus Pirate's I2C interface. It supports
    various I2C configurations including clock speed and output type.

    Attributes:
        portname (str): Name of the serial port (e.g., '/dev/bus_pirate' or 'COM3')
        speed (int): Communication speed in baud
        timeout (float): Timeout in seconds for read operations
        ser (serial.Serial): Serial port object
        mode (str): Current mode of the Bus Pirate
        connected (bool): Whether the Bus Pirate is connected
    """

    # I2C commands
    CMD_I2C_ENTER: ClassVar[int] = 0x02
    CMD_I2C_START: ClassVar[int] = 0x02
    CMD_I2C_STOP: ClassVar[int] = 0x03
    CMD_I2C_ACK: ClassVar[int] = 0x06
    CMD_I2C_NACK: ClassVar[int] = 0x07
    CMD_I2C_WRITE: ClassVar[int] = 0x10
    CMD_I2C_READ: ClassVar[int] = 0x20
    CMD_I2C_WRITE_READ: ClassVar[int] = 0x30
    CMD_I2C_CONFIG: ClassVar[int] = 0x80

    # I2C speeds
    SPEEDS = {'5kHz': 0b000,
             '50kHz': 0b001,
             '100kHz': 0b010,
             '400kHz': 0b011}

    pin_mapping = {'AUX': 0b10,
                    'CS': 0b01}

    # I2C configuration bits
    CFG_IDLE = 0x00
    CFG_POWER = 0x08
    CFG_PULLUP = 0x04
    SPEED_100KHZ = 0b010

    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """Initialize I2C protocol.

        Parameters
        ----------
        portname : str, optional
            Name of the serial port, by default ''
        speed : int, optional
            Communication speed in baud, by default 115200
        timeout : float, optional
            Timeout in seconds for read operations, by default 0.1
        connect : bool, optional
            Whether to connect immediately, by default True
        """
        super().__init__(portname, speed, timeout, connect)
        self.config = self.CFG_IDLE
        self.speed_setting = self.SPEED_100KHZ
        self.i2c_speed: Optional[str] = None
        # Only set protocol speed if self.port exists
        if hasattr(self, 'port') and self.port:
            self.speed = '100kHz'
        
    def enter(self) -> bool:
        """Enter I2C mode.

        Returns:
            bool: True if successful

        Raises:
            ValueError: If I2C mode could not be entered
        """
        if self.mode == 'i2c':
            return True
        if self.mode != 'bb':
            super(I2C, self).enter()
        self.write(self.CMD_I2C_ENTER)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "I2C1":
            self.mode = 'i2c'
            self.bp_port = 0b00         # two bit port
            self.bp_config = 0b0000
            self.recurse_end()
            return True
        self.recurse_flush(self.enter)
        raise ValueError('Could not enter I2C mode')

    @property
    def check_i2c(self) -> bool:
        """
        Test if we are still in I2C mode.

        Returns:
            bool: True if in I2C mode
        Raises:
            ValueError: If not in I2C mode
        """
        resp = self.response(20)
        self.write(0x01)
        resp = self.response(20)
        if resp == "I2C1":
            return True
        raise ValueError(f'Not in I2C mode, response {resp}.')

    def start(self) -> None:
        """Send I2C start condition.

        Raises:
            ValueError: If not in I2C mode
            IOError: If start condition fails
        """
        if self.mode != 'i2c':
            resp = self.response(4)
            raise ValueError(f'Not in I2C mode, response {resp}.')

        self.write(self.CMD_I2C_START)
        if self.response(1, binary=True) != b'\x01':
            raise IOError('Could not send I2C start bit')

    def stop(self) -> None:
        """Send I2C stop condition.

        Raises:
            IOError: If stop condition fails
        """
        self.write(self.CMD_I2C_STOP)
        if self.response(1, binary=True) != b'\x01':
            raise IOError('Could not send I2C stop bit')

    def ack(self) -> None:
        """Send I2C ACK.

        Raises:
            IOError: If ACK fails
        """
        self.write(self.CMD_I2C_ACK)
        if self.response(1, binary=True) != b'\x01':
            raise IOError('Could not send ACK')

    def nack(self) -> None:
        """Send I2C NACK.

        Raises:
            IOError: If NACK fails
        """
        self.write(self.CMD_I2C_NACK)
        if self.response(1, binary=True) != b'\x01':
            raise IOError('Could not send NACK')

    def sniffer(self) -> str:
        """
        Sniff traffic on an I2C bus.
        Returns:
            str: Sniffed data
        """
        self.write(0x0f)
        resp = self.response(64)
        return resp

    def transfer(self, txdata: Union[List[int], bytes]) -> List[bool]:
        """
        Bulk I2C write, send 1-16 bytes.
        Args:
            txdata: Data to send (1-16 bytes)
        Returns:
            List[bool]: True (ACK) or False (NACK) for each transmitted byte
        Raises:
            ValueError: If more than 16 bytes are requested to be sent
        """
        length = len(txdata)
        if length > 16:
            raise ValueError('A maximum of 16 bytes can be sent')
        self.write(self.CMD_I2C_WRITE | (length - 1))
        for data in txdata:
            self.write(data)

        resp = self.response(length+1)
        if resp[0] != '\x01':
            raise ValueError("Could not transfer I2C data")

        # Convert response to bools: 0x00=ACK (True), 0x01=NACK (False)
        return [b == '\x00' for b in resp[1:]]

    @property
    def speed(self) -> Optional[str]:
        """Get current I2C speed.

        Returns
        -------
        str
            Current I2C speed setting
        """
        return self.speed_setting

    @speed.setter
    def speed(self, frequency):
        """Set I2C speed.

        Parameters
        ----------
        frequency : str
            I2C clock speed (5kHz, 50kHz, 100kHz, 400kHz)

        Raises
        ------
        ValueError
            If I2C speed could not be set
        """
        if isinstance(frequency, int):
            # This is the serial port speed, not the I2C speed
            if hasattr(self, 'port') and self.port:
                self.port.baudrate = frequency
            return

        try:
            clock = self.SPEEDS[frequency]
            self.speed_setting = clock
        except KeyError:
            raise ValueError('Clock speed not supported')
        self.write(self.CMD_I2C_CONFIG | clock)

        if self.response(1, binary=True) != b'\x01':
            raise ValueError('Could not set IC2 speed')
        self.i2c_speed = frequency

    def write_then_read(
        self, numtx: int, numrx: int, txdata: Union[bytes, List[int]]
    ) -> bytes:
        """Write then read data.

        Args:
            numtx: Number of bytes to write
            numrx: Number of bytes to read
            txdata: Data to write

        Returns:
            bytes: Read data

        Raises:
            IOError: If transmission fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if isinstance(txdata, list):
            txdata = bytes(txdata)

        # Send write-then-read command
        self.write([self.CMD_I2C_WRITE_READ | (numtx - 1)])

        # Write data
        self.write(txdata)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise IOError('Error in transmission')

        # Read data
        return self.read(numrx)

    def write(self, data: Union[bytes, List[int]]) -> None:
        """Write data to the Bus Pirate.

        Args:
            data: Data to write (bytes or list of integers)

        Raises:
            IOError: If command is illegal or fails
        """
        if isinstance(data, int):
            if data > 0xFF:
                raise IOError('Illegal extended AUX command')
            self.port.write(bytes([data]))
            return

        if isinstance(data, list):
            data = bytes(data)
        self.port.write(data)

    def read(self, length: int = 1) -> bytes:
        """Read data from the Bus Pirate.

        Args:
            length: Number of bytes to read (default: 1)

        Returns:
            bytes: Read data

        Raises:
            IOError: If read fails
        """
        return self.port.read(length)

    def aux(self, cmd: int) -> str:
        """
        Provides extended use of AUX pin. Requires one command byte. Bus Pirate acknowledges 0x01.
        Args:
            cmd: Command byte
        Returns:
            str: Response string
        Raises:
            IOError: If command is illegal or fails
        """
        if cmd not in (0x00, 0x01, 0x02, 0x03, 0x10, 0x20):
            raise IOError('Illegal extended AUX command')
        self.write(self.CMD_I2C_CONFIG | cmd)
        if self.response(1, binary=True) != b'\x01':
            raise IOError('Error in extended AUX command')
        resp = self.response(20, binary=True)

        # firmware ~7.1 responds to the command with text followed by another
        # 0x01 confirmation. this behaivor was not well documented on the wiki
        if resp[-1] != 0x01:
            raise IOError('Error in extended AUX command')
        return resp[:-1].decode('ASCII')

    def configure(self, power: bool = False, pullup: bool = False) -> None:
        """Configure I2C interface.

        Args:
            power: Whether to enable power supply (default: False)
            pullup: Whether to enable pullup resistors (default: False)

        Raises:
            IOError: If configuration fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        # Send config command
        config = 0
        if power:
            config |= self.pin_mapping['AUX']
        if pullup:
            config |= self.pin_mapping['CS']

        self.write([self.CMD_I2C_CONFIG | config])

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise IOError('Error configuring pins')

        self.bp_config = config
