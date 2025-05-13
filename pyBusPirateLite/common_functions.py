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

from typing import List, Optional
from .I2C import I2C
from .base import BusPirate


def init_i2c(bp_device: I2C, power: bool = True, pullups: bool = True, speed: int = I2C.SPEEDS['50kHz']) -> bool:
    """Initializes I2C mode with some common settings hardwired.

    Parameters
    ----------
    bp_device : I2C
        Bus Pirate device instance configured for I2C.
    power : bool, optional
        Turn on power supplies (default is True).
    pullups : bool, optional
        Turn on on-board pull-up resistors (default is True).
    speed : int, optional
        I2C clock speed. Use values from `I2C.SPEEDS` (e.g., `I2C.SPEEDS['50kHz']`).

    Returns
    -------
    bool
        True if device could be initialized successfully, False otherwise.
    """
    if not bp_device.enter():  # Use I2C.enter()
        return False
    # configure_peripherals is inherited from BusPirate
    if not bp_device.configure_peripherals(power=power, pullups=pullups):
        return False
    bp_device.speed = speed  # Use I2C.speed property setter
    bp_device.timeout(0.1)  # BusPirate.timeout(time) method
    return True


def init_bb(bp_device: BusPirate, power: str = 'on', pullups: str = 'on') -> bool:
    """Initializes BitBang mode with the most common settings.

    Parameters
    ----------
    bp_device : BusPirate
        Bus Pirate device instance.
    power : str, optional
        Controls power supplies. Use 'on' or 'off' (case-insensitive, default is 'on').
    pullups : str, optional
        Controls on-board pull-up resistors. Use 'on' or 'off' (case-insensitive, default is 'on').

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    if not bp_device.enter_bb():
        return False  # Changed from return None

    power_bool = True if power.lower() == 'on' else False
    pullups_bool = True if pullups.lower() == 'on' else False

    if not bp_device.configure_peripherals(power=power_bool, pullups=pullups_bool):
        return False  # Changed from return None
    bp_device.timeout(0.1)
    return True  # Changed from return 1


def i2c_write_data(bp_device: I2C, data: List[int]) -> List[int]:
    """Send data over I2C. First byte should be the address with the R/W bit.

    NOTE: Address must include the write bit.
    Created by Peter Huewe peterhuewe@gmx.de

    Parameters
    ----------
    bp_device : I2C
        Bus Pirate device instance configured for I2C.
    data : List[int]
        List of bytes to send. The first byte is the I2C address (with R/W bit).

    Returns
    -------
    List[int]
        A list of acknowledgment signals (0 for ACK, non-zero for NACK, typically 1) 
        from the slave device, converted to integers. Each element corresponds to a 
        byte in `data`.
    """
    bp_device.start()  # Use I2C.start()
    # bulk_trans is inherited from BusPirate, takes (byte_count, byte_string), returns bytes
    raw_ack_signals: bytes = bp_device.bulk_trans(len(data), data)
    bp_device.stop()  # Use I2C.stop()

    # Iterating over a bytes object in Python 3 yields integers
    ack_signals: List[int] = [s for s in raw_ack_signals]
    return ack_signals


def sniff_i2c_devices(bp_device: I2C, power: bool = False) -> List[int]:
    """Scans for I2C devices and returns a list of detected 7-bit addresses.

    Parameters
    ----------
    bp_device : I2C
        Bus Pirate device instance configured for I2C.
    power : bool, optional
        Turn on power supplies before sniffing (default is False).
        Pull-ups are automatically enabled during initialization.

    Returns
    -------
    List[int]
        A list of 7-bit I2C addresses that responded with an ACK (value 0).
    """
    init_i2c(bp_device, power=power, pullups=True)  # Ensure pullups are enabled for sniffing
    working_addr: List[int] = []
    for n in range(128):  # Iterate over all possible 7-bit I2C addresses
        bp_device.start()  # Use I2C.start()
        # The address `n` is shifted left (n << 1) to form the 8-bit address byte.
        # The LSB (R/W bit) is 0, indicating a write operation (which is how addresses are pinged).
        # bulk_trans(1, [n << 1]) sends this single address byte.
        # It returns a bytes object (typically one byte) containing the ACK/NACK status.
        raw_ack_sig: bytes = bp_device.bulk_trans(1, [n << 1])
        bp_device.stop()  # Use I2C.stop()

        # An ACK is represented by the value 0.
        # Check if raw_ack_sig is not empty and its first byte is 0.
        if raw_ack_sig and raw_ack_sig[0] == 0:
            working_addr.append(n)
    return working_addr
