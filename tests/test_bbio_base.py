# -*- coding: utf-8 -*-
from time import sleep
import pytest
# from pyBusPirateLite.BBIO_base import *
from pyBusPirateLite.BitBang import BitBang, PIN_CS, PIN_MISO, PIN_MOSI, PIN_CLK, PIN_AUX
from pyBusPirateLite.base import BusPirate


def test_outputs():
    """ Test if exception is raised when nothing is set yet """
    bb = BitBang()
    with pytest.raises(TypeError):
        _ = bb.outputs


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


def test_init():
    """Test initialization."""
    bp = BusPirate(connect=False)
    assert bp.portname == ''
    assert bp.speed == 115200
    assert bp.timeout == 0.1
    assert not bp.connected
    assert bp.mode is None


def test_connect():
    """Test connection."""
    bp = BusPirate(connect=False)
    with pytest.raises(ValueError):
        bp.connect()


def test_disconnect():
    """Test disconnection."""
    bp = BusPirate(connect=False)
    bp.disconnect()
    assert not bp.connected
    assert bp.port is None


def test_write():
    """Test write."""
    bp = BusPirate(connect=False)
    with pytest.raises(ValueError):
        bp.write([0x00])


def test_read():
    """Test read."""
    bp = BusPirate(connect=False)
    with pytest.raises(ValueError):
        bp.read()


def test_enter():
    """Test enter."""
    bp = BusPirate(connect=False)
    with pytest.raises(ValueError):
        bp.enter()


def test_reset():
    """Test reset."""
    bp = BusPirate(connect=False)
    with pytest.raises(ValueError):
        bp.reset()


def test_context_manager():
    """Test context manager."""
    with BusPirate(connect=False) as bp:
        assert isinstance(bp, BusPirate)
        assert not bp.connected
