
[![Documentation Status](https://readthedocs.org/projects/pybuspiratelite/badge/?version=latest)](http://pybuspiratelite.readthedocs.io/en/latest/?badge=latest)


pyBusPirateLite
===============

Python library for BusPirate based on code from Garrett Berg.
It tries to be more Pythonic than the original code.

This library allows using the following modes:
* SPI
* I2C
* UART
* Bitbang
* Onewire
* Rawwire
* ADC measurements

For more information about the BusPirate see http://dangerousprototypes.com/docs/Bus_Pirate 

Based on code from Garrett Berg <cloudform511@gmail.com>
(http://dangerousprototypes.com/2011/03/14/new-version-of-pybuspiratelite-python-library/)

**Note**: Python 3.6 is required, mainly due to the use of `f`-strings.

Examples
--------

### SPI

```python
from pyBusPirateLite.SPI import SPI

spi = SPI()
spi.pins = SPI.PIN_POWER | SPI.PIN_CS 
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer( [0x82, 0x00])
spi.cs = False
```

### Bitbang
```python
from pyBusPirateLite.BitBang import BitBang

bb = BitBang()
bb.outputs = bb.PIN_AUX
bb.pins = 0        # set aux pin = 0   
bb.pins = bb.PIN_AUX  # set aux pin = 1
```

### I2C
```python
from pyBusPirateLite.I2C import I2C
i2c = I2C()
i2c.speed = '400kHz'
i2c.configure(power=True)
i2c.write_then_read(2,0, [0xec, 0xf6])  # set write register
i2c.write_then_read(1,1,[ 0xed])        # read from register
```

### Detect port
```python
from pyBusPirateLite.BitBang import BitBang
bb = BitBang(connect=False)
port = bb.get_port()
print(port)
bb.connect()
```
