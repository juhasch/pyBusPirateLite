import pytest

from pyBusPirateLite.I2C import I2C


def test_init():
    i2c = I2C(connect=False)
    assert i2c.portname == ''


def test_connect():
    i2c = I2C(connect=False)
    i2c.connect()
    assert i2c.portname != ''
    i2c.hw_reset()


def test_enter():
    i2c = I2C(connect=False)
    i2c.connect()
    i2c.enter()
    assert i2c.mode == 'i2c'


def test_connect_on_init():
    i2c = I2C()
    assert i2c.mode == 'i2c'


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
