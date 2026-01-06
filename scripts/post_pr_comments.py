#!/usr/bin/env python3
"""
Post PR Comments - Posts saved review comments to GitHub Pull Requests
Reads review comments from .git/review-comments/ and posts them to the PR
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' package not installed. Run: pip install requests")
    sys.exit(1)


class PRCommentPoster:
    def __init__(self):
        self.repo_root = self._get_repo_root()
        self.github_token = self._get_github_token()
        self.repo_info = self._get_repo_info()

    def _get_repo_root(self) -> Path:
        """Get the root directory of the git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        return Path(result.stdout.strip())

    def _get_github_token(self) -> str:
        """Get GitHub token from environment or git config"""
        # Try environment variable first
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token

        # Try git config
        try:
            result = subprocess.run(
                ["git", "config", "--get", "github.token"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass

        print("Error: GitHub token not found!")
        print("Set it using one of these methods:")
        print("  1. Environment variable: export GITHUB_TOKEN='your_token'")
        print("  2. Git config: git config --global github.token 'your_token'")
        print("\nCreate a token at: https://github.com/settings/tokens")
        print("Required scopes: repo (for private repos) or public_repo (for public repos)")
        sys.exit(1)

    def _get_repo_info(self) -> Dict[str, str]:
        """Get repository owner and name from git remote"""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()

            # Parse GitHub URL (supports both HTTPS and SSH)
            if "github.com" in remote_url:
                # Remove .git suffix
                remote_url = remote_url.replace(".git", "")

                # Extract owner/repo from URL
                if remote_url.startswith("git@github.com:"):
                    # SSH format: git@github.com:owner/repo.git
                    parts = remote_url.replace("git@github.com:", "").split("/")
                elif "github.com/" in remote_url:
                    # HTTPS format: https://github.com/owner/repo.git
                    parts = remote_url.split("github.com/")[1].split("/")
                else:
                    raise ValueError("Unable to parse GitHub URL")

                return {"owner": parts[0], "repo": parts[1]}
            else:
                raise ValueError("Not a GitHub repository")
        except Exception as e:
            print(f"Error: Unable to determine repository info: {e}")
            print("Make sure you're in a GitHub repository with a remote named 'origin'")
            sys.exit(1)

    def _get_pr_number_for_commit(self, commit_hash: str) -> Optional[int]:
        """Get PR number for a commit by checking the current branch"""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            branch = result.stdout.strip()

            if branch == "main" or branch == "master":
                print(f"Commit {commit_hash[:7]} is on {branch} branch, skipping PR comment")
                return None

            # Search for PR with this branch
            url = f"https://api.github.com/repos/{self.repo_info['owner']}/{self.repo_info['repo']}/pulls"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            params = {"head": f"{self.repo_info['owner']}:{branch}", "state": "open"}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            prs = response.json()
            if prs:
                return prs[0]["number"]

            print(f"No open PR found for branch '{branch}'")
            return None

        except Exception as e:
            print(f"Error finding PR: {e}")
            return None

    def _post_pr_comment(self, pr_number: int, comment_body: str) -> bool:
        """Post a comment to a GitHub PR"""
        try:
            url = f"https://api.github.com/repos/{self.repo_info['owner']}/{self.repo_info['repo']}/issues/{pr_number}/comments"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            data = {"body": comment_body}

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            print(f"✅ Comment posted to PR #{pr_number}")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ Failed to post comment: {e}")
            if e.response.status_code == 401:
                print("   Check your GitHub token permissions")
            elif e.response.status_code == 404:
                print("   PR not found or no access to repository")
            return False
        except Exception as e:
            print(f"❌ Error posting comment: {e}")
            return False

    def _format_review_for_pr(self, review_data: Dict) -> str:
        """Format review data for GitHub PR comment"""
        comment = review_data.get("comment", "")

        # Add header with commit info
        commit_hash = review_data.get("commit", "unknown")[:7]
        header = f"## 🤖 Automated Code Review for commit `{commit_hash}`\n\n"

        # Add footer with instructions
        footer = "\n\n---\n*This is an automated review. Fix the issues and push again.*"

        return header + comment + footer

    def post_comments_for_commits(self, commit_hashes: List[str]) -> int:
        """Post review comments for multiple commits"""
        posted_count = 0
        review_dir = self.repo_root / ".git" / "review-comments"

        for commit_hash in commit_hashes:
            review_file = review_dir / f"{commit_hash}.json"

            if not review_file.exists():
                print(f"ℹ️  No review comments for commit {commit_hash[:7]}")
                continue

            # Load review data
            with open(review_file, "r") as f:
                review_data = json.load(f)

            # Skip if no errors
            if not review_data.get("errors"):
                print(f"✅ No issues found for commit {commit_hash[:7]}")
                continue

            # Get PR number
            pr_number = self._get_pr_number_for_commit(commit_hash)
            if not pr_number:
                continue

            # Format and post comment
            comment_body = self._format_review_for_pr(review_data)
            if self._post_pr_comment(pr_number, comment_body):
                posted_count += 1

        return posted_count

    def post_comments_for_push(self) -> int:
        """Post review comments for commits being pushed"""
        try:
            # Get commits being pushed (not yet on remote)
            result = subprocess.run(
                ["git", "log", "@{u}..", "--format=%H"], capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                # No upstream branch, get all commits on current branch
                result = subprocess.run(
                    ["git", "log", "--format=%H"], capture_output=True, text=True, check=True
                )

            commit_hashes = result.stdout.strip().split("\n")
            commit_hashes = [h for h in commit_hashes if h]  # Remove empty strings

            if not commit_hashes:
                print("ℹ️  No commits to review")
                return 0

            print(f"📝 Checking {len(commit_hashes)} commit(s) for review comments...")
            return self.post_comments_for_commits(commit_hashes)

        except Exception as e:
            print(f"Error: {e}")
            return 0


def main():
    """Main entry point"""
    print("🚀 GitHub PR Comment Poster")
    print("=" * 60)

    poster = PRCommentPoster()

    print(f"Repository: {poster.repo_info['owner']}/{poster.repo_info['repo']}")
    print()

    # Post comments for commits being pushed
    posted_count = poster.post_comments_for_push()

    print()
    print("=" * 60)
    if posted_count > 0:
        print(f"✅ Posted {posted_count} review comment(s) to PR")
    else:
        print("ℹ️  No review comments posted")

    return 0 if posted_count >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
