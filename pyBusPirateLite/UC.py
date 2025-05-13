# Created by Garrett Berg on 2011-1-22
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

from typing import Type # Potentially useful for type hinting class types if UC evolves

from .BitBang import BitBang # Corrected import for BitBang
from .I2C import I2C
from .onewire import OneWire
from .rawwire import RawWire
from .SPI import SPI
from .UART import UART


"""
Some notes:
normal Values (sent to the uc) are mapped to AUX|MOSI|CLK|MISO|CS.
decoded values are mapped to AUX|CLK|MOSI|CS|MISO
The reason for doing this is to make it easier to 
deal with the standard cables.  If you have a different cable, you should set BBIO.t to False
in order to use normal data outputs.
"""


class UC(BitBang, I2C, OneWire, RawWire, SPI, UART):
    """A unified class for Bus Pirate, allowing transparent switching between protocols.

    This class inherits from all available protocol classes (BitBang, I2C, OneWire,
    RawWire, SPI, UART), making it possible to use a single object instance to
    access different Bus Pirate modes.

    To switch modes, simply call the `enter()` method of the desired protocol
    (e.g., `uc_instance.enter_spi()` to switch to SPI mode, which internally calls
    the `SPI.enter()` method after ensuring BitBang mode if necessary).

    The `self.mode` attribute (inherited from `BusPirate`) will reflect the
    current operational mode of the Bus Pirate (e.g., 'spi', 'i2c', 'bb').

    IMPORTANT:
    Switching modes typically resets the Bus Pirate's pins to a high-impedance (HiZ)
    state and may turn off power supplies (VCC, VPU). Any protocol-specific
    configurations (like speed, pin settings, pull-ups) MUST be reapplied
    after switching to a new mode. This is a hardware behavior of the Bus Pirate.

    Example:
    >>> from pyBusPirateLite.UC import UC
    >>> bp = UC(portname='/dev/ttyUSB0')
    >>> bp.enter_spi() # Enters SPI mode
    >>> bp.speed = '1MHz'
    >>> bp.pins = bp.PIN_POWER | bp.PIN_CS # Configure SPI pins
    >>> # ... perform SPI operations ...
    >>>
    >>> bp.enter_i2c() # Switches to I2C mode (pins/power reset by BP)
    >>> bp.speed = '100kHz'
    >>> bp.configure_peripherals(power=True, pullups=True) # Configure I2C
    >>> # ... perform I2C operations ...
    """
    pass
