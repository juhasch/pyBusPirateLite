#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example of SPI data transfer

from pyBusPirateLite.SPI import *

spi = SPI()
spi.pins = PIN_POWER | PIN_CS
spi.config = CFG_PUSH_PULL
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer([0x82, 0x55])
spi.cs = False
spi.pins = PIN_CS # turn off power
