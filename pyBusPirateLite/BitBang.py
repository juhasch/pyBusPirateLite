#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Sean Nelson on 2009-10-14.
Copyright 2009 Sean Nelson <audiohacked@gmail.com>

Overhauled and edited by Garrett Berg on 2011- 1 - 22
Copyright 2011 Garrett Berg <cloudform511@gmail.com>

pyBusPirate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBusPirate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.
"""

import serial

from .BBIO_base import BBIO_base, BPError, ProtocolError, translator

class BitBang(BBIO_base):
    def set_pwm_frequency(self, frequency, DutyCycle=.5):
        """set pwm frequency and duty cycle.  Stolen from http://codepad.org/qtYpZmIF"""
        if DutyCycle > 1:
            raise ValueError('Duty cycle should be between 0 and 1')
        Fosc = 32e6
        Tcy = 2.0 / Fosc
        PwmPeriod = 1.0 / frequency

        # find needed prescaler
        PrescalerList = {0:1, 1:8 , 2:64, 3:256}

        for n in range(4):
            Prescaler = PrescalerList[n]
            PRy = PwmPeriod * 1.0 / (Tcy * Prescaler)
            PRy = int(PRy - 1)
            OCR = int(PRy * DutyCycle)

            if PRy < (2 ** 16 - 1):
                break # valid value for PRy, keep values
        else:
            raise ValueError('frequency requested is invalid')

        if self.setup_PWM(prescaler = Prescaler, dutycycle = OCR, period = PRy):
            self.recurse_end()
            return 1
        return self.recurse(self.set_pwm_frequency, frequency, DutyCycle)

    def clear_pwm(self):
        self.check_mode('bb')
        self.write(0x13)
        self.timeout(self.minDelay * 10)
        if self.response(1, True) == 'x01':
            self.recurse_end()
            return 1
        return self.recurse(self.clear_pwm)

    def get_adc_voltage(self):
        """returns the voltage rather than a binary value.  Expect future
        versions to have error checking (need firmware upgrade)"""
        voltage = self.ADC_measure()
        voltage = (ord(voltage[0]) << 8) + ord(voltage[1])
        voltage = (voltage * 6.6) / 1024
        return voltage

    def start_getting_adc_voltages(self):
        """start continuously getting adc voltages.  use memberfunction enter_bb to exit,
        use get_next_adc_voltage to get the next one."""
        self.check_mode('bb')
        self.write(0x15)
        self.timeout(self.minDelay)
        self.mode = 'adc'
        voltage = self.response(2, True)
        voltage = (ord(voltage[0]) << 8) + ord(voltage[1])
        voltage = (voltage * 6.6) / 1024
        return voltage

    def get_next_adc_voltage(self):
        self.check_mode('adc')
        voltage = self.response(2, True)
        voltage = (ord(voltage[0]) << 8) + ord(voltage[1])

        temp_voltage = voltage

        #voltage = (ord(voltage[0]) << 8) + ord(voltage[1])
        voltage = (voltage * 6.6) / 1024

        if voltage < 10:
            """sometimes the input gets out of sync.  This is the best error checking
            currently available, firmware will probably be updated to expect a 101 or
            something in the top byte, which will be better error checking"""
            self.recurse_end()
            return voltage

        self.response(1)        # get an additional byte and then flush
        self.port.flushInput()
        return self.recurse(self.get_next_adc_voltage)

    def stop_getting_adc_voltages(self):
        """I was encountering problems resetting out of adc mode, so I wrote this
        little function"""
        self.check_mode('adc')
        self.port.flushInput()
        for i in range(5):
            self.write(0x00)
            #r, w, e = select.select([self.port], [], [], 0.01);
            r = self.response(1, True)
            if (r): break;
        self.port.flushInput()
        self.enter_bb()
        return 1

    """ Higher level functions.  Allows control of the BP port as if it were a microcontroller"""
    def set_port(self, byte):
        """sets the port bits as determined by the translator (self.t)."""
        self.check_mode('bb')
        self.bp_port = byte & 0x1F

        if ord(self.set_pins_bb(translator(self.bp_config  # check config bits too
            | self.bp_port, self.t))) & 0b11100000 == 0x80 | self.bp_config:
            self.recurse_end()
            return 1
        return self.recurse(self.set_port, byte)

    def read_port(self):
        """reads the port.  Will return a number (as opposed to a string).  Returns None
        if there is an error"""
        self.check_mode(['bb'])
        out = ord(self.set_pins_bb(translator(self.bp_config | self.bp_port, self.t)))

        if out & 0b11100000 == 0x80 | self.bp_config:   #check config bits too
            self.recurse_end()
            return translator(0x1F & out, self.t)
        return self.recurse(self.read_port)

    def read_pin(self, pin):
        """Gets the data at the pin.  Only works in bit bang mode"""
        self.check_mode('bb')
        pin = pin.upper()
        out = self.read_port()
        if out is None: return None
        out = translator(pinout_bb[pin], self.t) & out
        return bool(out)

    def set_dir(self, pins):
        """sets pins as either input (1) or output (0).  Only for bb mode """
        self.check_mode('bb')
        self.bp_dir = pins & 0x1F   # filter

        if ord(self.cfg_pins(translator(self.bp_dir, self.t))) & 0b11100000 == 0b01000000:
            self.recurse_end()
            return 1
        return self.recurse(self.set_dir, pins)

    def set_pin_dir(self, pin, direction):
        """sets the pin direction.  Only works in bit bang mode"""
        self.check_mode('bb')
        pin = pin.upper()
        if direction is ('out' or 'Out' or 'OUT' or 0):
            self.bp_dir &= ~translator(pinout_bb[pin], self.t)
        elif direction is ('in' or 'In' or 'IN' or 1):
            self.bp_dir |= translator(0x1F & pinout_bb[pin], self.t)
        else:
            raise ValueError('incorrect value for direction')
        return self.set_dir(self.bp_dir)

