#!/usr/bin/env python3
"""
GitHub Webhook Server for PR Code Review
- Handles pull_request events only
- Runs ruff + pytest on PR diff
- Updates GitHub commit status
- Posts deduplicated PR comments
"""

import hashlib
import hmac
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

import requests
from flask import Flask, jsonify, request

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

BOT_MARKER = "<!-- code-review-bot -->"
STATUS_CONTEXT = "code-review/pre-commit"

GITHUB_API_BASE = "https://api.github.com"

if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN not set")

app = Flask(__name__)

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------


def verify_signature(payload: bytes, signature_header: str) -> bool:
    if not WEBHOOK_SECRET:
        return True

    if not signature_header:
        return False

    algo, github_sig = signature_header.split("=")
    digest = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(digest, github_sig)


def run(cmd: List[str], cwd: Path, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


# ------------------------------------------------------------------------------
# GitHub API
# ------------------------------------------------------------------------------


class GitHubClient:
    def __init__(self, repo: str):
        self.repo = repo
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

    def set_status(self, sha: str, state: str, description: str):
        url = f"{GITHUB_API_BASE}/repos/{self.repo}/statuses/{sha}"
        payload = {
            "state": state,
            "description": description,
            "context": STATUS_CONTEXT,
        }
        requests.post(url, headers=self.headers, json=payload, timeout=10)

    def list_pr_comments(self, pr_number: int) -> List[Dict]:
        url = f"{GITHUB_API_BASE}/repos/{self.repo}/issues/{pr_number}/comments"
        resp = requests.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def delete_comment(self, comment_id: int):
        url = f"{GITHUB_API_BASE}/repos/{self.repo}/issues/comments/{comment_id}"
        requests.delete(url, headers=self.headers, timeout=10)

    def post_pr_comment(self, pr_number: int, body: str):
        url = f"{GITHUB_API_BASE}/repos/{self.repo}/issues/{pr_number}/comments"
        requests.post(url, headers=self.headers, json={"body": body}, timeout=10)


# ------------------------------------------------------------------------------
# Code Reviewer
# ------------------------------------------------------------------------------


class CodeReviewer:
    def __init__(self, repo_url: str, base_ref: str, head_sha: str):
        self.repo_url = repo_url
        self.base_ref = base_ref
        self.head_sha = head_sha
        self.workdir = Path(tempfile.mkdtemp(prefix="pr-review-"))
        self.errors: List[Dict] = []

    def cleanup(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    def clone_repo(self):
        run(["git", "clone", self.repo_url, "."], self.workdir)
        run(["git", "fetch", "origin", self.base_ref], self.workdir)
        run(["git", "checkout", self.head_sha], self.workdir)

    def changed_python_files(self) -> List[str]:
        result = run(
            ["git", "diff", "--name-only", f"origin/{self.base_ref}", self.head_sha],
            self.workdir,
        )
        return [f for f in result.stdout.splitlines() if f.endswith(".py")]

    def run_ruff(self, files: List[str]):
        if not files:
            return

        proc = subprocess.run(
            ["ruff", "check", "--output-format=json"] + files,
            cwd=self.workdir,
            capture_output=True,
            text=True,
        )

        if proc.stdout:
            issues = json.loads(proc.stdout)
            for i in issues:
                self.errors.append(
                    {
                        "file": i["filename"],
                        "line": i["location"]["row"],
                        "column": i["location"]["column"],
                        "code": i["code"],
                        "message": i["message"],
                    }
                )

    def run_format_check(self, files: List[str]):
        if not files:
            return

        proc = subprocess.run(
            ["ruff", "format", "--check"] + files,
            cwd=self.workdir,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            for f in files:
                self.errors.append(
                    {
                        "file": f,
                        "line": 1,
                        "column": 1,
                        "code": "FORMAT",
                        "message": "File is not properly formatted",
                    }
                )

    def run_pytest(self):
        proc = subprocess.run(
            ["pytest", "-q"],
            cwd=self.workdir,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            self.errors.append(
                {
                    "file": "tests/",
                    "line": 1,
                    "column": 1,
                    "code": "TEST",
                    "message": "Tests failed",
                }
            )

    def run_all(self) -> bool:
        files = self.changed_python_files()
        self.run_ruff(files)
        self.run_format_check(files)
        self.run_pytest()
        return not self.errors

    def build_comment(self) -> str:
        body = f"{BOT_MARKER}\n## 🔍 Code Review Results\n\n"
        if not self.errors:
            return body + "✅ All checks passed!"

        body += f"❌ Found **{len(self.errors)}** issue(s):\n\n"
        for e in self.errors:
            body += (
                f"- `{e['file']}` **{e['line']}:{e['column']}** `{e['code']}` — {e['message']}\n"
            )
        return body


# ------------------------------------------------------------------------------
# Webhook Handler
# ------------------------------------------------------------------------------


@app.route("/webhook", methods=["POST"])
def webhook():
    if not verify_signature(
        request.data,
        request.headers.get("X-Hub-Signature-256", ""),
    ):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.headers.get("X-GitHub-Event")
    payload = request.json

    if event != "pull_request":
        return jsonify({"message": "Ignored"}), 200

    action = payload["action"]
    if action not in ("opened", "synchronize"):
        return jsonify({"message": "Ignored"}), 200

    pr = payload["pull_request"]
    repo = payload["repository"]["full_name"]
    pr_number = pr["number"]
    base_ref = pr["base"]["ref"]
    head_sha = pr["head"]["sha"]
    clone_url = payload["repository"]["clone_url"]

    gh = GitHubClient(repo)
    gh.set_status(head_sha, "pending", "Running code quality checks")

    reviewer = CodeReviewer(clone_url, base_ref, head_sha)

    try:
        reviewer.clone_repo()
        success = reviewer.run_all()
    except Exception as e:
        gh.set_status(head_sha, "error", "CI execution failed")
        raise e
    finally:
        reviewer.cleanup()

    # Clean old bot comments
    for c in gh.list_pr_comments(pr_number):
        if BOT_MARKER in c["body"]:
            gh.delete_comment(c["id"])

    if success:
        gh.set_status(head_sha, "success", "All checks passed")
    else:
        gh.set_status(
            head_sha,
            "failure",
            f"Found {len(reviewer.errors)} issue(s)",
        )
        gh.post_pr_comment(pr_number, reviewer.build_comment())

    return jsonify({"success": success}), 200


# ------------------------------------------------------------------------------
# Health
# ------------------------------------------------------------------------------


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "github_token": bool(GITHUB_TOKEN),
            "webhook_secret": bool(WEBHOOK_SECRET),
        }
    )


# ------------------------------------------------------------------------------
# Entry
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
