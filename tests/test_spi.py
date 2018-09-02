from pyBusPirateLite.SPI import CFG_IDLE, CFG_PUSH_PULL, SPI


def test_init():
    spi = SPI(connect=False)
    assert spi.portname == ''


def test_connect():
    spi = SPI(connect=False)
    spi.connect()
    assert spi.portname != ''
    spi.hw_reset()


def test_enter():
    spi = SPI(connect=False)
    spi.connect()
    spi.enter()
    assert spi.mode == 'spi'
    spi.hw_reset()


def test_connect_on_init():
    spi = SPI()
    assert spi.mode == 'spi'
    spi.hw_reset()


def test_modestring():
    spi = SPI()
    assert spi.modestring == 'SPI1'
    spi.hw_reset()
