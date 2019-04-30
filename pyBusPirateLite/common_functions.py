#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from .I2C import I2C


def init_i2c(bp_device, power=True, pullups=True, speed=I2C.SPEEDS['50kHz']):
    """initializes i2c mode with some common settings hardwired

    Parameters
    ----------
    bp_device
        Bus pirate device
    power : bool
        Turn on power
    pullups : bool
        Turn on pullups
    speed: IC2.I2CSpeed
        Transfer speed

    Returns
    -------
    bool
        True if device could be initialized
    """
    if not bp_device.enter_I2C():
        return False
    if not bp_device.configure_peripherals(power, pullups):
        return False
    if not bp_device.set_speed(speed):
        return False
    bp_device.timeout(0.1)
    return True


def init_bb(bp_device, power='on', pullups='on'):
    """initializes bit bang mode with the most common settings

    Parameters

    """
    if not bp_device.enter_bb():
        return None
    if not bp_device.configure_peripherals(power, pullups):
        return None
    bp_device.timeout(0.1)
    return 1


def i2c_write_data(bp_device, data):
    """send data, first byte should be address.  NOTE: Address must include the write bit
    Created by Peter Huewe peterhuewe@gmx.de"""
    bp_device.send_start_bit()
    ack_signals = bp_device.bulk_trans(len(data), data)
    bp_device.send_stop_bit()

    ack_signals = list(ack_signals)
    for n in range(len(ack_signals)):
        ack_signals[int(n)] = ord(ack_signals[int(n)])

    return ack_signals


def sniff_i2c_devices(bp_device, power=False):
    init_i2c(bp_device, power)
    working_addr = []
    for n in range(128):
        bp_device.send_start_bit()
        ack_sig = list(bp_device.bulk_trans(1, [n << 1]))
        bp_device.send_stop_bit()

        for p in range(len(ack_sig)):
            ack_sig[p] = ord(ack_sig[p])
         
        if 0 in ack_sig:
            working_addr += [n]
    return working_addr
