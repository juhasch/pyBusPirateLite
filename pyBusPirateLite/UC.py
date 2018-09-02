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

from .BitBang import BitBang
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
    """This class brings together all of the modules under a single class, allowing you to switch
    to other modules, do a function, and then switch back transparently.  The class will keep track
    of where you are and raise an Error if you do something wrong.

    The variables bp_port, bp_dir, and bp_config store the values that it sees in each respective mode,
    and the variable mode stores which mode the bus pirate is in.

    IMPORTANT: Keep in mind that switching modes always makes the pins go to HiZ and the power supplies
    turn off.  This can suck for certain applications (like if you are manualy wiggling a clock
    or reset signal), but you can design around it with external pullups and external inverters.
    YOU HAVE TO RECONFIGURE ALL SETTINGS WHENEVER YOU SWITCH MODES.

    Note: current tested versions are only BBIO and I2C, but the other ones should work.  Go to
    ________________.com and post any errors, problems or helpful revisions so that the code
    can be updated
    """
    pass
