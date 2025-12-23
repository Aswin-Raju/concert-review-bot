#!/bin/bash
# Install git hooks for automated code review

set -e

echo "🔧 Installing Git Hooks for Code Review..."

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"
SCRIPTS_HOOKS_DIR="$REPO_ROOT/scripts/hooks"

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Install post-commit hook
echo "📝 Installing post-commit hook..."
cp "$SCRIPTS_HOOKS_DIR/post-commit" "$GIT_HOOKS_DIR/post-commit"
chmod +x "$GIT_HOOKS_DIR/post-commit"

# Install pre-push hook
echo "📝 Installing pre-push hook..."
cp "$SCRIPTS_HOOKS_DIR/pre-push" "$GIT_HOOKS_DIR/pre-push"
chmod +x "$GIT_HOOKS_DIR/pre-push"

# Make review bot executable
echo "📝 Making review bot executable..."
chmod +x "$REPO_ROOT/scripts/review_bot.py"

# Create review-comments directory
mkdir -p "$REPO_ROOT/.git/review-comments"

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "Installed hooks:"
echo "  • post-commit: Runs code quality checks after each commit"
echo "  • pre-push: Warns about code issues before pushing"
echo ""
echo "How it works:"
echo "  1. After each commit, code quality checks run automatically"
echo "  2. Issues are saved as review comments"
echo "  3. Before pushing, you'll see a summary of any issues"
echo "  4. You can choose to fix issues or push anyway"
echo ""
echo "To uninstall hooks, run:"
echo "  rm .git/hooks/post-commit .git/hooks/pre-push"
echo ""

