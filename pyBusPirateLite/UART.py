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

from .base import BPError, BusPirate

FOSC = (32000000 / 2)


class UARTCfg:
    OUTPUT_TYPE = 0x10
    DATABITS = 0x0C
    STOPBITS = 0x02
    POLARITY = 0x01


class UARTSpeed:
    _300 = 0b0000
    _1200 = 0b0001
    _2400 = 0b0010
    _4800 = 0b0011
    _9600 = 0b0100
    _19200 = 0b0101
    _33250 = 0b0110
    _38400 = 0b0111
    _57600 = 0b1000
    _115200 = 0b1001


class UART(BusPirate):
    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """ Provide the Bus Pirate UART interface

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
        >>> uart = UART()
        """
        self._config = None
        self._echo = False
        super().__init__(portname, speed, timeout, connect)

    def enter(self):
        """ Enter UART mode

        Raises
        ------
        BPError
            Could not enter UART mode
        """
        if self.mode == 'uart':
            return
        if self.mode != 'bb':
            super(UART, self).enter()
        self.write(0x03)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "ART1":
            self.mode = 'uart'
            self.bp_port = 0b00         # two bit port
            self.bp_config = 0b0000
            self.recurse_end()
            return
        self.recurse_flush(self.enter)
        raise BPError('Could not enter UART mode')

    @property
    def modestring(self):
        """ Return mode version string """
        self.write(0x01)
        self.timeout(self.minDelay * 10)
        return self.response(4)

    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, mode):
        if mode is True:
            self.write(0x03)
        else:
            self.write(0x02)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not set echo mode")
        self._echo = mode

    def manual_speed_cfg(self, baud):
        """ Manual baud rate configuration, send 2 bytes

        Configures the UART using custom baud rate generator settings. This command is followed by two data bytes that
        represent the BRG register value. Send the high 8 bits first, then the low 8 bits.

        Use the UART manual [PDF] or an online calculator to find the correct value (key values: fosc 32mHz,
        clock divider = 2, BRGH=1) . Bus Pirate responds 0x01 to each byte. Settings take effect immediately.
        """
        BRG = (FOSC // (4 * baud)) - 1
        BRGH = ((BRG >> 8) & 0xFF)
        BRGL = (BRG & 0xFF)
        self.write(0x03)
        self.write(BRGH)
        self.write(BRGL)
        self.timeout(0.1)
        return self.response()

    def begin_input(self):
        self.write(0x04)

    def end_input(self):
        self.write(0x05)

    def enter_bridge_mode(self):
        """ UART bridge mode (reset to exit)

        Starts a transparent UART bridge using the current configuration. Unplug the Bus Pirate to exit.
        """
        self.write(0x0f)
        self.timeout(0.1)
        self.response(1, binary=True)

    def set_cfg(self, cfg):
        self.write(0xC0 | cfg)
        self.timeout(0.1)
        return self.response(1, binary=True)

    def read_cfg(self):
        self.write(0xd0)
        self.timeout(0.1)
        return self.response(1, binary=True)
