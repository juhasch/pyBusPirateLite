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

For more information about the BusPirate see http://dangerousprototypes.com/docs/Bus_Pirate 

Based on code from Garrett Berg <cloudform511@gmail.com>
(http://dangerousprototypes.com/2011/03/14/new-version-of-pybuspiratelite-python-library/)


Examples
--------

### SPI

```python
from pyBusPirateLite.SPI import *

spi = SPI()
spi.pins = PIN_POWER | PIN_CS 
spi.config = CFG_PUSH_PULL | CFG_IDLE
spi.speed = '1MHz'

# send two bytes and receive answer
spi.cs = True
data = spi.transfer( [0x82, 0x00])
spi.cs = False
```

### Bitbang

```python
from pyBusPirateLite.BitBang import BitBang
from pyBusPirateLite.BBIO_base import PIN_AUX

bb = BitBang()
bb.outputs = PIN_AUX
bb.pins = 0        # set aux pin = 0   
bb.pins = PIN_AUX  # set aux pin = 1
```

### Automatically detect port
```python
from pyBusPirateLite.BitBang import BitBang
bb = BitBang(connect=False)
port = bb.get_port()
print(port)
```

### I2C
```python
from pyBusPirateLite.I2C import *

i2c = I2C()
i2c.pins = PIN_POWER | PIN_CS 
i2c.speed = '50kHz'
```
