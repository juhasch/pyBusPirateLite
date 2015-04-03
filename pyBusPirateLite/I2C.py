#!/usr/bin/env python
# encoding: utf-8
"""
Created by Sean Nelson on 2009-10-14.
Copyright 2009 Sean Nelson <audiohacked@gmail.com>

Overhauled and edited by Garrett Berg on 2011- 1 - 22
Copyright 2011 Garrett Berg <cloudform511@gmail.com>

This file is part of pyBusPirate.

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
try:
   from .BitBang import BBIO
except ValueError:
   from BitBang import BBIO

class I2CSpeed:
   _400KHZ = 0x03
   _100KHZ = 0x02
   _50KHZ = 0x01
   _5KHZ = 0x00

class I2CPins:
   POWER = 0x8
   PULLUPS = 0x4
   AUX = 0x2
   CS = 0x1

pin_mapping = {'AUX':   0b10,
              'CS':     0b01 }

class I2C(BBIO):
   def send_ack(self):
      self.check_mode('i2c')
      self.port.write("\x06")
      #self.timeout(0.1)
      return self.response()

   def send_nack(self):
      self.check_mode('i2c')
      self.port.write("\x07")
      #self.timeout(0.1)
      return self.response()

