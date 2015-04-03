# -*- coding: utf-8 -*-

from pyBusPirateLite.SPI import *

spi = SPI('COM3', 115200)
spi.BBmode()
spi.enter_SPI()
spi.cfg_pins(PinCfg.POWER | PinCfg.CS )
spi.cfg_spi( 0x0c )
spi.set_speed(SPISpeed._1MHZ)

register = 0
spi.CS_Low()
spi.port.write(bytes([0x11]))
spi.port.write(bytes([0x80]))
spi.port.write(bytes([0x00]))
spi.CS_High()
data = spi.response(2, True)

print(data[1])

spi.reset()



