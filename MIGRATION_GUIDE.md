# Migration Guide: From Pre-commit to Post-commit Hooks

This guide explains how to migrate from pre-commit hooks to the new post-commit hook system.

## Why the Change?

**Pre-commit hooks** run BEFORE you commit, which can:
- Block your commits if checks fail
- Interrupt your workflow
- Require you to fix issues before committing

**Post-commit hooks** run AFTER you commit, which:
- ✅ Never blocks your commits
- ✅ Gives immediate feedback after committing
- ✅ Allows you to commit freely and fix issues later
- ✅ Still warns you before pushing
- ✅ Better for rapid development

## Migration Steps

### Step 1: Disable Pre-commit Hooks

Run the disable script:

```bash
bash scripts/disable_precommit.sh
```

This will:
- Disable the pre-commit hook (moves to `.git/hooks/pre-commit.disabled`)
- Uninstall pre-commit package integration
- Rename `.pre-commit-config.yaml` to `.pre-commit-config.yaml.disabled`

### Step 2: Install Post-commit Hooks

Run the installation script:

```bash
bash scripts/install_hooks.sh
```

This will:
- Install the post-commit hook
- Install the pre-push hook
- Set up the review bot

### Step 3: Verify Installation

Check that hooks are installed:

```bash
ls -la .git/hooks/post-commit .git/hooks/pre-push
```

Both should be executable (`-rwxr-xr-x`).

### Step 4: Test the New System

Make a test commit:

```bash
# Create a test file
echo "def test(): pass" > src/test.py

# Commit (post-commit hook runs here)
git add src/test.py
git commit -m "Test: Verify post-commit hook"

# You should see:
# 🚀 Running post-commit checks...
# ✅ All checks passed!
```

## Workflow Comparison

### Old Workflow (Pre-commit)

```bash
# Make changes
vim src/file.py

# Try to commit
git commit -m "Add feature"

# ❌ BLOCKED! Pre-commit hook fails
# Must fix issues before committing
ruff check --fix src/
git add src/
git commit -m "Add feature"  # Try again
```

### New Workflow (Post-commit)

```bash
# Make changes
vim src/file.py

# Commit (always succeeds)
git commit -m "Add feature"

# ✅ Commit created!
# 🔍 Post-commit hook runs and shows issues
# ❌ Found 2 issue(s): [details shown]

# Fix issues when ready
ruff check --fix src/
git add src/
git commit -m "Fix issues"

# ✅ All checks passed!

# Push (pre-push hook warns if issues exist)
git push origin main
```

## Key Differences

| Aspect | Pre-commit | Post-commit |
|--------|-----------|-------------|
| **When runs** | Before commit | After commit |
| **Blocks commit** | Yes | No |
| **Workflow** | Fix → Commit | Commit → Fix |
| **Flexibility** | Less | More |
| **Feedback timing** | Before commit | After commit |
| **Push warning** | No | Yes (pre-push hook) |

## Benefits of Post-commit

1. **Never blocks your work**: You can always commit, even with issues
2. **Immediate feedback**: See issues right after committing
3. **Flexible workflow**: Fix issues when convenient
4. **Push protection**: Pre-push hook warns before pushing bad code
5. **Better for experimentation**: Commit freely during development

## What Stays the Same

- ✅ Same code quality checks (Ruff, pytest)
- ✅ Same error reporting format
- ✅ Same line-by-line feedback
- ✅ Same review comment storage

## What Changes

- ⚠️ Checks run AFTER commit instead of BEFORE
- ⚠️ Commits always succeed (checks don't block)
- ⚠️ Pre-push hook added for final warning

## Rollback (If Needed)

To go back to pre-commit hooks:

```bash
# Re-enable pre-commit
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
mv .pre-commit-config.yaml.disabled .pre-commit-config.yaml
pre-commit install

# Remove post-commit hook
rm .git/hooks/post-commit

# Keep or remove pre-push hook (optional)
rm .git/hooks/pre-push
```

## FAQ

### Q: Will my commits be blocked if there are issues?
**A:** No! Post-commit hooks never block commits. You'll see issues after committing, but the commit is already created.

### Q: When should I fix issues?
**A:** You can fix them immediately or later. The pre-push hook will remind you before pushing.

### Q: Can I still push code with issues?
**A:** Yes, but the pre-push hook will warn you and ask for confirmation.

### Q: What if I want to skip the checks?
**A:** The checks always run, but they never block. You can ignore the warnings if needed.

### Q: How do I see what issues were found?
**A:** Check the output after committing, or view saved reviews:
```bash
cat .git/review-comments/$(git rev-parse HEAD).json
```

## Best Practices

1. **Review feedback after each commit**: Check the post-commit output
2. **Fix issues before pushing**: Address problems before they reach the remote
3. **Use the pre-push warning**: Pay attention to the pre-push hook's warnings
4. **Commit frequently**: Don't worry about perfect code in each commit
5. **Clean up before PR**: Ensure all issues are fixed before creating a PR

## Support

If you encounter issues during migration:

1. Check that hooks are executable: `ls -la .git/hooks/`
2. Verify Python version: `python3 --version` (requires 3.12+)
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Run manual test: `python3 scripts/review_bot.py`

For more help, see:
- `README.md` - Main documentation
- `SETUP_GUIDE.md` - Detailed setup instructions
- `TEST_GUIDE.md` - Testing procedures