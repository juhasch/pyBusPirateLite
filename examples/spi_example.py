#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example of SPI data transfer

from pyBusPirateLite.SPI import *
from pyBusPirateLite.BBIO_base import PinCfg

spi = SPI()
spi.connect('COM3')
spi.enter_bb()
spi.enter_spi()

spi.cfg_pins(PinCfg.POWER | PinCfg.CS )
spi.cfg_spi( 0x0c )
spi.set_speed(SPISpeed._1MHZ)

# send two bytes and receive answer
spi.cs_low()
data = spi.transfer( [0x82, 0x00])
spi.cs_high()

print(ord(data[2]))

spi.reset()
spi.port.close()
