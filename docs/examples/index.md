# Examples

This section provides practical examples for using pyBusPirateLite with different protocols and devices.

## Protocol Examples

```{toctree}
:maxdepth: 2
:caption: Protocol Examples:

spi_examples
i2c_examples
uart_examples
bitbang_examples
adc_examples
```

## Device Examples

```{toctree}
:maxdepth: 2
:caption: Device Examples:

eeprom_examples
sensor_examples
display_examples
```

## Common Patterns

### Context Manager Usage

```python
from pyBusPirateLite.SPI import SPI

with SPI() as spi:
    spi.speed = '1MHz'
    spi.cs = True
    data = spi.transfer([0x00])
    spi.cs = False
```

### Error Handling

```python
from pyBusPirateLite.exceptions import BusPirateError

try:
    with SPI() as spi:
        spi.transfer([0x00])
except BusPirateError as e:
    print(f"Error: {e}")
```

### Port Detection

```python
from pyBusPirateLite.BitBang import BitBang

bb = BitBang(connect=False)
port = bb.get_port()
print(f"BusPirate found at: {port}")
bb.connect()
```

## Contributing Examples

If you have a working example that you'd like to share, please:

1. Fork the repository
2. Add your example to the appropriate file
3. Submit a pull request

Make sure to include:
- Clear description of what the example does
- Required hardware setup
- Complete code with comments
- Expected output or behavior 