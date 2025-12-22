# Pytest Sample Repository

A sample Python project demonstrating pytest testing with pre-commit hooks for code quality.

## Project Structure

```
.
├── src/                    # Source code
│   ├── __init__.py
│   ├── calculator.py       # Calculator functions
│   └── string_utils.py     # String utility functions
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_calculator.py  # Calculator tests
│   └── test_string_utils.py # String utility tests
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml          # Project configuration and Ruff settings
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- **Sample Python modules**: Calculator and string utility functions
- **Comprehensive tests**: Unit tests with pytest including parametrized tests
- **Code quality tools**: Ruff for linting and formatting
- **Pre-commit hooks**: Automatic code quality checks before commits
- **Test coverage**: pytest-cov for coverage reporting

## Setup

### 1. Create a virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install with optional dev dependencies:

```bash
pip install -e ".[dev]"
```

### 3. Initialize git repository (if not already done)

```bash
git init
```

### 4. Install pre-commit hooks

```bash
pre-commit install
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

Run specific test file:
```bash
pytest tests/test_calculator.py
```

Run tests in verbose mode:
```bash
pytest -v
```

## Pre-commit Hooks

The pre-commit hooks will automatically run before each commit:

- **Ruff linter**: Checks code for errors and style issues (with auto-fix)
- **Ruff formatter**: Formats code according to style guidelines

### Manual pre-commit run

Run on all files:
```bash
pre-commit run --all-files
```

Run on staged files only:
```bash
pre-commit run
```

## Ruff Configuration

Ruff is configured in `pyproject.toml` with:
- Target Python version: 3.12
- Line length: 100 characters
- Auto-fix enabled
- Selected rules: E (errors), F (code issues), W (warnings), I (import sorting), B (common mistakes)
- Ignored rules: E501 (long lines in comments), F403/F405 (import * patterns)

## Code Quality

The project enforces code quality through:
1. **Linting**: Ruff checks for code issues
2. **Formatting**: Ruff formats code consistently
3. **Testing**: pytest ensures functionality
4. **Coverage**: pytest-cov tracks test coverage
5. **Pre-commit**: Automatic checks before commits

## Example Usage

```python
from src.calculator import add, subtract, multiply, divide
from src.string_utils import reverse_string, is_palindrome, count_vowels

# Calculator
result = add(5, 3)  # 8
result = divide(10, 2)  # 5.0

# String utilities
reversed_text = reverse_string("hello")  # "olleh"
is_pal = is_palindrome("racecar")  # True
vowel_count = count_vowels("hello")  # 2
```

## Contributing

1. Make your changes
2. Run tests: `pytest`
3. Pre-commit hooks will run automatically on commit
4. If hooks fail, fix issues and commit again

## License

MIT License