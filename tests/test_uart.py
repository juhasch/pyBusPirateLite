import pytest

from pyBusPirateLite.UART import UART


def test_init():
    uart = UART(connect=False)
    assert uart.portname == ''


def test_connect():
    uart = UART(connect=False)
    uart.connect()
    assert uart.portname != ''
    uart.hw_reset()


def test_enter():
    uart = UART(connect=False)
    uart.connect()
    uart.enter()
    assert uart.mode == 'uart'
    uart.hw_reset()


def test_connect_on_init():
    uart = UART()
    assert uart.mode == 'uart'
    uart.hw_reset()


def test_modestring():
    uart = UART()
    assert uart.modestring == 'ART1'
    uart.hw_reset()


@pytest.mark.xfail
def test_echo():
    raise NotImplementedError()


@pytest.mark.xfail
def test_manual_speed_cfg():
    raise NotImplementedError()


@pytest.mark.xfail
def test_begin_input():
    raise NotImplementedError()


@pytest.mark.xfail
def test_end_input():
    raise NotImplementedError()


@pytest.mark.xfail
def test_enter_bridge_mode():
    raise NotImplementedError()


@pytest.mark.xfail
def def_set_cfg():
    raise NotImplementedError()


@pytest.mark.xfail
def test_read_cfg():
    raise NotImplementedError()
