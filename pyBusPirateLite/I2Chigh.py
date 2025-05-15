# Created by Ondrej Caletka on 2010-11-06.
# Copyright 2010 Ondrej Caletka <ondrej.caletka@gmail.com>
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

from typing import List # Added for type hinting
from .I2C import I2C
from .base import ProtocolError # For raising specific errors if desired

""" enter binary mode """

class I2Chigh(I2C):
    """High level I2C transactions, not included in uc class"""
    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """
        This constructor by default conntects to the first buspirate it can
        find. If you don't want that, set connect to False.

        Parameters
        ----------
        portname : str, optional
            Name of comport (/dev/bus_pirate or COM3)
        speed : int, optional
            Communication speed, use default of 115200
        timeout : float, optional
            Timeout in s to wait for reply
 
        Examples
        --------
        >>> from pyBusPirateLite.I2Chigh import I2Chigh
        >>> i2c = I2Chigh()
        """
        super().__init__(portname, speed, timeout, connect)

    def get_byte(self, i2c_address: int, register_address: int) -> int:
        """ Read one byte from address addr """
        self.start()
        ack_status_write: bytes = self.transfer([(i2c_address << 1), register_address])
        if 0x01 in ack_status_write:
            raise IOError(f"I2C device 0x{i2c_address:02x} did not ACK register 0x{register_address:02x} for read setup.")

        self.start()
        ack_status_read_addr: bytes = self.transfer([(i2c_address << 1) | 0x01])
        if 0x01 in ack_status_read_addr:
            raise IOError(f"I2C device 0x{i2c_address:02x} did not ACK for read operation.")

        read_value_byte: bytes = self.read_byte()
        self.nack()
        self.stop()
        
        return read_value_byte[0]

    def set_byte(self, i2c_address: int, register_address: int, value: int) -> None:
        """ Write one byte to address addr """
        if not (0 <= value <= 255):
            raise ValueError(f"Value to write must be a byte (0-255), got {value}.")

        self.start()
        ack_status: bytes = self.transfer([(i2c_address << 1), register_address, value])
        self.stop()

        if 0x01 in ack_status:
            nack_indices = [i for i, ack_byte in enumerate(ack_status) if ack_byte == 0x01]
            raise IOError(f"I2C write to device 0x{i2c_address:02x}, register 0x{register_address:02x} failed. NACK received at transfer byte(s): {nack_indices}")

    def command(self, i2c_address: int, cmd_byte: int) -> None:
        """ Writes one byte command to slave """
        if not (0 <= cmd_byte <= 255):
            raise ValueError(f"Command byte must be 0-255, got {cmd_byte}.")

        self.start()
        ack_status: bytes = self.transfer([(i2c_address << 1), cmd_byte])
        self.stop()

        if 0x01 in ack_status:
            nack_indices = [i for i, ack_byte in enumerate(ack_status) if ack_byte == 0x01]
            raise IOError(f"I2C command to device 0x{i2c_address:02x} failed. NACK at transfer byte(s): {nack_indices}")

    def set_word(self, i2c_address: int, register_address: int, value: int) -> None:
        """ Writes two byte value (big-endian) to address addr """
        if not (0 <= value <= 65535):
            raise ValueError(f"Value for set_word must be 0-65535, got {value}.")

        vh: int = (value >> 8) & 0xFF
        vl: int = value & 0xFF

        self.start()
        ack_status: bytes = self.transfer([(i2c_address << 1), register_address, vh, vl])
        self.stop()

        if 0x01 in ack_status:
            nack_indices = [i for i, ack_byte in enumerate(ack_status) if ack_byte == 0x01]
            raise IOError(f"I2C set_word to device 0x{i2c_address:02x}, register 0x{register_address:02x} failed. NACK at transfer byte(s): {nack_indices}")

    def get_word(self, i2c_address: int, register_address: int) -> int:
        """ Reads two byte value (big-endian) from address addr """
        self.start()
        ack_status_write: bytes = self.transfer([(i2c_address << 1), register_address])
        if 0x01 in ack_status_write:
            raise IOError(f"I2C device 0x{i2c_address:02x} did not ACK register 0x{register_address:02x} for get_word setup.")

        self.start()
        ack_status_read_addr: bytes = self.transfer([(i2c_address << 1) | 0x01])
        if 0x01 in ack_status_read_addr:
            raise IOError(f"I2C device 0x{i2c_address:02x} did not ACK for get_word read operation.")

        rh_byte: bytes = self.read_byte()
        self.ack()
        rl_byte: bytes = self.read_byte()
        self.nack()
        self.stop()
        
        rh_val: int = rh_byte[0]
        rl_val: int = rl_byte[0]
        
        return (rh_val << 8) + rl_val

'''some standard functions for i2c communication'''
