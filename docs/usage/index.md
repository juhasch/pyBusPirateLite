# Usage Guide

This guide provides detailed examples for using pyBusPirateLite with different protocols.

## Common Setup

All protocol modules share some common setup steps:

```python
# Import the protocol module
from pyBusPirateLite.SPI import SPI  # or I2C, UART, etc.

# Create an instance
protocol = SPI()  # or I2C(), UART(), etc.

# Configure the interface
protocol.speed = '1MHz'  # Set appropriate speed
protocol.configure(power=True)  # Enable power pins if needed
```

## SPI Interface

The SPI interface supports various configurations and operations:

```python
from pyBusPirateLite.SPI import SPI

# Initialize and configure
spi = SPI()
spi.pins = SPI.PIN_POWER | SPI.PIN_CS 
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
spi.speed = '1MHz'

# Basic transfer
spi.cs = True
data = spi.transfer([0x82, 0x00])
spi.cs = False

# Read operation
spi.cs = True
spi.transfer([0x03])  # Read command
data = spi.transfer([0x00] * 10)  # Read 10 bytes
spi.cs = False
```

## I2C Interface

The I2C interface provides methods for common I2C operations:

```python
from pyBusPirateLite.I2C import I2C

# Initialize and configure
i2c = I2C()
i2c.speed = '400kHz'
i2c.configure(power=True)

# Write to device
i2c.write_then_read(2, 0, [0xec, 0xf6])  # Write 2 bytes to register 0

# Read from device
data = i2c.write_then_read(1, 1, [0xed])  # Read 1 byte from register 1
```

## UART Interface

The UART interface supports standard serial communication:

```python
from pyBusPirateLite.UART import UART

# Initialize and configure
uart = UART()
uart.speed = '115200'
uart.configure(power=True)

# Send data
uart.write([0x55, 0xAA])

# Receive data
data = uart.read(10)  # Read 10 bytes
```

## Bitbang Mode

Bitbang mode allows direct control of the BusPirate pins:

```python
from pyBusPirateLite.BitBang import BitBang

# Initialize
bb = BitBang()

# Configure outputs
bb.outputs = bb.PIN_AUX

# Control pins
bb.pins = 0        # Set aux pin = 0
bb.pins = bb.PIN_AUX  # Set aux pin = 1
```

## ADC Measurements

The ADC interface allows reading analog values:

```python
from pyBusPirateLite.ADC import ADC

# Initialize
adc = ADC()

# Read voltage
voltage = adc.read_voltage()
```

## Error Handling

All interfaces use consistent error handling:

```python
from pyBusPirateLite.exceptions import BusPirateError

try:
    spi = SPI()
    spi.transfer([0x00])
except BusPirateError as e:
    print(f"Error: {e}")
```

## Best Practices

1. Always configure the interface before use
2. Use appropriate speed settings
3. Handle errors appropriately
4. Close connections when done
5. Use context managers when possible

## Advanced Usage

For more advanced usage examples, see the [API Reference](../api/index.md) and [Examples](../examples/index.md) sections. 