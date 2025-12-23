# GitHub PR Comments Setup Guide

This guide explains how to set up automatic posting of review comments to GitHub Pull Requests.

## Overview

When you push code with issues, the system can automatically post detailed review comments to your GitHub PR, showing:
- 🔴 Errors with line numbers
- ⚠️ Warnings with specific error codes
- 💡 Suggestions for fixing issues

## Setup Steps

### Step 1: Create a GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name: "Code Review Bot"
4. Select scopes:
   - ✅ `repo` (for private repositories)
   - OR ✅ `public_repo` (for public repositories only)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Step 2: Configure the Token

Choose one of these methods:

#### Option A: Environment Variable (Recommended)

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export GITHUB_TOKEN='ghp_your_token_here'
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

#### Option B: Git Config (Per Repository)

```bash
git config github.token 'ghp_your_token_here'
```

Or globally:
```bash
git config --global github.token 'ghp_your_token_here'
```

### Step 3: Verify Setup

Test the PR comment poster:

```bash
python3 scripts/post_pr_comments.py
```

Expected output:
```
🚀 GitHub PR Comment Poster
============================================================
Repository: owner/repo-name

📝 Checking X commit(s) for review comments...
✅ Comment posted to PR #123
============================================================
✅ Posted 1 review comment(s) to PR
```

## How It Works

### Automatic Posting (During Push)

When you push code with issues:

```bash
git push origin feature-branch
```

The pre-push hook will:
1. Show you the review comments
2. Ask: "Do you want to continue pushing? (y/N)"
3. If you say yes, ask: "Post review comments to GitHub PR? (y/N)"
4. If you say yes, automatically post comments to the PR

### Manual Posting

Post comments manually anytime:

```bash
python3 scripts/post_pr_comments.py
```

This will:
- Find all commits being pushed
- Check for saved review comments
- Find the associated PR
- Post comments to the PR

## Example PR Comment

When posted to GitHub, the comment looks like:

```markdown
## 🤖 Automated Code Review for commit `abc1234`

## 🔍 Code Review Results

Found 3 issue(s) that need attention:

### 📄 `src/calculator.py`

🔴 **Line 15:5** - `F841`
   Local variable `unused_var` is assigned but never used

⚠️ **Line 20:1** - `FORMAT`
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

---
*This is an automated review. Fix the issues and push again.*
```

## Workflow Example

### Complete Workflow with PR Comments

```bash
# 1. Create a feature branch
git checkout -b feature/new-feature

# 2. Make changes with some issues
cat > src/example.py << 'EOF'
def bad_function():
    unused = 5
    return 1
EOF

# 3. Commit (post-commit hook runs)
git add src/example.py
git commit -m "Add new feature"
# Output: ❌ Found 1 issue(s): unused variable

# 4. Push to create PR
git push origin feature/new-feature

# Pre-push hook shows:
# ⚠️ WARNING: You are pushing commits with code quality issues!
# Do you want to continue pushing? (y/N) y
# Post review comments to GitHub PR? (y/N) y
# 📤 Posting review comments to PR...
# ✅ Comment posted to PR #123

# 5. Check your PR on GitHub - you'll see the automated review comment!

# 6. Fix the issues
cat > src/example.py << 'EOF'
def good_function():
    """A properly formatted function."""
    return 1
EOF

# 7. Commit and push the fix
git add src/example.py
git commit -m "Fix: Remove unused variable"
git push origin feature/new-feature
# Output: ✅ All checks passed!
```

## Features

### Smart PR Detection
- Automatically finds the PR for your branch
- Works with any branch name
- Skips main/master branches

### Commit Tracking
- Only posts comments for commits being pushed
- Avoids duplicate comments
- Links comments to specific commits

### Error Handling
- Clear error messages if token is missing
- Validates repository access
- Handles API rate limits gracefully

## Troubleshooting

### "GitHub token not found"

**Solution**: Set up your token using one of the methods in Step 2.

```bash
# Quick fix:
export GITHUB_TOKEN='your_token_here'
```

### "No open PR found for branch"

**Cause**: You haven't created a PR yet, or the PR is closed.

**Solution**: Create a PR on GitHub first, then push again.

### "Failed to post comment: 401"

**Cause**: Invalid or expired token.

**Solution**: Generate a new token and update your configuration.

### "Failed to post comment: 404"

**Cause**: Repository not found or no access.

**Solution**: 
- Check that the token has correct permissions
- Verify you have access to the repository
- Ensure the repository URL is correct

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit tokens to git**
   - Tokens are in `.gitignore` by default
   - Use environment variables or git config

2. **Use minimal permissions**
   - Only grant `public_repo` for public repos
   - Use `repo` only when needed for private repos

3. **Rotate tokens regularly**
   - Generate new tokens periodically
   - Revoke old tokens on GitHub

4. **Keep tokens private**
   - Don't share tokens in chat or email
   - Don't include in screenshots

## Advanced Usage

### Post Comments for Specific Commits

```bash
# Get commit hash
COMMIT=$(git rev-parse HEAD)

# Post comment for that commit
python3 -c "
from scripts.post_pr_comments import PRCommentPoster
poster = PRCommentPoster()
poster.post_comments_for_commits(['$COMMIT'])
"
```

### Disable Automatic Posting

Edit `.git/hooks/pre-push` and remove the PR comment posting section, or always answer 'n' when prompted.

### Batch Post Comments

```bash
# Post comments for all unpushed commits
python3 scripts/post_pr_comments.py
```

## Integration with CI/CD

If you later enable GitHub Actions, you can use the same review bot:

```yaml
# .github/workflows/review.yml
name: Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Review Bot
        run: python3 scripts/review_bot.py
      - name: Post Comments
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python3 scripts/post_pr_comments.py
```

## FAQ

### Q: Will comments be posted for every push?
**A:** Only if you answer 'y' when prompted, and only for commits with issues.

### Q: Can I post comments without pushing?
**A:** Yes, run `python3 scripts/post_pr_comments.py` manually.

### Q: What if I don't want PR comments?
**A:** Just answer 'n' when the pre-push hook asks, or don't set up a GitHub token.

### Q: Can multiple people use this?
**A:** Yes! Each developer sets up their own token. Comments show who posted them.

### Q: Are comments deleted when issues are fixed?
**A:** No, they remain as a history. Post a new comment when fixed.

## Support

For issues:
1. Check token permissions
2. Verify repository access
3. Test with `python3 scripts/post_pr_comments.py`
4. Check GitHub API status: https://www.githubstatus.com/

For more help, see:
- `README.md` - Main documentation
- `SETUP_GUIDE.md` - Installation guide
- `MIGRATION_GUIDE.md` - Migration from pre-commit