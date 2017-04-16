# -*- coding: utf-8 -*-
from pyBusPirateLite.BitBang import BitBang
from pyBusPirateLite.BBIO_base import *
from nose.tools import raises
from time import sleep


@raises(TypeError)
def test_outputs():
    """ Test if exception is raised when nothing is set yet """
    bb = BitBang()
    bb.outputs
    bb.disconnect()
    bb.hw_reset()


def test_pins_CS():
    """ Set and read back CS pin """
    bb = BitBang()
    bb.outputs = PIN_CS
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = PIN_CS
    sleep(0.2)
    assert bb.outputs == PIN_CS
    assert bb.pins == PIN_CS
    bb.hw_reset()


def test_pins_MISO():
    """ Set and read back MISO pin """
    bb = BitBang()
    bb.outputs = PIN_MISO
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = PIN_MISO
    sleep(0.2)
    assert bb.outputs == PIN_MISO
    assert bb.pins == PIN_MISO
    bb.hw_reset()


def test_pins_MOSI():
    """ Set and read back MOSI pin """
    bb = BitBang()
    bb.outputs = PIN_MOSI
    bb.pins = 0
    sleep(0.5)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = PIN_MOSI
    sleep(0.2)
    assert bb.outputs == PIN_MOSI
    assert bb.pins == PIN_MOSI
    bb.hw_reset()


def test_pins_CLK():
    """ Set and read back CLK pin """
    bb = BitBang()
    bb.outputs = PIN_CLK
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = PIN_CLK
    sleep(0.2)
    assert bb.outputs == PIN_CLK
    assert bb.pins == PIN_CLK
    bb.hw_reset()


def test_pins_AUX():
    """ Set and read back AUX pin """
    bb = BitBang()
    bb.outputs = PIN_AUX
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    sleep(0.2)
    bb.pins = PIN_AUX
    assert bb.outputs == PIN_AUX
    assert bb.pins == PIN_AUX
    bb.hw_reset()
