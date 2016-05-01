#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example of SPI data transfer

from pyBusPirateLite.SPI import SPI, CFG_PUSH_PULL, CFG_IDLE
from pyBusPirateLite.BBIO_base import PIN_POWER, PIN_CS

spi = SPI()
spi.outputs = PIN_POWER | PIN_CS
spi.state = PIN_POWER | PIN_CS
spi.config = CFG_PUSH_PULL | CFG_IDLE
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer( [0x82, 0x00])
spi.cs = False

print(ord(data[2]))
