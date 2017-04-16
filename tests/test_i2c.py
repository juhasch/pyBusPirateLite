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


def test_echo():
    pass


def test_manual_speed_cfg():
    pass


def test_begin_input():
    pass


def test_end_input():
    pass


def test_enter_bridge_mode():
    pass


def def_set_cfg():
    pass


def test_read_cfg():
    pass
