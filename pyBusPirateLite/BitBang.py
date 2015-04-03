#!/usr/bin/env python
# encoding: utf-8
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

import select
import serial
import sys

try:
   from .BBIO_base import *
except ValueError:
   from BBIO_base import *

"""
PICSPEED = 24MHZ / 16MIPS
"""

'''pinout_uc prior to translating be careful, you have to translate this
when you use it!!! (only wory about this if you are developing code for the editing
this class)'''
pinout_bb = {'AUX':     0b10000,
             'MOSI':    0b01000,
             'CLK':     0b00100,
             'MISO':    0b00010,
             'CS':      0b00001}



def translator(byte, translate):
   '''translates a byte so that the pinout is more user friendly (for the standard connector
   orientation)'''
   if translate == True:
      '''maps AUX|MOSI|CLK|MISO|CS to AUX|CLK|MOSI|CS|MISO'''
      if byte > 255: raise ValueError('Value Too Large')
      return (byte & 0b11110000) | ((byte & 0b0101) << 1) | ((byte & 0b1010) >> 1)
   else:
      return byte

'''if transltor (self.t) is True then pinout is AUX|CLK|MOSI|CS|MISO
   if translator is False then:                 AUX|MOSI|CLK|MISO|CS
   The first is much more user friendly, the second is the order the 
   bus pirate uses (and expects)
   the values in self.uc_port and self.uc_dir are the values you **want**,
   i.e. if you have translate on then they will read AUX|CLK|MOSI|CS|MISO
'''
class BBIO(BBIO_base):
   def __init__(self):
      # MAJOR CHANGE: If you are re-using old code,
      # you must nowconnect to device by calling 
      # the connect() function below.  There is no automatic connection
      self.connected = False
      self.mode = None
      self.t = True

   def connect(self, p = "/dev/bus_pirate", s = 115200, t_out = 1):
      ''' will try to automatically find a port regarless of os (to be added)'''
      try:
         self.port = serial.Serial(p, s, timeout = t_out)
      except serial.serialutil.SerialException:
         return 0
      self.connected = True
      self.minDelay = 1 / s
      return 1

   _attempts_ = 0   # global stored for use in enter_bb
   def enter_bb(self):
      '''this is the be-all-end-all restart function.  It will keep trying
      to get the bus pirate into bit bang mode even if it is stuck.  Call this
      to get the bus pirate into a known state (bb mode)'''
      if self.connected is not True:
         return 0 # still need to connect to port
      self.port.flushInput()
      for i in range(20):
         self.port.write("\x00")
         #r, w, e = select.select([self.port], [], [], 0.01)
         r = self.response(1, True)
         if (r): break
      self.port.flushInput()
      self.port.write('\x00')
      if self.response(5, True) == "BBIO1":
         self.mode = 'bb'
         self.bp_config = 0x00      # configuration bits determine action of power sources and pullups
         self.bp_port = 0x00        # out_port similar to ports in microcontrollers
         self.bp_dir = 0x1F         # direction port similar to microchip microcontrollers.  (1) is input, (0) is output
         self.recurse_end()
         return 1
      return self.recurse_flush(self.enter_bb)

   '''calls to be used only in bit bang mode'''
   def enter_spi(self):
      self.check_mode('bb')
      self.port.write("\x01")
      self.timeout(self.minDelay * 10)
      if self.response(4) == "SPI1":
         self.mode = 'spi'
         self.bp_port = 0b00         # two bit port
         self.bp_config = 0b0000
         self.recurse_end()
         return 1
      return self.recurse_flush(self.enter_spi)

   def enter_i2c(self):
      self.check_mode('bb')
      self.port.write("\x02")
      self.timeout(self.minDelay * 10)
      if self.response(4) == "I2C1":
         self.mode = 'i2c'
         self.bp_port = 0b00         # two bit port
         self.bp_config = 0b0000
         self.recurse_end()
         return 1
      return self.recurse_flush(self.enter_i2c)

   def enter_uart(self):
      self.check_mode('bb')
      self.port.write("\x03")
      self.timeout(self.minDelay * 10)
      if self.response(4) == "ART1":
         self.mode = 'uart'
         self.bp_port = 0b00         # two bit port
         self.bp_config = 0b0000
         self.recurse_end()
         return 1
      return self.recurse_flush(self.enter_uart)

   def enter_1wire(self):
      self.check_mode('bb')
      self.port.write("\x04")
      self.timeout(self.minDelay * 10)
      if self.response(4) == "1W01":
         self.mode = '1wire'
         self.bp_port = 0b00         # two bit port
         self.bp_config = 0b0000
         self._attempts_ = 1
         return 1
      return self.recurse_flush(self.enter_1wire)

   def enter_rawwire(self):
      self.check_mode('bb')
      self.port.write("\x05")
      self.timeout(self.minDelay * 10)
      if self.response(4) == "RAW1":
         self.mode = 'raw'
         self.bp_port = 0b00         # two bit port
         self.bp_config = 0b0000
         self.recurse_end()
         return 1
      return self.recurse_flush(self.enter_rawwire)

   def set_pwm_frequency(self, frequency, DutyCycle = .5):
      '''set pwm frequency and duty cycle.  Stolen from http://codepad.org/qtYpZmIF'''
      if DutyCycle > 1: raise ValueError('Duty cycle should be between 0 and 1')
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

         if PRy < (2 ** 16 - 1): break # valid value for PRy, keep values
      else: raise ValueError('frequency requested is invalid')

      if self.setup_PWM(prescaler = Prescaler, dutycycle = OCR, period = PRy):
         self.recurse_end()
         return 1
      return self.recurse(self.set_pwm_frequency, frequency, DutyCycle)

   def clear_pwm(self):
      self.check_mode('bb')
      self.port.write("\x13")
      self.timeout(self.minDelay * 10)
      if self.response() == 1:
         self.recurse_end()
         return 1
      return self.recurse(self.clear_pwm)

   def get_adc_voltage(self):
      '''returns the voltage rather than a binary value.  Expect future
      versions to have error checking (need firmware upgrade)'''
      voltage = self.ADC_measure()
      voltage = (ord(voltage[0]) << 8) + ord(voltage[1])
      voltage = (voltage * 6.6) / 1024
      return voltage

   def start_getting_adc_voltages(self):
      '''start continuously getting adc voltages.  use memberfunction enter_bb to exit,
      use get_next_adc_voltage to get the next one.'''
      self.check_mode('bb')
      self.port.write("\x15")
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
         '''sometimes the input gets out of sync.  This is the best error checking
         currently available, firmware will probably be updated to expect a 101 or
         something in the top byte, which will be better error checking'''
         self.recurse_end()
         return voltage

      self.response(1)        # get an additional byte and then flush
      self.port.flushInput()
      return self.recurse(self.get_next_adc_voltage)

   def stop_getting_adc_voltages(self):
      '''I was encountering problems resetting out of adc mode, so I wrote this
      little function'''
      self.check_mode('adc')
      self.port.flushInput();
      for i in range(5):
         self.port.write("\x00");
         #r, w, e = select.select([self.port], [], [], 0.01);
         r = self.response(1, True)
         if (r): break;
      self.port.flushInput()
      self.enter_bb()
      return 1

   ''' Higher level functions.  Allows control of the BP port as if it were a microcontroller'''
   def set_port(self, byte):
      '''sets the port bits as determined by the translator (self.t).'''
      self.check_mode('bb')
      self.bp_port = byte & 0x1F
      #print 'config is', self.bp_config
      #print 'port is', self.bp_port

      if ord(self.set_pins_bb(translator(self.bp_config  # check config bits too
            | self.bp_port, self.t))) & 0b11100000 == 0x80 | self.bp_config:
         self.recurse_end()
         return 1
      return self.recurse(self.set_port, byte)

   def read_port(self):
      '''reads the port.  Will return a number (as opposed to a string).  Returns None
      if there is an error'''
      self.check_mode(['bb'])
      out = ord(self.set_pins_bb(translator(self.bp_config | self.bp_port, self.t)))

      if out & 0b11100000 == 0x80 | self.bp_config:   #check config bits too
         self.recurse_end()
         return translator(0x1F & out, self.t)
      return self.recurse(self.read_port)

   def read_pin(self, pin):
      '''Gets the data at the pin.  Only works in bit bang mode'''
      self.check_mode('bb')
      pin = pin.upper()
      out = self.read_port()
      if out is None: return None
      out = translator(pinout_bb[pin], self.t) & out
      return bool(out)

   def set_dir(self, pins):
      '''sets pins as either input (1) or output (0).  Only for bb mode '''
      self.check_mode('bb')
      self.bp_dir = pins & 0x1F   # filter      

      if ord(self.cfg_pins(translator(self.bp_dir, self.t))) & 0b11100000 == 0b01000000:
         self.recurse_end()
         return 1
      return self.recurse(self.set_dir, pins)

   def set_pin_dir(self, pin, direction):
      '''sets the pin direction.  Only works in bit bang mode'''
      self.check_mode('bb')
      pin = pin.upper()
      if direction is ('out' or 'Out' or 'OUT' or 0):
         #print 'setting as out'
         self.bp_dir &= ~translator(pinout_bb[pin], self.t)
      elif direction is ('in' or 'In' or 'IN' or 1):
         #print 'setting as in'
         self.bp_dir |= translator(0x1F & pinout_bb[pin], self.t)
      else: raise ValueError('incorrect value for direction')
      return self.set_dir(self.bp_dir)

   ''' Higher level commands that can be used in ANY mode'''
   def configure_peripherals(self, power = None, pullups = None):
      '''sets configuration settings of peripherals.  Use set_pin and clear_pin to 
      adjust pins.  Can be used in ANY mode'''
      if self.mode == 'bb':
         if power != None:
            if (power.upper() == 'YES') or (power.upper() == 'ON'):
               self.bp_config |= 0b01000000
            elif (power.upper() == 'NO') or (power.upper() == 'OFF'):
               self.bp_config &= 0b10111111
            else: raise ValueError('incorrect value given for power')
         if pullups != None:
            if (pullups.upper() == 'YES') or (pullups.upper() == 'ON'):
               self.bp_config |= 0b00100000
            elif (pullups.upper() == 'NO') or (pullups.upper() == 'OFF'):
               self.bp_config &= 0b11011111
            else: raise ValueError('incorrect value given for pullups')
         check = (#returns the whole port back so we filter
               0b11100000 & (translator(ord(self.set_pins_bb(
               translator(self.bp_config | self.bp_port, self.t))) , self.t)))
         if check == 0x80 | self.bp_config:
            self.recurse_end()
            return 1

      else:
         self.check_mode(not_bb)
         if power != None:
            if (power.upper() == 'YES') or (power.upper() == 'ON'):
               self.bp_config |= 0b1000
            elif (power.upper() == 'NO') or (power.upper() == 'OFF'):
               self.bp_config &= 0b0111
            else: raise ValueError('incorrect value given for i2c_dir')
         if pullups != None:
            if (pullups.upper() == 'YES') or (pullups.upper() == 'ON'):
               self.bp_config |= 0b0100
            elif (pullups.upper() == 'NO') or (pullups.upper() == 'OFF'):
               self.bp_config &= 0b1011
            else: raise ValueError('incorrect value given for i2c_dir')
         if self.cfg_pins(self.bp_config | self.bp_port):
            self.recurse_end()
            return 1
      return self.recurse(self.configure_peripherals, power, pullups)

   def get_peripheral_configuration(self):
      '''more of a placeholder than anything right now'''
      if self.mode == 'bb':
         return 0b01100000 & self.bp_config
      else:
         self.check_mode(not_bb)
         return 0b1100 & self.bp_config

   def set_pin(self, pin):
      '''sets the pin.  needs more testing for non-bb modes, but works in i2c
      and bb modes'''
      self.check_mode(all_modes)
      if self.mode == 'bb':
         pin = pin.upper()
         self.bp_port |= translator(pinout_bb[pin], self.t)
         return self.set_port(self.bp_port)
      else:
         '''this code works very strangely, it seems that
         CS and AUX work differently.  Needs more testing
         I think that CS = 1 makes it input (sinks and goes 
         low) and CS = 0 makes it output (so it goes high 
         w/ pullup).'''
         pin = pin.upper()
         if pin == 'CS':
            self.bp_port |= 0b01
         elif pin == 'AUX':
            self.bp_port &= ~0b10
         else: raise ValueError('wrong value')
         self.cfg_pins(self.bp_config | self.bp_port)

   def clear_pin(self, pin):
      '''clears the pin, needs more testing for non-bb modes'''
      self.check_mode(all_modes)
      if self.mode == 'bb':
         pin = pin.upper()
         #print 'internal port', bin(self.bp_port); #print 'bp port', bin(self.read_port_bb())
         self.bp_port &= ~translator(pinout_bb[pin], self.t)
         #print 'and now internal port', bin(self.bp_port)
         return self.set_port(self.bp_port)

      else:
         '''this code works very strangely, it seems that
         CS and AUX work differently.  Needs more testing
         I think that CS = 1 makes it input (sinks and goes 
         low) and CS = 0 makes it output (so it goes high 
         w/ pullup).'''
         pin = pin.upper()
         if pin == 'CS':
            self.bp_port &= ~0b01
         elif pin == 'AUX':
            self.bp_port |= 0b10
         else: raise ValueError('wrong value')
         self.cfg_pins(self.bp_config | self.bp_port)

   """ General Commands for Higher-Level Modes.  
   Note: Some of these do not have error checking implemented 
   (they return a 0 or 1.  You have to do your own error 
   checking.  This is as planned, since all of these
   depend on the device you are interfacing with)"""

   def set_speed(self, speed = 0):
      '''sets the speed of communication.  Used in every extra mode (not bb)'''
      self.check_mode(not_bb)
      self.port.write(chr(0x60 | speed))
      self.timeout(self.minDelay * 10)
      if self.response() == 1:
         self.recurse_end()
         return 1
      return self.recurse(self.set_speed, speed)

   def send_start_bit(self):
      self.check_mode(['i2c', 'raw'])
      self.port.write("\x02")
      #self.timeout(0.1)
      if self.response() == 1:
         self.recurse_end()
         return 1
      return self.recurse(self.send_start_bit)

   def send_stop_bit(self):
      self.check_mode(['i2c', 'raw'])
      self.port.write("\x03")
      if self.response() == 1:
         self.recurse_end()
         return 1
      return self.recurse(self.send_stop_bit)

   def read_byte(self):
      '''Reads a byte from the bus, returns the byte. You must ACK or NACK each 
      byte manually.  NO ERROR CHECKING (obviously)'''
      self.check_mode(not_bb)
      if self.mode == 'raw':
         self.port.write("\x06")
         #self.timeout(0.1)
         return self.response(1, True) #this was changed, before it didn't have the 'True' which means it
                                       # would have never returned any real data!
      else:
         self.port.write("\x04")
         #self.timeout(0.1)
         return self.response(1, True)

   def bulk_trans(self, byte_count = 1, byte_string = None):
      '''this is how you send data in most of the communication modes.
      See the i2c example function in common_functions.
      Send the data, and read the returned array.  
      In I2C:  A '1' means that it was NOT ACKNOWLEDGED, and a '0' means that 
      it WAS ACKNOWLEDGED (the reason for this is because this is what the 
      bus pirate itself does...)
      In modes other than I2C I think it returns whatever data it gets while
      sending, but this feature is untested.  PLEASE REPORT so that I can
      document it.'''
      self.check_mode(not_bb)
      if byte_string == None: pass
      self.port.write(chr(0x10 | (byte_count - 1)))
      #self.timeout(self.minDelay * 10)
      for i in range(byte_count):
         self.port.write(chr(byte_string[i]))
         #self.timeout(self.minDelay * 10)
      data = self.response(byte_count + 1, True)
      if ord(data[0]) == 1:  # bus pirate sent an acknolwedge properly
         self.recurse_end()
         return data[1:]
      self.recurse(self.bulk_trans, byte_count, byte_string)

if __name__ == '__main__':
   from common_functions import init_bus_pirate
   #test routine
   bp_device = init_bus_pirate('bb')
   if not bp_device:
      print 'cant connect'
      sys.exit()
   print 'connected'

   #port_test(bp_device, 0b00001)
   #pin_test(bp_device, 'miso')
   integrity_test(bp_device)

   raw_input('press enter to exit')
   #leave
   if bp_device.resetBP():
      print "Exited successfully"
   else:
      print "failed exit."
      sys.exit()
