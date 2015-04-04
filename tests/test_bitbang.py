#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pyBusPirateLite.common_functions import init_bus_pirate

def test_init():
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
