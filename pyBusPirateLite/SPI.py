#!/usr/bin/env python
# encoding: utf-8
"""
Created by Sean Nelson on 2009-10-14.
Copyright 2009 Sean Nelson <audiohacked@gmail.com>

Overhauled and edited by Garrett Berg on 2011- 1 - 22
Copyright 2011 Garrett Berg <cloudform511@gmail.com>

This file is part of pyBusPirate.

pyBusPirate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBusPirate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.
"""

from .BitBang import BBIO


class SPISpeed:
    _30KHZ = 0b000
    _125KHZ = 0b001
    _250KHZ = 0b010
    _1MHZ = 0b011
    _2MHZ = 0b100
    _2_6MHZ = 0b101
    _4MHZ = 0b110
    _8MHZ = 0b111


class SPICfg:
    OUT_TYPE = 0x8
    IDLE = 0x4
    CLK_EDGE = 0x2
    SAMPLE = 0x1


class SPIOutType:
    HIZ = 0
    _3V3 = 1

class SPI(BBIO):
    def cfg_spi(self, spi_cfg):
        """ Set SPI configuration
        :param spi_cfg: Values defined in SPICfg
        """
        self.check_mode('spi')
        self.write(0x80 | spi_cfg)
        self.timeout(0.1)
        resp = self.response(1, True)
        if resp != '\x01':
            raise ValueError("Could not set SPI configuration", resp)

    def read_spi_cfg(self):
        """ Read SPI configuration
        :return: Values defined in SPICfg
        """
        self.check_mode('spi')
        self.write(0x90)
        self.timeout(0.1)
        return self.response(1, True)

    def transfer(self, txdata):
        """ Transfer data to/from SPI
        :param txdata: List of data to send
        :return: List of recieved data
        """
        self.check_mode('spi')
        length = len(txdata)
        self.write(0x10 + length-1)
        for data in txdata:
            self.write(data)
        return self.response(length+1, True)

    def cs_low(self):
        self.write(0x02)
        return self.response(1)

    def cs_high(self):
        self.write(0x03)
        return self.response(1)
