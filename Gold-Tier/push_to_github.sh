#!/bin/bash

# Script to push Bronze Tier project to GitHub
# Repository: https://github.com/AnamShergill/Hackathon_0-Bronze-Tier.git

echo "=========================================="
echo "Pushing Bronze Tier to GitHub"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Check if README_GITHUB.md exists and rename it
if [ -f README_GITHUB.md ]; then
    echo "📝 Using GitHub README..."
    mv README.md README_LOCAL.md 2>/dev/null || true
    mv README_GITHUB.md README.md
    echo "✅ README prepared for GitHub"
    echo ""
fi

# Add all files (respecting .gitignore)
echo "📁 Adding files to git..."
git add .
echo "✅ Files staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git status --short
echo ""

# Commit
echo "💾 Creating commit..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Bronze Tier Complete - AI Employee Vault v1.0"
fi
git commit -m "$commit_msg"
echo "✅ Commit created"
echo ""

# Add remote if not exists
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/AnamShergill/Hackathon_0-Bronze-Tier.git
    echo "✅ Remote added"
    echo ""
fi

# Set main branch
echo "🌿 Setting up main branch..."
git branch -M main
echo "✅ Branch set to main"
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo "⚠️  You may be prompted for GitHub credentials"
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Project pushed to GitHub"
    echo "=========================================="
    echo ""
    echo "🔗 Repository: https://github.com/AnamShergill/Hackathon_0-Bronze-Tier"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Add a description and topics"
    echo "3. Enable GitHub Pages (optional)"
    echo "4. Share with the community!"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Push failed"
    echo "=========================================="
    echo ""
    echo "Common issues:"
    echo "1. Authentication failed - Set up GitHub credentials"
    echo "2. Repository doesn't exist - Create it on GitHub first"
    echo "3. Permission denied - Check repository access"
    echo ""
    echo "Manual push command:"
    echo "git push -u origin main"
    echo ""
fi
