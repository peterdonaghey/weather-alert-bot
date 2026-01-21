#!/bin/bash

# Script to manually trigger the GitHub Actions workflow
# This sends weather reports to all subscribers

set -e

echo "🚀 Triggering weather check workflow..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Install it: brew install gh"
    echo "Or use the Python script instead: python trigger_workflow.py"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

# Get repo info
REPO=$(git remote get-url origin | sed -E 's/.*github.com[:/](.*)\.git/\1/')
OWNER=$(echo $REPO | cut -d'/' -f1)
REPO_NAME=$(echo $REPO | cut -d'/' -f2)

echo "📦 Repository: $OWNER/$REPO_NAME"
echo ""

# Trigger workflow
echo "⏳ Triggering workflow..."
gh workflow run weather-check.yml --repo "$OWNER/$REPO_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "View progress:"
    echo "  gh run list --repo $OWNER/$REPO_NAME --workflow=weather-check.yml"
    echo ""
    echo "Watch logs:"
    echo "  gh run watch --repo $OWNER/$REPO_NAME"
else
    echo "❌ Failed to trigger workflow"
    exit 1
fi
