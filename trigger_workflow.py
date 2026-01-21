#!/usr/bin/env python3
"""
Manually trigger the GitHub Actions workflow.
Alternative to trigger_workflow.sh if you don't have gh CLI installed.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path


def get_repo_info():
    """Get repository owner and name from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()
        
        # Handle both SSH and HTTPS URLs
        if "github.com:" in url or "github.com/" in url:
            parts = url.replace(".git", "").split("github.com")[1]
            parts = parts.strip("/").replace(":", "/")
            owner, repo = parts.split("/")[-2:]
            return owner, repo
        else:
            raise ValueError("Could not parse GitHub URL")
    except Exception as e:
        print(f"❌ Error getting repo info: {e}")
        sys.exit(1)


def trigger_workflow(owner: str, repo: str, token: str):
    """Trigger the GitHub Actions workflow via API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/weather-check.yml/dispatches"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    payload = {
        "ref": "main",  # or "master" depending on your default branch
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 204:
        print("✅ Workflow triggered successfully!")
        print(f"\nView progress: https://github.com/{owner}/{repo}/actions")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    """Main entry point."""
    print("🚀 Triggering weather check workflow...\n")
    
    # Get repo info
    owner, repo = get_repo_info()
    print(f"📦 Repository: {owner}/{repo}\n")
    
    # Get GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set.")
        print("\nTo set it:")
        print("  1. Create a GitHub Personal Access Token:")
        print("     https://github.com/settings/tokens")
        print("     (needs 'repo' scope)")
        print("  2. Export it:")
        print("     export GITHUB_TOKEN=your_token_here")
        print("\nOr add it to your .env file:")
        print("     echo 'GITHUB_TOKEN=your_token_here' >> .env")
        sys.exit(1)
    
    # Trigger workflow
    print("⏳ Triggering workflow...")
    if trigger_workflow(owner, repo, token):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
