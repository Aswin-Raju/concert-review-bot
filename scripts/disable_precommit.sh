#!/bin/bash
# Script to disable pre-commit hooks completely

set -e

echo "🔧 Disabling Pre-commit Hooks..."

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Disable pre-commit hook if it exists
if [ -f "$GIT_HOOKS_DIR/pre-commit" ]; then
    echo "📝 Disabling pre-commit hook..."
    mv "$GIT_HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit.disabled"
    echo "   ✅ Moved to pre-commit.disabled"
else
    echo "   ℹ️  No pre-commit hook found"
fi

# Uninstall pre-commit package hooks if installed
if command -v pre-commit &> /dev/null; then
    echo "📝 Uninstalling pre-commit package hooks..."
    pre-commit uninstall 2>/dev/null || true
    echo "   ✅ Pre-commit package hooks uninstalled"
else
    echo "   ℹ️  Pre-commit package not installed"
fi

# Rename .pre-commit-config.yaml to disable it
if [ -f "$REPO_ROOT/.pre-commit-config.yaml" ]; then
    echo "📝 Disabling .pre-commit-config.yaml..."
    mv "$REPO_ROOT/.pre-commit-config.yaml" "$REPO_ROOT/.pre-commit-config.yaml.disabled"
    echo "   ✅ Renamed to .pre-commit-config.yaml.disabled"
else
    echo "   ℹ️  No .pre-commit-config.yaml found"
fi

echo ""
echo "✅ Pre-commit hooks disabled successfully!"
echo ""
echo "Active hooks:"
echo "  • post-commit: Runs after each commit"
echo "  • pre-push: Runs before pushing"
echo ""
echo "Disabled:"
echo "  • pre-commit hook (if existed)"
echo "  • pre-commit package integration"
echo "  • .pre-commit-config.yaml"
echo ""
echo "To re-enable pre-commit hooks:"
echo "  mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit"
echo "  mv .pre-commit-config.yaml.disabled .pre-commit-config.yaml"
echo "  pre-commit install"
echo ""

# Made with Bob
