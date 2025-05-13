# Contributing to pyBusPirateLite

Thank you for your interest in contributing to pyBusPirateLite! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/pyBusPirateLite.git
   cd pyBusPirateLite
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests:
   ```bash
   pytest
   ```
4. Run linting:
   ```bash
   pre-commit run --all-files
   ```
5. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

## Code Style

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Write tests for new functionality

## Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage
- Use pytest fixtures for test setup

## Documentation

- Update documentation for any new features
- Follow the existing documentation style
- Include examples in docstrings
- Update README.md if necessary

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if needed
3. The PR will be merged once you have the sign-off of at least one maintainer

## Questions?

Feel free to open an issue if you have any questions about contributing! 