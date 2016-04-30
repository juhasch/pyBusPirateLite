#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""some simple pin testing or port testing"""

def testpin(bp_device, *pins):
   #pin dir testing
   print('config', bp_device.configure_peripherals(power = True, pullups = True))
   bp_device.set_port(0)
   bp_device.set_dir(0)


   raw_input('pin testing.  All pins (except the tested pin) set to inputs and values changed\nto zero, press enter when ready')

   for pin in pins:
      bp_device.set_pin_dir(pin, 'out')
      for n in range(5): #do full loop 5 times
         raw_input('changing %s to 1, press enter' % pin)
         print('error checking:', bp_device.set_pin(pin))
         print('adc currently reads', bp_device.get_adc_voltage(), 'volts')

         raw_input('now setting output to 0, press enter')
         print('error checking:', bp_device.clear_pin(pin))
         print('adc currently reads', bp_device.get_adc_voltage(), 'volts')
      raw_input('changing dir to input. press enter for next pin')
      bp_device.set_pin_dir(pin, 'in')

   raw_input('press enter for next')

def pin_dir_test(bp_device, *pins):
   '''This shows the strange occurence that the port is apparently reseting
   whenever you change the directions (and reseting to output no less).  Put
   a 5V pullup resistor on the pin and run this to see the effect'''
   #pin dir testing
   print 'config', bp_device.configure_peripherals(power = True, pullups = True)
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
