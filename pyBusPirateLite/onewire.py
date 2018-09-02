# Created by Sean Nelson on 2009-10-20.
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

"""
Binary1WIRE mode:
00000000 - reset to BBIO
00000001 - mode version string (1W01)
00000010 - 1wire reset
00000100 - read byte
00001000 - ROM search macro (0xf0)
00001001 - ALARM search macro (0xec)
0001xxxx - Bulk transfer, send 1-16 bytes (0=1byte!)
0100wxyz - Configure peripherals w=power, x=pullups, y=AUX, z=CS (
0101wxyz - Read peripherals (planned, not implemented)
"""

from .BitBang import BusPirate


class OneWire(BusPirate):
    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """ Provide access to the Bus Pirate Onewire protocol

        Parameters
        ----------
        portname : str
            Name of comport (/dev/bus_pirate or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply
        connect : bool
            Automatically connect to BusPirate (default) 

        Example
        -------
        >>> spi = OneWire()
        """
        super().__init__(portname, speed, timeout, connect)

    def enter_1wire(self):
        self.check_mode('bb')
        self.write(0x04)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "1W01":
            self.mode = '1wire'
            self.bp_port = 0b00         # two bit port
            self.bp_config = 0b0000
            self._attempts_ = 1
            return 1
        return self.recurse_flush(self.enter_1wire)

    def reset(self):
        self.check_mode('1wire')
        self.port.write(chr(0x02))
        self.timeout(0.1)
        return self.response(1)

    def rom_search(self):
        self.check_mode('1wire')
        self.port.write(chr(0x08))
        self.timeout(0.1)
        self.__group_response()

    def alarm_search(self):
        self.check_mode('1wire')
        self.port.write(chr(0x09))
        self.timeout(0.1)
        self.__group_response()

    def __group_response(self):
        self.check_mode('1wire')
        EOD = chr(0xff)
        count = 0
        while count < 8:
            if count > 255:
                raise IOError('EOD counter exceeded')
            data = self.port.read(8)
            if data == EOD:
                count +=1
            else:
                print(data)
