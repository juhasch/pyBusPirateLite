# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-13

### Added
- Comprehensive test suite for all core protocols (SPI, I2C, UART, BitBang)
- Type hints for all public interfaces
- Detailed API documentation
- Example code for all supported protocols
- Context manager support for all interfaces

### Changed
- Improved code quality and consistency
- Enhanced error handling and reporting
- Better documentation structure and examples
- Clarified ADC functionality as part of BitBang interface
- Modernized Python code style

### Fixed
- Documentation accuracy improvements
- ADC examples updated to reflect actual implementation
- Test coverage expanded for core functionality
- Various minor bug fixes and improvements

## [0.3.0] - 2024-03-19

### Added
- Modern Python packaging with pyproject.toml
- Pre-commit hooks for code quality
- Type hints support
- Comprehensive test suite
- Improved documentation
- Development tools configuration (black, isort, flake8, mypy)

### Changed
- Updated minimum Python version to 3.6
- Modernized package structure
- Improved code quality and style

### Fixed
- Various bug fixes and improvements

## [0.2.0] - 2023-01-01

### Added
- Initial public release
- Support for SPI, I2C, UART, Bitbang, Onewire, Rawwire modes
- ADC measurements support

### Changed
- Based on code from Garrett Berg
- More Pythonic implementation 