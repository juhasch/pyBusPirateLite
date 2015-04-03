#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
 * Summary :
 * 
 * Created on Jan 26, 2011
 * @author: garrett
'''

import select
import serial
import sys
from time import sleep

class PinCfg:
   POWER = 0x8
   PULLUPS = 0x4
   AUX = 0x2
   CS = 0x1

class BBIOPins:
   # Bits are assigned as such:
   MOSI = 0x01;
   CLK = 0x02;
   MISO = 0x04;
   CS = 0x08;
   AUX = 0x10;
   PULLUP = 0x20;
   POWER = 0x40;

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

all_modes = ['i2c' , 'uart' , 'spi' , '1wire' , 'raw', 'bb']
all_modes_and_special = ['i2c' , 'uart' , 'spi' , '1wire' , 'raw', 'bb', 'adc']
not_bb = ['i2c' , 'uart' , 'spi' , '1wire' , 'raw']

class BBIO_base():
   '''functions used in every mode, the base of class.  Most of these you can
   probably ignore, as they are just used in the other member classes
   Note: Also contains some of the older functions that are now probably outdated
   '''
   def resetBP(self):
      self.reset()
      self.port.write("\x0F")
      self.timeout(.1)
      #self.port.read(2000)
      self.port.flushInput()
      self.mode = None
      return 1

   def check_mode(self, chkmode):
      if self.mode not in chkmode:
         raise ValueError('attempt to run {0} protocol when the bus pirate is not in {0} mode'.format(chkmode))
      return 1

   def timeout(self, timeout = 0.1):
      sleep(timeout)
      #select.select([], [], [], timeout)

   def response(self, byte_count = 1, return_data = False):
      '''request a number of bytes and whether you want the data itself.  If it receives a
      '1' then it returns a 1 ('1' is the std bus pirate response for most functions)'''
      data = self.port.read(byte_count)
      if byte_count == 1 and return_data == False:
         if data == chr(0x01): return 1
         else: return None
      else:
         return data

   def cfg_pins(self, pins = 0):
      '''used in every mode to configure pins.  In bb it configures as either input or output,
      in the other modes it normally configures peripherals such as power supply and the aux pin'''
      self.check_mode(all_modes)
      self.port.write(chr(0x40 | pins))
      self.timeout(self.minDelay * 10)
      return self.response(1, True)

   def set_pins_bb(self, pins):
      '''same as raw_set_pins, except it returns the value it obtains. 
      Necessary to read values in bb mode.  Can be used instead of 
      the raw one if you want to know the output'''
      self.check_mode(all_modes_and_special)
      self.port.write(chr(0x80 | pins))
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
            self.port.write('\x00')
         self.port.flushInput()
         return function(*args)
      raise IOError('bus pirate malfunctioning')

   # Self Tests
   def short_selftest(self):
      self.check_mode('bb')
      self.port.write("\x10")
      self.timeout(self.minDelay * 10)
      return self.response(1, True)

   def long_selftest(self):
      self.check_mode('bb')
      self.port.write("\x11")
      self.timeout(self.minDelay * 10)
      return self.response(1, True)


   # PWM control
   def setup_PWM(self, prescaler, dutycycle, period):
      self.check_mode('bb')
      self.port.write("\x12")
      self.port.write(chr(prescaler))
      self.port.write(chr((dutycycle >> 8) & 0xFF))
      self.port.write(chr(dutycycle & 0xFF))
      self.port.write(chr((period >> 8) & 0xFF))
      self.port.write(chr(period & 0xFF))
      self.timeout(self.minDelay * 10)
      return self.response()

   # ADC control
   def ADC_measure(self):
      self.check_mode('bb')
      self.port.write("\x14")
      self.timeout(self.minDelay)
      return self.response(2, True)

   def mode_string(self):
      self.port.write("\x01")
      self.timeout(self.minDelay * 10)
      return self.response()

   '''unused legacy code or code I'm not so sure of...'''
   def raw_set_pins(self, pins):
      '''kept in for legacy purposes, but not used or recomended'''
      self.check_mode('raw')
      self.port.write(chr(0x80 | pins))
      self.timeout(self.minDelay)
      return self.response(1)

   def raw_cfg_pins(self, config):
      '''practically identical to cfg_pins except it returns a different value'''
      self.port.write(chr(0x40 | config))
      self.timeout(self.minDelay * 10)
      return self.response(1)

   def read_pins(self):
      '''I'm not sure what this is used for.  I can't find reference to the command 0x50'''
      self.port.write("\x50")
      self.timeout(self.minDelay)
      return self.response(1, True)

   def read_speed(self):
      '''I don't see reference to this in the documentation, but it was in the old pyBusPirateLite
      so I'm leaving it in.'''
      self.port.write("\x70")
      select.select(None, None, None, 0.1)
      return self.response(1, True)

   def reset(self):
      '''I would recommend not using this.  Use enter_bb instead.  Kept and NOT UPDTADED
      if people are using old code they should probably change their code :D'''
      self.port.write("\x00")
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
      self.port.write("\x04")
      self.timeout(0.1)
      return self.response(1)

   def cs_high(self):
      self.check_mode(['raw', 'spi'])
      self.bp_port |= 0b01
      self.port.write("\x05")
      self.timeout(0.1)
      return self.response(1)

   def BBmode(self):
      return self.enter_bb()

   def enter_SPI(self):
      return self.enter_spi()

   def enter_I2C(self):
      return self.enter_i2c()

   def enter_UART(self):
      return self.enter_uart()

   def clear_PWM(self):
      return self.clear_pwm()



'''Testing Functions.  Use these to do some simple pin testing or port testing'''

def pin_test(bp_device, *pins):
   #pin dir testing
   print 'config', bp_device.configure_peripherals(power = 'ON', pullups = 'on')
   bp_device.set_port(0)
   bp_device.set_dir(0)


   raw_input('pin testing.  All pins (except the tested pin) set to inputs and values changed\nto zero, press enter when ready')

   for pin in pins:
      bp_device.set_pin_dir(pin, 'out')
      for n in range(5): #do full loop 5 times
         raw_input('changing %s to 1, press enter' % pin)
         print 'error checking:', bp_device.set_pin(pin)
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

         raw_input('now setting output to 0, press enter')
         print 'error checking:', bp_device.clear_pin(pin)
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'
      raw_input('changing dir to input. press enter for next pin')
      bp_device.set_pin_dir(pin, 'in')

   raw_input('press enter for next')

def pin_dir_test(bp_device, *pins):
   '''This shows the strange occurence that the port is apparently reseting
   whenever you change the directions (and reseting to output no less).  Put
   a 5V pullup resistor on the pin and run this to see the effect'''
   #pin dir testing
   print 'config', bp_device.configure_peripherals(power = 'ON', pullups = 'on')
   bp_device.set_port(0)
   bp_device.set_dir(0x1F)

   raw_input('pin direction testing.  All pins set to inputs and values changed\nto zero, press enter when ready')

   for pin in pins:
      for n in range(5): #do full loop 5 times
         raw_input('changing %s direction to output, press enter' % pin)
         print 'error checking:', bp_device.set_pin_dir(pin, 'out')
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

         raw_input('now setting output to 0, press enter')
         print 'error checking:', bp_device.clear_pin(pin)
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

         raw_input('changing %s direction to input, press enter' % pin)
         print 'error checking:', bp_device.set_pin_dir(pin, 'in')
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

         raw_input('now setting output to 0, press enter')
         print 'error checking:', bp_device.clear_pin(pin)
         print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

   raw_input('press enter for next')

def port_test(bp_device, port, std_port = 0b00000):
   '''change the port to 0 or 1.  Works similiar to a microcontroller'''
   print 'config', bp_device.configure_peripherals(power = 'ON', pullups = 'on')
   bp_device.set_port(std_port)
   bp_device.set_dir(0)

   raw_input('port testing. All pins outputs and at %s.  press enter when ready' % bin(std_port))

   for n in range(5): #do full loop 5 times
      raw_input('changing port to %s, press enter' % bin(~port & std_port))
      print 'error checking:', bp_device.set_port(~port & std_port)
      print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

      raw_input('changing port to %s, press enter' % bin(port | std_port))
      print 'error checking:', bp_device.set_port(port | std_port)
      print 'adc currently reads', bp_device.get_adc_voltage(), 'volts'

   raw_input('press enter for next')


def pwm_test(bp_device):
   bp_device.set_pin_dir('aux', 'out')

   bp_device.set_pwm_frequency(1000)

   raw_input('press enter to continue')

def integrity_error():
   raise ValueError('failed the integrity test here')

def integrity_test(bp_device, test_repeat = 10):
   '''to do a code integrity test connect CS to MISO and CLK to MOSI.
   Also connect the ADC to either 3 or 5V .  AUX pin not currently tested
   (but it works... trust me :D )'''

   print 'starting integrity tests'
   print 'testing mode switching'
   for n in range(test_repeat):
      if not bp_device.enter_bb(): integrity_error()
      if not bp_device.enter_i2c(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()
      if not bp_device.enter_spi(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()
      if not bp_device.enter_1wire(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()
      if not bp_device.enter_uart(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()
      if not bp_device.enter_rawwire(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()

   print 'mode switching: OK'

   print 'checking adc'
   for n in range(test_repeat):
      if not bp_device.configure_peripherals(power = 'on', pullups = 'on'): integrity_error()

      if not bp_device.start_getting_adc_voltages(): integrity_error()

      for n in range(1000):
         if bp_device.get_next_adc_voltage() < 2: integrity_error()

      if not bp_device.stop_getting_adc_voltages(): integrity_error()

      if not bp_device.enter_bb(): integrity_error()

      if not bp_device.configure_peripherals(power = 'off'): integrity_error()

      voltage_drop = []
      for n in range(10):
         voltage_drop.append(bp_device.get_adc_voltage())
      if bp_device.get_adc_voltage() > 0.3: integrity_error()

   print "notice that the voltage drops steadily.  This is the power source turning off"
   print voltage_drop
   print 'adc: ok'

   print 'pin and port testing'
   for n in range(test_repeat):
      #first test x1x1
      if not bp_device.set_dir(0b11010): integrity_error()
      if not bp_device.set_port(0b00101): integrity_error()
      if bp_device.read_port() & 0b00101 != 0b00101: integrity_error()

      #now test x0x0
      if not bp_device.set_dir(0b11010): integrity_error()
      if not bp_device.set_port(0b00000): integrity_error()
      if bp_device.read_port() & 0b00000 != 0b00000: integrity_error()

      # now test 1x1x
      if not bp_device.set_dir(0b10101): integrity_error()
      if not bp_device.set_port(0b01010): integrity_error()
      if bp_device.read_port() & 0b01010 != 0b01010: integrity_error()

      # now test 0x0x
      if not bp_device.set_dir(0b10101): integrity_error()
      if not bp_device.set_port(0b0000): integrity_error()
      if bp_device.read_port() & 0b00000 != 0b00000: integrity_error()

      if not bp_device.set_dir(0x1F): integrity_error()
      # now do pin testing


      for pins in (('miso', 'cs') , ('mosi', 'clk')):
         if not bp_device.set_pin_dir(pins[0], 'in'): integrity_error()
         if not bp_device.set_pin_dir(pins[1], 'out'): integrity_error()
         if not bp_device.set_pin(pins[1]): integrity_error()
         if bp_device.read_pin(pins[0]) != 1: integrity_error()
         if not bp_device.clear_pin(pins[1]): integrity_error()
         if bp_device.read_pin(pins[0]) != 0: integrity_error()

         if not bp_device.set_pin_dir(pins[1], 'in'): integrity_error()
         if not bp_device.set_pin_dir(pins[0], 'out'): integrity_error()
         if not bp_device.set_pin(pins[0]): integrity_error()
         if bp_device.read_pin(pins[1]) != 1: integrity_error()
         if not bp_device.clear_pin(pins[0]): integrity_error()
         if bp_device.read_pin(pins[1]) != 0: integrity_error()

   print 'pins and port testing: OK'


   print 'still to do: pin and port testing in other modes.'

   # may use these instead of all the longer recursion statements eventually
   #_atempts_ = 0





count = 0
if __name__ == '__main__':
   print 'nothing here'



