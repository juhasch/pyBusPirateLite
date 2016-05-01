# pyBusPirateLite
Python library for BusPirate

Based on code from Garrett Berg <cloudform511@gmail.com>

http://dangerousprototypes.com/2011/03/14/new-version-of-pybuspiratelite-python-library/

-------------------------

This library has been significantly updated an modified. The main goal was to make it simpler to use
and more pythonic.

It automatically tries to find the right comport, connects to the bus pirate and is typically used only in
a given mode to avoid confusion.

Examples
--------

1. SPI

from pyBusPirateLite.SPI import SPI, CFG_PUSH_PULL, CFG_IDLE
from pyBusPirateLite.BBIO_base import PIN_POWER, PIN_CS

spi = SPI()
spi.cfg_pins = PIN_POWER | PIN_CS 
spi.config = CFG_PUSH_PULL | CFG_IDLE
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer( [0x82, 0x00])
spi.cs = False

print(ord(data[2]))

2. I2C

from pyBusPirateLite.SPI import I2C
from pyBusPirateLite.BBIO_base import PIN_POWER, PIN_CS

i2c = I2C()
i2c.cfg_pins = PIN_POWER | PIN_CS 
i2c.speed = '50kHz'
