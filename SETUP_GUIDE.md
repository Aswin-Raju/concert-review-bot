# Automated Code Review Setup Guide

This guide explains how to set up and use the automated code review system using Git hooks.

## Overview

Since GitHub Actions are disabled at the organizational level, this solution uses **Git hooks** to run code quality checks locally and provide line-by-line review comments for PRs.

## How It Works

### 1. Post-Commit Hook
- Runs automatically **after each commit**
- Analyzes changed Python files
- Runs Ruff linting and formatting checks
- Executes pytest tests
- Saves detailed review comments to `.git/review-comments/`

### 2. Pre-Push Hook
- Runs automatically **before pushing to remote**
- Checks for saved review comments
- Displays all issues with file paths, line numbers, and error details
- Asks for confirmation before pushing code with issues
- Allows you to cancel and fix issues first

### 3. Review Bot
- Python script that performs all code quality checks
- Generates structured review comments in JSON format
- Provides actionable feedback with error codes and suggestions

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Git Hooks

```bash
bash scripts/install_hooks.sh
```

This will:
- Copy hook scripts to `.git/hooks/`
- Make them executable
- Create the review-comments directory

### Step 3: Verify Installation

```bash
ls -la .git/hooks/
```

You should see:
- `post-commit` (executable)
- `pre-push` (executable)

## Usage

### Normal Development Workflow

1. **Make changes to your code**
   ```bash
   vim src/calculator.py
   ```

2. **Commit your changes**
   ```bash
   git add src/calculator.py
   git commit -m "Add new feature"
   ```
   
   The post-commit hook runs automatically:
   ```
   🚀 Running post-commit checks...
   🔍 Running code quality checks...
   📝 Checking 1 file(s): src/calculator.py
   
   🔧 Running Ruff linter...
   🎨 Checking code formatting...
   🧪 Running tests...
   
   ❌ Found 2 issue(s):
   [Review output displayed here]
   ```

3. **Fix any issues if needed**
   ```bash
   ruff check --fix src/
   ruff format src/
   pytest
   ```

4. **Commit fixes**
   ```bash
   git add src/
   git commit -m "Fix code quality issues"
   ```

5. **Push to remote**
   ```bash
   git push origin feature-branch
   ```
   
   The pre-push hook runs:
   ```
   🔍 Checking for code review comments...
   
   ⚠️  Found review comments for commit: abc123...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [Detailed review comments displayed]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   ⚠️  WARNING: You are pushing commits with code quality issues!
   Do you want to continue pushing? (y/N)
   ```

### Manual Review Check

Run the review bot manually on the last commit:
```bash
python3 scripts/review_bot.py
```

View saved review comments:
```bash
cat .git/review-comments/$(git rev-parse HEAD).json
```

## Review Comment Format

Review comments include:

### Error Information
- **File path**: Which file has the issue
- **Line number**: Exact line with the problem
- **Column number**: Specific position in the line
- **Error code**: Ruff error code (e.g., F841, E501)
- **Message**: Description of the issue
- **Severity**: Error (🔴) or Warning (⚠️)

### Example Review Output

```markdown
## 🔍 Code Review Results

Found 3 issue(s) that need attention:

### 📄 `src/calculator.py`

🔴 **Line 15:5** - `F841`
   Local variable `unused_var` is assigned but never used

⚠️ **Line 1:1** - `FORMAT`
   File is not properly formatted. Run 'ruff format' to fix.

### 📄 `tests/test_calculator.py`

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

## Common Scenarios

### Scenario 1: All Checks Pass
```bash
git commit -m "Add feature"
# Output:
# 🚀 Running post-commit checks...
# ✅ All checks passed! Code looks good.
```

### Scenario 2: Issues Found
```bash
git commit -m "Add feature"
# Output:
# ❌ Found 2 issue(s):
# [Detailed review shown]
# ⚠️  Please fix the issues before pushing to PR

# Fix issues
ruff check --fix src/
pytest

# Commit fixes
git commit -m "Fix issues"
```

### Scenario 3: Push with Issues
```bash
git push origin feature-branch
# Output:
# ⚠️  WARNING: You are pushing commits with code quality issues!
# Do you want to continue pushing? (y/N) n
# Push cancelled. Fix the issues and try again.
```

## Troubleshooting

### Hook Not Running
```bash
# Check if hooks are executable
ls -la .git/hooks/post-commit .git/hooks/pre-push

# Make them executable if needed
chmod +x .git/hooks/post-commit .git/hooks/pre-push
```

### Review Bot Fails
```bash
# Check Python version (requires 3.12+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt

# Run manually to see errors
python3 scripts/review_bot.py
```

### Clear Old Review Comments
```bash
# Remove all saved review comments
rm -rf .git/review-comments/*
```

## Uninstalling

To remove the Git hooks:
```bash
rm .git/hooks/post-commit .git/hooks/pre-push
```

To remove review comments:
```bash
rm -rf .git/review-comments/
```

## Benefits

✅ **No GitHub Actions Required**: Works entirely with local Git hooks
✅ **Immediate Feedback**: Get review comments right after committing
✅ **Line-by-Line Details**: Know exactly where and what to fix
✅ **Prevents Bad Pushes**: Warning before pushing problematic code
✅ **Automated**: No manual steps needed once installed
✅ **Flexible**: Can push anyway if needed (with confirmation)

## Integration with PRs

When you push commits with review comments:
1. The pre-push hook shows all issues
2. You can choose to fix them or push anyway
3. In the PR, reviewers can reference the saved review comments
4. Team members can run the same checks locally

## Best Practices

1. **Fix issues before pushing**: Address review comments immediately
2. **Run tests locally**: Use `pytest` before committing
3. **Use auto-fix**: Run `ruff check --fix` to auto-fix many issues
4. **Format code**: Run `ruff format` to ensure consistent formatting
5. **Review comments**: Read the detailed feedback carefully

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the main README.md
3. Examine the review bot script: `scripts/review_bot.py`
4. Check hook scripts: `scripts/hooks/`