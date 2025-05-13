# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
# 
# Updated and made Python3 compatible by Juergen Hasch, 20160501
# Copyright 2016 Juergen Hasch <python@elbonia.de>
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

from .BBIO_base import BBIO_base


class SPI(BBIO_base):
    """SPI protocol class for Bus Pirate.

    This class provides methods for SPI communication with the Bus Pirate.
    It supports various SPI configurations including clock speed, clock polarity,
    clock phase, and output type.

    Attributes
    ----------
    portname : str
        Name of the serial port
    speed : int
        Communication speed in baud
    timeout : float
        Timeout in seconds for read operations
    ser : serial.Serial
        Serial port object
    mode : str
        Current mode ('spi')
    connected : bool
        Whether the device is connected
    config : int
        Current SPI configuration
    speed_setting : int
        Current SPI speed setting
    """

    # SPI commands
    SPI_CMD_ENTER = 0x01
    SPI_CMD_START = 0x02
    SPI_CMD_STOP = 0x03
    SPI_CMD_READ = 0x04
    SPI_CMD_WRITE = 0x05
    SPI_CMD_CONFIG = 0x06
    SPI_CMD_WRITE_THEN_READ = 0x07

    # SPI configuration bits
    CFG_IDLE = 0x00
    CFG_POWER = 0x08
    CFG_PULLUP = 0x04
    CFG_AUX = 0x02
    CFG_CS = 0x01

    # SPI speed settings
    SPEED_30KHZ = 0x00
    SPEED_125KHZ = 0x01
    SPEED_250KHZ = 0x02
    SPEED_1MHZ = 0x03
    SPEED_2MHZ = 0x04
    SPEED_2_6MHZ = 0x05
    SPEED_4MHZ = 0x06
    SPEED_8MHZ = 0x07

    # Speed mapping
    SPEEDS = {
        '30kHz': SPEED_30KHZ,
        '125kHz': SPEED_125KHZ,
        '250kHz': SPEED_250KHZ,
        '1MHz': SPEED_1MHZ,
        '2MHz': SPEED_2MHZ,
        '2.6MHz': SPEED_2_6MHZ,
        '4MHz': SPEED_4MHZ,
        '8MHz': SPEED_8MHZ
    }

    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """Initialize SPI protocol.

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
        self.speed_setting = self.SPEED_30KHZ
        # Only set protocol speed if self.port exists
        if hasattr(self, 'port') and self.port:
            self.speed = '1MHz'

    def enter(self) -> bool:
        """Enter SPI mode.

        Returns
        -------
        bool
            True if successful

        Raises
        ------
        ValueError
            If entering SPI mode fails
        """
        if self.mode == 'spi':
            return True

        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        # Send enter command
        self.write(self.SPI_CMD_ENTER)
        self.timeout(0.1)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:  # SPI1
            raise ValueError("Failed to enter SPI mode")

        self.mode = 'spi'
        return True

    def config(self, speed: int = None, clock_polarity: bool = None,
               clock_phase: bool = None, output_type: int = None) -> None:
        """Configure SPI settings.

        Parameters
        ----------
        speed : int, optional
            SPI speed setting (SPEED_* constants), by default None
        clock_polarity : bool, optional
            Clock polarity (True = idle high), by default None
        clock_phase : bool, optional
            Clock phase (True = sample on trailing edge), by default None
        output_type : int, optional
            Output type (0 = 3.3V, 1 = open drain), by default None

        Raises
        ------
        ValueError
            If configuration fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Build configuration byte
        config = 0x00
        if speed is not None:
            self.speed_setting = speed
            config |= (speed & 0x07) << 5
        if clock_polarity is not None:
            config |= (1 if clock_polarity else 0) << 4
        if clock_phase is not None:
            config |= (1 if clock_phase else 0) << 3
        if output_type is not None:
            config |= (output_type & 0x01) << 2

        # Send configuration
        self.write(self.SPI_CMD_CONFIG)
        self.write(config)
        self.timeout(0.1)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise ValueError("Failed to configure SPI")

        self.config = config

    def write_then_read(self, write_data: Union[bytes, bytearray, list],
                       read_length: int = 0) -> bytes:
        """Write data then read response.

        Parameters
        ----------
        write_data : Union[bytes, bytearray, list]
            Data to write
        read_length : int, optional
            Number of bytes to read, by default 0

        Returns
        -------
        bytes
            Read data

        Raises
        ------
        ValueError
            If write/read operation fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Send command
        self.write(self.SPI_CMD_WRITE_THEN_READ)
        self.write(len(write_data))
        self.write(read_length)
        self.timeout(0.1)

        # Write data
        for byte in write_data:
            self.write(byte)
            self.timeout(0.1)

        # Read response
        if read_length > 0:
            return self.read(read_length)
        return b''

    def write(self, data: Union[bytes, bytearray, list]) -> None:
        """Write data.

        Parameters
        ----------
        data : Union[bytes, bytearray, list]
            Data to write

        Raises
        ------
        ValueError
            If write operation fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Send command
        self.write(self.SPI_CMD_WRITE)
        self.write(len(data))
        self.timeout(0.1)

        # Write data
        for byte in data:
            self.write(byte)
            self.timeout(0.1)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise ValueError("Failed to write data")

    def read(self, length: int) -> bytes:
        """Read data.

        Parameters
        ----------
        length : int
            Number of bytes to read

        Returns
        -------
        bytes
            Read data

        Raises
        ------
        ValueError
            If read operation fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Send command
        self.write(self.SPI_CMD_READ)
        self.write(length)
        self.timeout(0.1)

        # Read response
        return self.read(length)

    def start(self) -> None:
        """Start SPI transaction.

        Raises
        ------
        ValueError
            If start operation fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Send command
        self.write(self.SPI_CMD_START)
        self.timeout(0.1)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise ValueError("Failed to start SPI transaction")

    def stop(self) -> None:
        """Stop SPI transaction.

        Raises
        ------
        ValueError
            If stop operation fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        if self.mode != 'spi':
            self.enter()

        # Send command
        self.write(self.SPI_CMD_STOP)
        self.timeout(0.1)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise ValueError("Failed to stop SPI transaction")

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, cfg):
        """ Configure peripherals

        Parameters
        ----------
        cfg: int
            Pin configuration 0000wxyz
            w=power, x=pull-ups, y=AUX, z=CS

        Notes
        -----
        Enable (1) and disable (0) Bus Pirate peripherals and pins. Bit w enables the power supplies, bit x toggles
        the on-board pull-up resistors, y sets the state of the auxiliary pin, and z sets the chip select pin.
        Features not present in a specific hardware version are ignored. Bus Pirate responds 0x01 on success.

        * CS pin always follows the current HiZ pin configuration.
        * AUX is always a normal pin output (0=GND, 1=3.3volts).
        """
        self.write(0x40 | (cfg & 0x0f))
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not set SPI pins")
        self._pins = cfg

    @property
    def speed(self):
        """Get current SPI speed setting."""
        return self.speed_setting

    @speed.setter
    def speed(self, frequency):
        """Set SPI speed.

        Parameters
        ----------
        frequency : str or int
            SPI clock speed (30kHz, 125kHz, 250kHz, 1MHz, 2MHz, 2.6MHz, 4MHz, 8MHz) or serial port speed (int)

        Raises
        ------
        ValueError
            If SPI speed could not be set
        """
        if isinstance(frequency, int):
            # This is the serial port speed, not the SPI speed
            if hasattr(self, 'port') and self.port:
                self.port.baudrate = frequency
            return
        try:
            clock = self.SPEEDS[frequency]
            self.speed_setting = clock
        except KeyError:
            raise ValueError('Clock speed not supported')
        self.write(0x60 | clock)

        if self.response(1, binary=True) != b'\x01':
            raise ValueError('Could not set SPI speed')

    def sniffer(self, cs):
        """ Sniff SPI traffic when CS low(10)/all(01) TODO

        Parameters
        ----------
        cs : Bool
            True: Capture when CS is low
            False: Capture all

        Notes
        -----
        0000 11XX
        The SPI sniffer is implemented in hardware and should work up to 10MHz. It follows the configuration settings
        you entered for SPI mode. The sniffer can read all traffic, or filter by the state of the CS pin.

            [/] - CS enable/disable
            xy - escape character (\\) precedes two byte values X (MOSI pin) and Y (MISO pin) (updated in v5.1)

        Sniffed traffic is encoded according to the table above. The two data bytes are escaped with the '\' character
        to help locate data in the stream.

        Send the SPI sniffer command to start the sniffer, the Bus Pirate responds 0x01 then sniffed data starts to
        flow. Send any byte to exit. Bus Pirate responds 0x01 on exit. (0x01 reply location was changed in v5.8)

        If the sniffer can't keep with the SPI data, the MODE LED turns off and the sniff is aborted. (new in v5.1)

        The sniffer follows the output clock edge and output polarity settings of the SPI mode, but not the input
        sample phase.

        More detailed notes on the SPI sniffer in the SPI user terminal documentation.
        """
        if cs is True:
            cmd = 0x0e
        else:
            cmd = 0x0d
        self.write(cmd)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError('Could not set SPI sniff mode')
