# API Reference

This section provides detailed documentation for the pyBusPirateLite API.

## Core Modules

```{toctree}
:maxdepth: 2

spi
i2c
uart
bitbang
onewire
rawwire
adc
```

## Common Features

All protocol modules share some common features:

- Automatic port detection
- Connection management
- Error handling
- Configuration options

## Example Usage

### SPI Interface

```python
from pyBusPirateLite.SPI import SPI

spi = SPI()
spi.pins = SPI.PIN_POWER | SPI.PIN_CS 
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
spi.speed = '1MHz'

# Send data
spi.cs = True
data = spi.transfer([0x82, 0x00])
spi.cs = False
```

### I2C Interface

```python
from pyBusPirateLite.I2C import I2C

i2c = I2C()
i2c.speed = '400kHz'
i2c.configure(power=True)
i2c.write_then_read(2, 0, [0xec, 0xf6])
```

### UART Interface

```python
from pyBusPirateLite.UART import UART

uart = UART()
uart.speed = '115200'
uart.configure(power=True)
uart.write([0x55, 0xAA])
data = uart.read(10)
```

## Error Handling

All modules raise appropriate exceptions when errors occur:

```python
from pyBusPirateLite.exceptions import BusPirateError

try:
    spi = SPI()
    spi.transfer([0x00])
except BusPirateError as e:
    print(f"Error: {e}")
```

## Configuration Options

Each protocol module has specific configuration options:

- Speed settings
- Pin configurations
- Protocol-specific settings

See the individual module documentation for details. 