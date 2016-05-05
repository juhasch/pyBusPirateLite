from pyBusPirateLite.SPI import SPI, CFG_PUSH_PULL, CFG_IDLE
from pyBusPirateLite.BBIO_base import PIN_POWER, PIN_CS


def test_init():
    spi = SPI(connect=False)
    assert spi.portname == ''


def test_connect():
    spi = SPI(connect=False)
    spi.connect()
    assert bb.portname != ''


def test_enter():
    spi = SPI(connect=False)
    spi.connect()
    spi.enter()
    assert spi.mode == 'spi'


def test_connect_on_init():
    spi = SPI()
    assert spi.mode == 'spi'


def test_modestring():
    spi = SPI()
    assert spi.modestring == 'SPI1'
