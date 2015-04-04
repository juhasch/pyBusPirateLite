#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
 * Summary :
 * 
 * Created on Jan 26, 2011
 * @author: garrett
"""

import select
import serial
from time import sleep

class PinCfg:
    POWER = 0x8
    PULLUPS = 0x4
    AUX = 0x2
    CS = 0x1


class BBIOPins:
    # Bits are assigned as such:
    MOSI = 0x01
    CLK = 0x02
    MISO = 0x04
    CS = 0x08
    AUX = 0x10
    PULLUP = 0x20
    POWER = 0x40


class BBIOModes:
    # modes are assigned as such.  Use either the strings or this class in your
    # code
    I2C = 'i2c'
    UART = 'uart'
    SPI = 'spi'
    _1WIRE = '1wire'
    RAW = 'raw'
    BB = 'bb'
    ADC = 'adc'

all_modes = ['i2c', 'uart', 'spi', '1wire', 'raw', 'bb']
all_modes_and_special = ['i2c', 'uart', 'spi', '1wire', 'raw', 'bb', 'adc']
not_bb = ['i2c', 'uart', 'spi', '1wire', 'raw']


class BBIO_base:
    """functions used in every mode, the base of class.  Most of these you can
    probably ignore, as they are just used in the other member classes
    Note: Also contains some of the older functions that are now probably outdated
    """
    def __init__(self):
        self.minDelay = 1 / 115200
        self.mode = None

    def resetBP(self):
        self.reset()
        self.write(0x0f)
        self.timeout(.1)
        self.port.flushInput()
        self.mode = None

    def check_mode(self, chkmode):
        if self.mode not in chkmode:
            raise ValueError('attempt to run {0} protocol when the bus pirate is not in {0} mode'.format(chkmode))
        return 1

    def timeout(self, timeout = 0.1):
        sleep(timeout)

    def write(self, byte):
        self.port.write(bytes([byte]))
        
    def response(self, byte_count = 1, return_data = False):
        """request a number of bytes and whether you want the data itself.  If it receives a
        '1' then it returns a 1 ('1' is the std bus pirate response for most functions)"""
        data = self.port.read(byte_count)
        if byte_count == 1 and return_data == False:
            if data == 0x01:
                return 1
            else:
                return None
        else:
            return data.decode()

    def cfg_pins(self, pins=0):
        """used in every mode to configure pins.  In bb it configures as either input or output,
        in the other modes it normally configures peripherals such as power supply and the aux pin"""
        self.check_mode(all_modes)
        self.write(0x40 | pins)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    def set_pins_bb(self, pins):
        """same as raw_set_pins, except it returns the value it obtains.
        Necessary to read values in bb mode.  Can be used instead of
        the raw one if you want to know the output"""
        self.check_mode(all_modes_and_special)
        self.write(0x80 | pins)
        self.timeout(self.minDelay)
        return self.response(1, True)

    _attempts_ = 0
    def recurse_end(self):
        self._attempts_ = 0

    def recurse(self, function, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            return function(*args)
        raise IOError('bus pirate malfunctioning')

    def recurse_flush(self, function, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            for n in range(5):
                self.write(0x00)
            self.port.flushInput()
            return function(*args)
        raise IOError('bus pirate malfunctioning')

    # Self Tests
    def short_selftest(self):
        self.check_mode('bb')
        self.write(0x10)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    def long_selftest(self):
        self.check_mode('bb')
        self.write(0x11)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)


    # PWM control
    def setup_PWM(self, prescaler, dutycycle, period):
        self.check_mode('bb')
        self.write(0x12)
        self.write(prescaler)
        self.write((dutycycle >> 8) & 0xFF)
        self.write(dutycycle & 0xFF)
        self.write((period >> 8) & 0xFF)
        self.write(period & 0xFF)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    # ADC control
    def ADC_measure(self):
        self.check_mode('bb')
        self.write(0x14)
        self.timeout(self.minDelay)
        return self.response(2, True)

    def mode_string(self):
        self.write(0x01)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    """unused legacy code or code I'm not so sure of..."""
    def raw_set_pins(self, pins):
        """kept in for legacy purposes, but not used or recomended"""
        self.check_mode('raw')
        self.write(0x80 | pins)
        self.timeout(self.minDelay)
        return self.response(1)

    def raw_cfg_pins(self, config):
        """practically identical to cfg_pins except it returns a different value"""
        self.write(0x40 | config)
        self.timeout(self.minDelay * 10)
        return self.response(1)

    def read_pins(self):
        """I'm not sure what this is used for.  I can't find reference to the command 0x50"""
        self.write(0x50)
        self.timeout(self.minDelay)
        return self.response(1, True)

    def read_speed(self):
        """I don't see reference to this in the documentation, but it was in the old pyBusPirateLite
        so I'm leaving it in."""
        self.write(0x70)
        select.select(None, None, None, 0.1)
        return self.response(1, True)

    def reset(self):
        """I would recommend not using this.  Use enter_bb instead.  Kept and NOT UPDTADED
        if people are using old code they should probably change their code :D"""
        self.write(0x00)
        self.timeout(self.minDelay * 10)
        self.mode = 'bb'

    # These commands are very strange, because you can also influence the cs
    # pin through the configuration register.  Additional testing needed.
    # These commands MAY OR MAY NOT BE SUPPORTED.
    # They should keep track of everything though, so please
    # test these and report if they work! (also test set_pin('cs') :D
    def cs_low(self):
        self.check_mode(['raw', 'spi'])
        self.bp_port &= ~0b01
        self.write(0x04)
        self.timeout(0.1)
        return self.response(1)

    def cs_high(self):
        self.check_mode(['raw', 'spi'])
        self.bp_port |= 0b01
        self.write(0x05)
        self.timeout(0.1)
        return self.response(1)
