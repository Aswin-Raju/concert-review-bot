#!/usr/bin/env python3
"""
Review Bot - Automated code review script for PR commits
Runs linting, formatting checks, and tests, then posts line-by-line comments on PRs
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


class ReviewBot:
    def __init__(self):
        self.repo_root = self._get_repo_root()
        self.errors: List[Dict] = []

    def _get_repo_root(self) -> Path:
        """Get the root directory of the git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        return Path(result.stdout.strip())

    def _get_changed_files(self) -> List[str]:
        """Get list of Python files changed in the last commit"""
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f.endswith(".py") and os.path.exists(f)]

    def _run_ruff_check(self, files: List[str]) -> List[Dict]:
        """Run ruff linting on changed files"""
        if not files:
            return []

        errors = []
        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json"] + files,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.stdout:
                ruff_output = json.loads(result.stdout)
                for issue in ruff_output:
                    errors.append(
                        {
                            "file": issue["filename"],
                            "line": issue["location"]["row"],
                            "column": issue["location"]["column"],
                            "code": issue["code"],
                            "message": issue["message"],
                            "severity": "error"
                            if issue["code"].startswith("E") or issue["code"].startswith("F")
                            else "warning",
                        }
                    )
        except subprocess.CalledProcessError as e:
            print(f"Ruff check failed: {e}")
        except json.JSONDecodeError:
            print("Failed to parse ruff output")

        return errors

    def _run_ruff_format_check(self, files: List[str]) -> List[Dict]:
        """Check if files are properly formatted"""
        if not files:
            return []

        errors = []
        try:
            result = subprocess.run(
                ["ruff", "format", "--check", "--diff"] + files,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.returncode != 0:
                # Parse diff output to find formatting issues
                for file in files:
                    errors.append(
                        {
                            "file": file,
                            "line": 1,
                            "column": 1,
                            "code": "FORMAT",
                            "message": "File is not properly formatted. Run 'ruff format' to fix.",
                            "severity": "warning",
                        }
                    )
        except subprocess.CalledProcessError:
            pass

        return errors

    def _run_pytest(self) -> List[Dict]:
        """Run pytest and capture failures"""
        errors = []
        try:
            result = subprocess.run(
                ["pytest", "-v", "--tb=short", "--no-cov"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.returncode != 0:
                # Parse pytest output for failures
                lines = result.stdout.split("\n")
                for line in lines:
                    if "FAILED" in line:
                        errors.append(
                            {
                                "file": "tests/",
                                "line": 1,
                                "column": 1,
                                "code": "TEST",
                                "message": f"Test failure: {line.strip()}",
                                "severity": "error",
                            }
                        )
        except subprocess.CalledProcessError:
            errors.append(
                {
                    "file": "tests/",
                    "line": 1,
                    "column": 1,
                    "code": "TEST",
                    "message": "Tests failed to run",
                    "severity": "error",
                }
            )

        return errors

    def run_checks(self) -> bool:
        """Run all checks and collect errors"""
        print("🔍 Running code quality checks...")

        # Get changed files
        changed_files = self._get_changed_files()
        if not changed_files:
            print("✅ No Python files changed")
            return True

        print(f"📝 Checking {len(changed_files)} file(s): {', '.join(changed_files)}")

        # Run ruff linting
        print("\n🔧 Running Ruff linter...")
        lint_errors = self._run_ruff_check(changed_files)
        self.errors.extend(lint_errors)

        # Run ruff format check
        print("🎨 Checking code formatting...")
        format_errors = self._run_ruff_format_check(changed_files)
        self.errors.extend(format_errors)

        # Run tests
        print("🧪 Running tests...")
        test_errors = self._run_pytest()
        self.errors.extend(test_errors)

        return len(self.errors) == 0

    def generate_review_comment(self) -> str:
        """Generate a formatted review comment"""
        if not self.errors:
            return "✅ All checks passed! Code looks good."

        comment = "## 🔍 Code Review Results\n\n"
        comment += f"Found {len(self.errors)} issue(s) that need attention:\n\n"

        # Group errors by file
        errors_by_file: Dict[str, List[Dict]] = {}
        for error in self.errors:
            file = error["file"]
            if file not in errors_by_file:
                errors_by_file[file] = []
            errors_by_file[file].append(error)

        # Format errors by file
        for file, file_errors in sorted(errors_by_file.items()):
            comment += f"### 📄 `{file}`\n\n"
            for error in file_errors:
                severity_emoji = "🔴" if error["severity"] == "error" else "⚠️"
                comment += f"{severity_emoji} **Line {error['line']}:{error['column']}** - `{error['code']}`\n"
                comment += f"   {error['message']}\n\n"

        comment += "\n---\n"
        comment += "💡 **Next Steps:**\n"
        comment += "1. Fix the issues listed above\n"
        comment += "2. Run `ruff check --fix` to auto-fix linting issues\n"
        comment += "3. Run `ruff format` to format your code\n"
        comment += "4. Run `pytest` to ensure all tests pass\n"
        comment += "5. Commit and push your changes\n"

        return comment

    def save_review_to_file(self):
        """Save review comments to a file for later use"""
        review_dir = self.repo_root / ".git" / "review-comments"
        review_dir.mkdir(exist_ok=True)

        # Get current commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        commit_hash = result.stdout.strip()

        review_file = review_dir / f"{commit_hash}.json"

        review_data = {
            "commit": commit_hash,
            "errors": self.errors,
            "comment": self.generate_review_comment(),
        }

        with open(review_file, "w") as f:
            json.dump(review_data, f, indent=2)

        print(f"\n📝 Review saved to: {review_file}")
        return review_file

    def print_summary(self):
        """Print a summary of the review"""
        if not self.errors:
            print("\n✅ All checks passed!")
            return

        print(f"\n❌ Found {len(self.errors)} issue(s):")
        print(self.generate_review_comment())


def main():
    """Main entry point"""
    bot = ReviewBot()

    # Run all checks
    success = bot.run_checks()

    # Save review comments
    bot.save_review_to_file()

    # Print summary
    bot.print_summary()

    # Exit with appropriate code
    if not success:
        print("\n⚠️  Please fix the issues before pushing to PR")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
