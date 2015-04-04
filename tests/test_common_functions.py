#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

def speed_test_pin(bp_device):
    """a simple speed test I've been using to see how fast the bp can communicate."""
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
    print(' periods: /n', str(periods))
    print('\n\n\n frequency of data is : /n', [2.0 / n for n in periods]) #sent two commands so two times

def speed_test_adc(bp_device):
    """

    :rtype : object
    """
    bp_device.enter_bb()
    bp_device.configure_peripherals('on', 'on')
    voltages = [bp_device.special_start_getting_adc_voltages() ]
    periods = [1]
    print('got here')
    for n in range (50):
        periods.append(time.time())
        #voltages.append(bp_device.get_adc_voltage())
        voltages.append(bp_device.special_get_next_adc_voltage())
        periods[-1] = time.time() - periods[-1]
    print('all periods /n', periods)
    print('\n\n\nall voltages')
    print(voltages)
    print('\n\n frequency of data \n', [1.0 / n for n in periods])
