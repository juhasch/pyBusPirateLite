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

""
from .I2C import I2C

""" enter binary mode """

class I2Chigh(I2C):
    """High level I2C transactions, not included in uc class"""
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
 
        Examples
        --------
        >>> from pyBusPirateLite.I2Chigh import I2Chigh
        >>> i2c = I2Chigh()
        """
        super().__init__(portname, speed, timeout, connect)

    def get_byte(self, i2caddr, addr):
        """ Read one byte from address addr """
        self.start()
        stat = self.transfer([i2caddr << 1, addr])
        self.start()
        stat += self.transfer([i2caddr << 1 | 1])
        r = self.read_byte()
        self.nack()
        self.stop()
        if stat.find(chr(0x01)) != -1:
            raise IOError("I2C command on address 0x%02x not acknowledged!" % (i2caddr))
        return ord(r)

    def set_byte(self, i2caddr, addr, value):
        """ Write one byte to address addr """
        self.start()
        stat = self.transfer([i2caddr << 1, addr, value])
        self.stop()
        if stat.find(chr(0x01)) != -1:
            raise IOError("I2C command on address 0x%02x not acknowledged!" % (i2caddr))

    def command(self, i2caddr, cmd):
        """ Writes one byte command to slave """
        self.send_start_bit()
        stat = self.bulk_trans(2, [i2caddr << 1, cmd])
        self.send_stop_bit()
        if stat[0] == chr(0x01):
            raise IOError("I2C command on address 0x%02x not acknowledged!" % (i2caddr))

    def set_word(self, i2caddr, addr, value):
        """ Writes two byte value (big-endian) to address addr """
        vh = value / 256
        vl = value % 256
        self.send_start_bit()
        stat = self.bulk_trans(4, [i2caddr << 1, addr, vh, vl])
        self.send_stop_bit()
        if stat.find(chr(0x01)) != -1:
            raise IOError("I2C command on address 0x%02x not acknowledged!" % (i2caddr))

    def get_word(self, i2caddr, addr):
        """ Reads two byte value (big-endian) from address addr """
        self.send_start_bit()
        stat = self.bulk_trans(2, [i2caddr << 1, addr])
        self.send_start_bit()
        stat += self.bulk_trans(1, [i2caddr << 1 | 1])
        rh = self.read_byte()
        self.send_ack()
        rl = self.read_byte()
        self.send_nack()
        self.send_stop_bit()
        if stat.find(chr(0x01)) != -1:
            raise IOError("I2C command on address 0x%02x not acknowledged!" % (i2caddr))
        return ord(rh) * 256 + ord(rl)

'''some standard functions for i2c communication'''
