#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example of SPI data transfer

from pyBusPirateLite.SPI import SPI
from pyBusPirateLite.BBIO_base import PinCfg

spi = SPI()

spi.cfg_pins(PinCfg.POWER | PinCfg.CS )
spi.config = SPI_cfg['PUSH_PULL'] | SPI_cfg['IDLE']
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer( [0x82, 0x00])
spi.cs = False

print(ord(data[2]))
