# -*- coding: utf-8 -*-
from time import sleep

import pytest

from pyBusPirateLite.BitBang import BitBang


def test_outputs():
    """ Test if exception is raised when nothing is set yet """
    with pytest.raises(TypeError):
        bb = BitBang()
        bb.outputs
        bb.disconnect()
        bb.hw_reset()


def test_pins_CS():
    """ Set and read back CS pin """
    bb = BitBang()
    bb.outputs = bb.PIN_CS
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = bb.PIN_CS
    sleep(0.2)
    assert bb.outputs == bb.PIN_CS
    assert bb.pins == bb.PIN_CS
    bb.hw_reset()


def test_pins_MISO():
    """ Set and read back MISO pin """
    bb = BitBang()
    bb.outputs = bb.PIN_MISO
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = bb.PIN_MISO
    sleep(0.2)
    assert bb.outputs == bb.PIN_MISO
    assert bb.pins == bb.PIN_MISO
    bb.hw_reset()


def test_pins_MOSI():
    """ Set and read back MOSI pin """
    bb = BitBang()
    bb.outputs = bb.PIN_MOSI
    bb.pins = 0
    sleep(0.5)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = bb.PIN_MOSI
    sleep(0.2)
    assert bb.outputs == bb.PIN_MOSI
    assert bb.pins == bb.PIN_MOSI
    bb.hw_reset()


def test_pins_CLK():
    """ Set and read back CLK pin """
    bb = BitBang()
    bb.outputs = bb.PIN_CLK
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    bb.pins = bb.PIN_CLK
    sleep(0.2)
    assert bb.outputs == bb.PIN_CLK
    assert bb.pins == bb.PIN_CLK
    bb.hw_reset()


def test_pins_AUX():
    """ Set and read back AUX pin """
    bb = BitBang()
    bb.outputs = bb.PIN_AUX
    bb.pins = 0
    sleep(0.2)
    assert bb.outputs == 0
    assert bb.pins == 0
    sleep(0.2)
    bb.pins = bb.PIN_AUX
    assert bb.outputs == bb.PIN_AUX
    assert bb.pins == bb.PIN_AUX
    bb.hw_reset()
