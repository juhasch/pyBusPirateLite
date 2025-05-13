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

from typing import Optional, List # Added List for future use like bulk_transfer

from .base import BusPirate, ProtocolError, BPError


class RawWireCfg:
    """Configuration constants for Raw-Wire mode settings (used with `wire_cfg`).
    
    These bits can be ORed together to form the configuration byte for `wire_cfg`.
    - NA:     Unknown purpose, possibly 'No Action' or a specific pin. (0x01)
    - LSB:    Set bit order to LSB first. Default is MSB first. (0x02)
    - _3WIRE: Enable 3-wire mode. Default is 2-wire mode. (0x04)
    - OUTPUT: Set output type to normal (push-pull). Default is open-drain. (0x08)
    """
    NA: int = 0x01
    LSB: int = 0x02
    _3WIRE: int = 0x04 
    OUTPUT: int = 0x08


class RawWire(BusPirate):
    """ Interface for Bus Pirate's Raw-Wire binary communication mode. """

    # Raw-Wire Command Constants
    _CMD_ENTER_RAWWIRE_MODE: int = 0x05
    _CMD_GET_MODE_VERSION: int = 0x01 
    
    _CMD_START_BIT: int = 0x02      
    _CMD_STOP_BIT: int = 0x03       
    _CMD_READ_BYTE_RAW: int = 0x04 # Bus Pirate command to read a byte via raw wire (implies 8 clock ticks by BP)
    _CMD_READ_BIT: int = 0x07       
    _CMD_PEEK_INPUT_PIN: int = 0x08 
    _CMD_CLOCK_TICK: int = 0x09     
    _CMD_CLOCK_LOW: int = 0x0A      
    _CMD_CLOCK_HIGH: int = 0x0B     
    _CMD_DATA_LOW: int = 0x0C       
    _CMD_DATA_HIGH: int = 0x0D      

    _CMD_BULK_TRANSFER_BASE: int = 0x10 # 0001xxxx
    _CMD_BULK_CLOCK_TICKS_BASE: int = 0x20 # 0010xxxx

    _CMD_CONFIGURE_WIRE_SETTINGS_BASE: int = 0x80 # 1000xxxx, lower 4 bits from RawWireCfg

    _EXPECTED_MODE_VERSION: str = "RAW1"

    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """
        Initializes the RawWire interface.

        Parameters
        ----------
        portname : str, optional
            Name of the serial port.
        speed : int, optional
            Serial communication speed.
        timeout : float, optional
            Timeout in seconds for serial communication.
        connect : bool, optional
            Whether to connect immediately.
 
        Examples
        --------
        >>> from pyBusPirateLite.rawwire import RawWire
        >>> rw = RawWire()
        """
        super().__init__(portname, speed, timeout, connect)

    def enter(self) -> bool:
        """Enter Raw-Wire binary mode.

        Returns
        -------
        bool
            True if Raw-Wire mode was entered successfully.

        Raises
        -------
        BPError
            If already in Raw-Wire mode or cannot enter BitBang mode first.
        ProtocolError
            If mode entry fails.
        """
        if self.mode == 'raw':
            raise BPError("Already in Raw-Wire mode.") 
        if self.mode != 'bb':
           super().enter()

        self.write(self._CMD_ENTER_RAWWIRE_MODE)
        response_str = self.response(4)
        if response_str == self._EXPECTED_MODE_VERSION:
            self.mode = 'raw'
            self.recurse_end()
            return True
        raise ProtocolError(f"Failed to enter Raw-Wire mode. Expected '{self._EXPECTED_MODE_VERSION}', got '{response_str}'")

    def start_bit(self) -> bytes:
        """Sends a 'start bit' command (0x02).
        Legacy. Its specific meaning depends on the protocol being implemented.

        Returns
        -------
        bytes
            The 1-byte response from Bus Pirate, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_START_BIT)
        return self.response(1, binary=True)

    def stop_bit(self) -> bytes:
        """Sends a 'stop bit' command (0x03).
        Legacy. Its specific meaning depends on the protocol being implemented.

        Returns
        -------
        bytes
            The 1-byte response from Bus Pirate, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_STOP_BIT)
        return self.response(1, binary=True)

    def read_bit(self) -> bytes:
        """Reads a single bit from the data input pin (command 0x07).

        Returns
        -------
        bytes
            The 1-byte response (e.g., b'\x00' or b'\x01').
        """
        self.check_mode('raw')
        self.write(self._CMD_READ_BIT)
        return self.response(1, binary=True)

    def peek(self) -> bytes:
        """Peeks at the data input pin state (command 0x08).

        Returns
        -------
        bytes
            The 1-byte response indicating pin state.
        """
        self.check_mode('raw')
        self.write(self._CMD_PEEK_INPUT_PIN)
        return self.response(1, binary=True)

    def clock_tick(self) -> bytes:
        """Generates a single clock pulse (command 0x09).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_CLOCK_TICK)
        return self.response(1, binary=True)

    def clock_low(self) -> bytes:
        """Sets the CLK pin low (command 0x0A).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_CLOCK_LOW)
        return self.response(1, binary=True)

    def clock_high(self) -> bytes:
        """Sets the CLK pin high (command 0x0B).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_CLOCK_HIGH)
        return self.response(1, binary=True)

    def data_low(self) -> bytes:
        """Sets the data output pin (MOSI/DAT) low (command 0x0C).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_DATA_LOW)
        return self.response(1, binary=True)

    def data_high(self) -> bytes:
        """Sets the data output pin (MOSI/DAT) high (command 0x0D).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        """
        self.check_mode('raw')
        self.write(self._CMD_DATA_HIGH)
        return self.response(1, binary=True)

    def wire_cfg(self, config_flags: int) -> bytes:
        """Configures Raw-Wire settings (bit order, wire count, output type).
        Command: 0x80 | config_flags. Use `RawWireCfg` constants.

        Parameters
        ----------
        config_flags : int
            Bitmask of configuration options (e.g., `RawWireCfg.LSB | RawWireCfg.OUTPUT`).
            Must be a 4-bit value (0-15).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).
        
        Raises
        -------
        ValueError
            If `config_flags` is out of the 0-15 range.
        """
        self.check_mode('raw')
        if not (0 <= config_flags <= 0x0F):
            raise ValueError(f"Configuration flags must be a 4-bit value (0-15), got {config_flags:#04x}.")
        self.write(self._CMD_CONFIGURE_WIRE_SETTINGS_BASE | config_flags)
        return self.response(1, binary=True)

    def bulk_clock_ticks(self, ticks: int) -> bytes:
        """Generates a specified number of clock ticks (1 to 16).
        Command: 0x20 | (ticks - 1).

        Parameters
        ----------
        ticks : int
            Number of clock pulses (1-16).

        Returns
        -------
        bytes
            The 1-byte response, typically b'\x01' (ACK).

        Raises
        -------
        ValueError
            If `ticks` is not in the range [1, 16].
        """
        self.check_mode('raw')
        if not (1 <= ticks <= 16):
            raise ValueError(f"Number of ticks must be between 1 and 16, got {ticks}.")
        self.write(self._CMD_BULK_CLOCK_TICKS_BASE | (ticks - 1))
        return self.response(1, binary=True)
