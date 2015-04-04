#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyBusPirateLite.SPI import *

port = 'COM3'

def test_connect():
    spi = SPI()
    spi.connect(port)
    assert spi.connected
    spi.port.close()

def test_bbmode():
    spi = SPI()
    spi.connect(port)
    spi.enter_bb()
    assert spi.mode == 'bb'
    spi.port.close()

def test_spi():
    spi = SPI()
    spi.connect(port)
    spi.enter_bb()
    spi.enter_spi()
    assert spi.mode == 'spi'
    spi.port.close()

def test_i2c():
    spi = SPI()
    spi.connect(port)
    spi.enter_bb()
    spi.enter_i2c()
    assert spi.mode == 'i2c'
    spi.port.close()

def test_rawwire():
    spi = SPI()
    spi.connect(port)
    spi.enter_bb()
    spi.enter_rawwire()
    assert spi.mode == 'raw'
    spi.port.close()

def test_uart():
    spi = SPI()
    spi.connect(port)
    spi.enter_bb()
    spi.enter_uart()
    assert spi.mode == 'uart'
    spi.port.close()

