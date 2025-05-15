# Installation Guide

This guide will help you install pyBusPirateLite and its dependencies.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- BusPirate hardware device
- USB cable

## Basic Installation

The simplest way to install pyBusPirateLite is using pip:

```bash
pip install pyBusPirateLite
```

## Development Installation

If you want to contribute to the project or need the latest development version:

1. Clone the repository:
   ```bash
   git clone https://github.com/juhasch/pyBusPirateLite.git
   cd pyBusPirateLite
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Hardware Setup

1. Connect your BusPirate to your computer using a USB cable
2. The device should be automatically detected
3. Verify the connection:
   ```python
   from pyBusPirateLite.BitBang import BitBang
   bb = BitBang()
   print(bb.get_port())  # Should print the port name
   ```

## Troubleshooting

### Common Issues

1. **Device not found**
   - Check USB connection
   - Verify device drivers are installed
   - Try a different USB port

2. **Permission denied**
   - On Linux, add your user to the `dialout` group:
     ```bash
     sudo usermod -a -G dialout $USER
     ```
   - Log out and log back in for changes to take effect

3. **ImportError: No module named 'pyBusPirateLite'**
   - Verify installation was successful
   - Check if you're in the correct virtual environment
   - Try reinstalling the package

### Getting Help

If you encounter any issues not covered here:
1. Check the [documentation](https://pybuspiratelite.readthedocs.io/)
2. Search [existing issues](https://github.com/juhasch/pyBusPirateLite/issues)
3. Create a new issue with:
   - Python version
   - Operating system
   - BusPirate firmware version
   - Error message
   - Steps to reproduce

## Development Tools

After installation, you can use the following development tools:

1. Run tests:
   ```bash
   pytest
   ```

2. Check code style:
   ```bash
   black pyBusPirateLite tests
   isort pyBusPirateLite tests
   flake8 pyBusPirateLite tests
   ```

3. Type checking:
   ```bash
   mypy pyBusPirateLite
   ```

4. Build documentation:
   ```bash
   cd docs
   make html
   ``` 