.. _i2c_examples:

Examples using I2C
==================

Here is an example to read the ID of a BME280 pressure sensor. The I2C slave address is 0x76 and the ID register is 0xd0::


    from pyBusPirateLite.I2C import I2C

    i2c = I2C()
    i2c.speed = '400kHz'
    i2c.configure(power=True)
    i2c.start()
    i2c.transfer([0xec, 0xd0])
    r = i2c.write_then_read(1, 1, [0xed])
    print(f'BME280 ID={hex(r[0])}')


In this case the register address has to be written to the device first, using `0xec = 0x76 << 1`
as first data byte. When reading, the read address is `0xed = 0x76 << 1 + 0x01`.
