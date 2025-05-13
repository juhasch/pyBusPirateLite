# pyBusPirateLite Documentation

Welcome to the pyBusPirateLite documentation! This library provides a Python interface for the BusPirate hardware tool, making it easy to interact with various protocols like SPI, I2C, UART, and more.

## Quick Start

```python
from pyBusPirateLite.SPI import SPI

# Initialize SPI interface
spi = SPI()
spi.pins = SPI.PIN_POWER | SPI.PIN_CS 
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
spi.speed = '1MHz'

# Send data
spi.cs = True
data = spi.transfer([0x82, 0x00])
spi.cs = False
```

## Features

- Support for multiple protocols:
  - SPI
  - I2C
  - UART
  - Bitbang
  - Onewire
  - Rawwire
  - ADC measurements
- Modern Python interface
- Type hints support
- Comprehensive documentation
- Extensive test coverage

## Installation

```bash
pip install pyBusPirateLite
```

## Requirements

- Python 3.6 or higher
- pyserial 3.0 or higher
- BusPirate hardware

## Documentation Contents

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
usage/index
api/index
examples/index
contributing
changelog
```

## Support

If you encounter any issues or have questions, please:

1. Check the [documentation](https://pybuspiratelite.readthedocs.io/)
2. Search [existing issues](https://github.com/juhasch/pyBusPirateLite/issues)
3. Create a new issue if needed

## License

This project is licensed under the BSD License - see the [LICENSE](https://github.com/juhasch/pyBusPirateLite/blob/master/LICENSE) file for details.

## Acknowledgments

Based on code from Garrett Berg <cloudform511@gmail.com>
(http://dangerousprototypes.com/2011/03/14/new-version-of-pybuspiratelite-python-library/) 