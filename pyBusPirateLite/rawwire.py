#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

# See http://dangerousprototypes.com/blog/2009/10/27/binary-raw-wire-mode/

from .base import BusPirate


def bchar(char):
    return bytearray([char])


class RawWireCfg:
    NA = 0x01
    LSB = 0x02
    _3WIRE = 0x04
    OUTPUT = 0x08


class RawWire(BusPirate):
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
        >>> from pyBusPirateLite.rawwire import RawWire
        >>> raw = RawWire()
        """
        super().__init__(portname, speed, timeout, connect)

    def enter(self):
        """Enter raw wire mode

        Raw-wire binary mode provides access to the Bus Pirate's raw 2- and 3-wire libraries.
        This new mode will make it easier to script operations on arbitrary serial protocols
        used by devices like smart cards, shift registers, etc.
        """
        if self.mode == 'raw':
            return
        if self.mode != 'bb':
           super(RawWire, self).enter()

        self.write(0x05)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "RAW1":
            self.mode = 'raw'
            self.bp_port = 0b00  # two bit port
            self.bp_config = 0b0000
            self.recurse_end()
            return 1
        return self.recurse_flush(self.enter_rawwire)

    def start_bit(self):
        """is kept in because it was in for legacy code,
        I recommend you use send_start_bit"""
        self.port.write(bchar(0x02))
        self.timeout(0.1)
        return self.response(1)

    def stop_bit(self):
        """is kept in because it was in for legacy code,
        I recommend you use send_stop_bit"""
        self.port.write(bchar(0x03))
        self.timeout(0.1)
        return self.response(1)

    def cs_low(self):
        self.port.write(bchar(0x04))
        self.timeout(0.1)
        return self.response(1)

    def cs_high(self):
        self.port.write(bchar(0x05))
        self.timeout(0.1)
        return self.response(1)

    def read_byte(self):
        self.port.write(bchar(0x06))
        self.timeout(0.1)
        return self.response(1, True)

    def read_bit(self):
        self.port.write(bchar(0x07))
        self.timeout(0.1)
        return self.response(1, False)

    def peek(self):
        self.port.write(bchar(0x08))
        self.timeout(0.1)
        return self.response(1)

    def clock_tick(self):
        self.port.write(bchar(0x09))
        self.timeout(0.1)
        return self.response(1)

    def clock_low(self):
        self.port.write(bchar(0x0a))
        self.timeout(0.1)
        return self.response(1)

    def clock_high(self):
        self.port.write(bchar(0x0b))
        self.timeout(0.1)
        return self.response(1)

    def data_low(self):
        self.port.write(bchar(0x0c))
        self.timeout(0.1)
        return self.response(1)

    def data_high(self):
        self.port.write(bchar(0x0d))
        self.timeout(0.1)
        return self.response(1)

    # NOTE: Untested. Not clear if it returns 0x01 for each bit or byte,
    # it looks like there are some typos in the documentation.
    def bulk_bits(self, byte, n_bits):
        if n_bits < 1 or n_bits > 8:
            raise ValueError('Can only send 1 through 8 bits')
        if type(byte) is str:
            byte = ord(byte[0])
        byte_val = byte >> (8 - n_bits)
        self.port.write(bchar(0b00110000 | (n_bits - 1)))
        self.port.write(bchar(byte_val))
        self.timeout(0.1)
        return self.response(1)

    def wire_cfg(self, pins = 0):
        """1000wxyz – Config, w=HiZ/3.3v, x=2/3wire, y=msb/lsb, z=not used"""
        self.port.write(bchar(0x80 | pins))
        self.timeout(0.1)
        return self.response(1)

    def peripherals_cfg(self, flags=0):
        """0100wxyz – Configure peripherals w=power, x=pullups, y=AUX, z=CS"""
        self.port.write(bchar(0b01000000 | flags))
        self.timeout(0.1)
        return self.response(1)

    def speed_cfg(self, speed=0):
        """011000xx – Set speed, 3=~400kHz, 2=~100kHz, 1=~50kHz, 0=~5kHz"""
        self.port.write(bchar(0b1100000 | speed))
        self.timeout(0.1)
        return self.response(1)

    # if someone who cares could write a more user-friendly wire_cfg that would be cool
    # (make it similar to my configure_peripherals)

    def bulk_clock_ticks(self, ticks = 1):
        self.port.write(bchar(0x20 | (ticks - 1)))
        self.timeout(0.1)
        return self.response(1)
