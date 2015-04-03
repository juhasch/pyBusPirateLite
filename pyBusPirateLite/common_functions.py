#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Garrett Berg on 2011-1-22
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
   from . import I2C
   from . import BitBang
   from . import UC
except ValueError:
   import I2C
   import BitBang
   import UC
import sys

if __name__ == '__main__':
   import time


def init_i2c(bp_device, power = 'on', pullups = 'on', speed = I2C.I2CSpeed._50KHZ):
   '''initializes i2c mode with some common settings hardwired'''
   if not bp_device.enter_I2C():
      return None
   if not bp_device.configure_peripherals(power, pullups):
      return None
   if not bp_device.set_speed(speed):
      return None
   bp_device.timeout(0.1)
   return 1

def init_bb(bp_device, power = 'on', pullups = 'on'):
   '''initializes bit bang mode with the most common settings'''
   if not bp_device.enter_bb():
      return None
   if not bp_device.configure_peripherals(power, pullups):
      return None
   bp_device.timeout(0.1)
   return 1

def i2c_write_data(bp_device, data):
   '''send data, first byte should be address.  NOTE: Address must include the write bit
   Created by Peter Huewe peterhuewe@gmx.de'''
   bp_device.send_start_bit()
   ack_signals = bp_device.bulk_trans(len(data), data)
   bp_device.send_stop_bit()

   ack_signals = list(ack_signals)
   for n in range(len(ack_signals)):
      ack_signals[int(n)] = ord(ack_signals[int(n)])

   return ack_signals


def sniff_i2c_devices(bp_device, power = 'off'):
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
   
   print working_addr
   return working_addr
   
def init_bus_pirate(mode = 'uc', timeout = None, port = None):
   '''connects the bus pirate over a range of possible ports and returns its object'''
   if mode is 'uc':
      bp_device = UC.UC()

   if mode is 'bb':
      bp_device = BitBang.BBIO()

   if mode is 'i2c':
      bp_device = I2C.I2C()
   #add your own if you want.  I mostly just use the uc one

   if port is None:
      if sys.platform == 'win32':
         if not bp_device.connect(4, 115200, timeout):   # 4 connects to port 5 on my computer.  This may not work for you.
            return None

      elif sys.platform == 'linux2':
         for n in range(4):
            if bp_device.connect("/dev/ttyUSB" + str(n), 115200, timeout):
               break
         else:
            return None
   else:
      if not bp_device.connect(port, 115200, timeout):
         return None

   bp_device.enter_bb()

   return bp_device


if __name__ == '__main__':

   def speed_test_pin(bp_device):
      '''a simple speed test I've been using to see how fast the bp can communicate.'''
      bp_device.enter_bb()
      bp_device.configure_peripherals('on', 'on')
      bp_device.set_dir(0b11100) #lower two pins output
      bp_device.set_port(0)

      periods = []
      for i in range(500):
         periods.append(time.time())
         bp_device.set_port(0b1)
         bp_device.set_port(0b0)
         periods[-1] = time.time() - periods[-1]
      print ' periods: /n', str(periods)
      print '\n\n\n frequency of data is : /n', [2.0 / n for n in periods] #sent two commands so two times

   def speed_test_adc(bp_device):
      bp_device.enter_bb()
      bp_device.configure_peripherals('on', 'on')
      voltages = [bp_device.special_start_getting_adc_voltages() ]
      periods = [1]
      print 'got here'
      for n in range (50):
         periods.append(time.time())
         #voltages.append(bp_device.get_adc_voltage())
         voltages.append(bp_device.special_get_next_adc_voltage())
         periods[-1] = time.time() - periods[-1]
      print 'all periods /n', periods
      print '\n\n\nall voltages'
      print voltages
      print '\n\n frequency of data \n', [1.0 / n for n in periods]


if __name__ == '__main__':
   bp_device = init_bus_pirate()
   #speed_test_pin(bp_device)
   speed_test_adc(bp_device)
