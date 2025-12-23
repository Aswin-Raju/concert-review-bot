# Pytest Sample Repository

A sample Python project demonstrating pytest testing with automated code review using Git hooks.

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
- **Automated Code Review**: Git hooks that run checks after commits and before pushes
- **Line-by-line Review Comments**: Detailed feedback on code quality issues
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

### 4. Install Git hooks for automated code review

```bash
bash scripts/install_hooks.sh
```

This will install:
- **post-commit hook**: Runs code quality checks after each commit
- **pre-push hook**: Shows review comments before pushing to remote

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

## Automated Code Review System

### How It Works

1. **After Each Commit**: The `post-commit` hook automatically runs:
   - Ruff linting on changed Python files
   - Code formatting checks
   - All tests via pytest
   - Saves review comments to `.git/review-comments/`

2. **Before Pushing**: The `pre-push` hook:
   - Checks for any saved review comments
   - Displays detailed issues with file, line, and error information
   - Asks for confirmation before pushing code with issues

3. **Review Comments Include**:
   - 🔴 Errors (linting issues, test failures)
   - ⚠️ Warnings (formatting issues, code style)
   - Line-by-line feedback with specific error codes
   - Suggestions for fixing issues

### Manual Review Check

Run the review bot manually on the last commit:
```bash
python3 scripts/review_bot.py
```

View saved review comments:
```bash
cat .git/review-comments/$(git rev-parse HEAD).json
```

### Example Review Output

```
## 🔍 Code Review Results

Found 3 issue(s) that need attention:

### 📄 `src/calculator.py`

🔴 **Line 15:5** - `F841`
   Local variable `unused_var` is assigned but never used

⚠️ **Line 1:1** - `FORMAT`
   File is not properly formatted. Run 'ruff format' to fix.

### 📄 `tests/`

🔴 **Line 1:1** - `TEST`
   Test failure: FAILED tests/test_calculator.py::test_divide_by_zero

---
💡 **Next Steps:**
1. Fix the issues listed above
2. Run `ruff check --fix` to auto-fix linting issues
3. Run `ruff format` to format your code
4. Run `pytest` to ensure all tests pass
5. Commit and push your changes
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
5. **Automated Review**: Git hooks provide line-by-line feedback

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
3. Commit your changes (review bot runs automatically)
4. Review any issues reported by the post-commit hook
5. Fix issues if needed and commit again
6. Push your changes (pre-push hook will show any remaining issues)

### Workflow Example

```bash
# Make changes to code
vim src/calculator.py

# Run tests locally
pytest

# Commit changes (triggers post-commit hook)
git add src/calculator.py
git commit -m "Add new feature"

# Review bot runs automatically and shows results
# If issues found, fix them:
ruff check --fix src/
ruff format src/
pytest

# Commit fixes
git add src/
git commit -m "Fix code quality issues"

# Push (pre-push hook shows final review)
git push origin feature-branch
```

### Uninstalling Hooks

To remove the Git hooks:
```bash
rm .git/hooks/post-commit .git/hooks/pre-push
```

## License

MIT License