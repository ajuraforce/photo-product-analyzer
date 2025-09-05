#!/usr/bin/env python3
"""
Script to push the project source code to GitHub
Requires GitHub personal access token, repository owner, and repository name to be set as environment variables
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """Execute a shell command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_git_status():
    """Check if we're in a git repository"""
    if not Path(".git").exists():
        print("📁 Initializing git repository...")
        if not run_command("git init", "Initializing git repository"):
            return False
    return True

def setup_git_config():
    """Setup basic git configuration if not already set"""
    result = subprocess.run("git config --global user.email", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        run_command('git config --global user.email "action@github.com"', "Setting default git email")
    
    result = subprocess.run("git config --global user.name", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        run_command('git config --global user.name "GitHub Action"', "Setting default git name")

def add_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
credentials.json
*.log
temp/
tmp/

# Uploads (keep structure but ignore files)
static_server/uploads/*
!static_server/uploads/.gitkeep

# Development
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create .gitkeep for uploads directory
    uploads_dir = Path("static_server/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    (uploads_dir / ".gitkeep").touch()
    
    print("✅ Updated .gitignore and created upload directory structure")

def main():
    """Main function to push code to GitHub"""
    print("🚀 GitHub Push Script")
    print("=" * 50)
    
    # Get environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("GITHUB_OWNER")
    repo_name = os.getenv("GITHUB_REPO")
    
    if not all([github_token, repo_owner, repo_name]):
        print("❌ Missing required environment variables:")
        if not github_token:
            print("   - GITHUB_TOKEN: Your GitHub Personal Access Token")
        if not repo_owner:
            print("   - GITHUB_OWNER: Your GitHub username or organization")
        if not repo_name:
            print("   - GITHUB_REPO: Repository name")
        print("\nPlease set these environment variables and try again.")
        sys.exit(1)
    
    # Check git status
    if not check_git_status():
        sys.exit(1)
    
    # Setup git configuration
    setup_git_config()
    
    # Add/update .gitignore
    add_gitignore()
    
    # Set up remote URL with token
    remote_url = f"https://{github_token}@github.com/{repo_owner}/{repo_name}.git"
    
    print(f"📡 Repository: {repo_owner}/{repo_name}")
    
    # Check if remote exists
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("🔗 Adding remote origin...")
        if not run_command(f"git remote add origin {remote_url}", "Adding remote origin"):
            sys.exit(1)
    else:
        print("🔄 Updating remote origin...")
        if not run_command(f"git remote set-url origin {remote_url}", "Updating remote origin"):
            sys.exit(1)
    
    # Stage all files
    if not run_command("git add .", "Staging all files"):
        sys.exit(1)
    
    # Check if there are changes to commit
    result = subprocess.run("git diff --staged --quiet", shell=True)
    if result.returncode == 0:
        print("ℹ️  No changes to commit")
    else:
        # Commit changes
        commit_message = "Update project source code"
        if not run_command(f'git commit -m "{commit_message}"', f"Committing changes: {commit_message}"):
            sys.exit(1)
    
    # Push to GitHub
    if not run_command("git push -u origin main", "Pushing to GitHub"):
        # Try master branch if main fails
        print("🔄 Trying master branch...")
        if not run_command("git push -u origin master", "Pushing to GitHub (master branch)"):
            sys.exit(1)
    
    print("\n🎉 Successfully pushed to GitHub!")
    print(f"🔗 Repository URL: https://github.com/{repo_owner}/{repo_name}")

if __name__ == "__main__":
    main()