#!/usr/bin/env python3
"""
GitHub Push Script for nuttyfi32 Package
This script:
1. Initializes git repo if needed (first time)
2. Adds ALL project files
3. Commits changes
4. Pushes to GitHub Master branch
5. Creates/updates GitHub release with ZIP file
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
REPO_URL = "https://github.com/itsbhupendrasingh/nuttyfi32.git"
BRANCH = "Master"
ZIP_FILE = BASE_DIR / f"nuttyfi32-{VERSION}.zip"
JSON_FILE = BASE_DIR / "package_nuttyfi32_index.json"

# Files to include in git
INCLUDE_FILES = [
    "package_nuttyfi32_index.json",
    "build_nuttyfi32_complete.py",
    "push_to_github.py",
    "build_and_push.bat",
    "README.md",
    "QUICK_START.md",
    f"nuttyfi32-{VERSION}.zip",  # ZIP file (if exists)
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    ".git",
    "temp_build",
    "arduino-esp32-master",
    "esp32-*.zip",
    ".gitignore",
]

def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Run shell command"""
    if isinstance(cmd, str):
        print(f"Running: {cmd}")
    else:
        print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or BASE_DIR,
            shell=isinstance(cmd, str),
            check=check,
            capture_output=capture_output,
            text=True
        )
        if capture_output and result.stdout:
            return result.stdout.strip()
        if not capture_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed!")
        if isinstance(cmd, list):
            print(f"  Command: {' '.join(cmd)}")
        else:
            print(f"  Command: {cmd}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        if check:
            raise
        return e

def check_git_installed():
    """Check if git is installed"""
    try:
        run_command(["git", "--version"], check=True, capture_output=True)
        return True
    except:
        print("ERROR: Git is not installed or not in PATH!")
        print("Please install Git from: https://git-scm.com/downloads")
        return False

def init_git_repo():
    """Initialize git repository"""
    git_dir = BASE_DIR / ".git"
    
    is_new_repo = False
    if not git_dir.exists():
        print("Initializing new git repository...")
        run_command(["git", "init"])
        run_command(["git", "branch", "-M", BRANCH])
        is_new_repo = True
        print("  ✓ Git repository initialized")
    else:
        print("Git repository already exists")
    
    # Check if remote exists
    try:
        remote_url = run_command(["git", "remote", "get-url", "origin"], check=True, capture_output=True)
        if remote_url != REPO_URL:
            print(f"Updating remote URL to: {REPO_URL}")
            run_command(["git", "remote", "set-url", "origin", REPO_URL])
        else:
            print(f"  ✓ Remote already set: {REPO_URL}")
    except:
        print(f"Adding remote: {REPO_URL}")
        run_command(["git", "remote", "add", "origin", REPO_URL])
        print("  ✓ Remote added")
    
    return is_new_repo

def create_gitignore():
    """Create .gitignore file"""
    gitignore_file = BASE_DIR / ".gitignore"
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Build files
temp_build/
*.zip
!nuttyfi32-*.zip

# ESP32 BSP source (don't commit large source files)
arduino-esp32-master/
esp32-*.zip

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
"""
    
    if not gitignore_file.exists():
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("  ✓ Created .gitignore file")
        return True
    return False

def add_files_to_git():
    """Add files to git"""
    print("Adding files to git...")
    
    # Create .gitignore first
    gitignore_created = create_gitignore()
    if gitignore_created:
        run_command(["git", "add", ".gitignore"])
    
    # Add all files that exist
    files_added = []
    for file_pattern in INCLUDE_FILES:
        file_path = BASE_DIR / file_pattern
        if file_path.exists():
            run_command(["git", "add", str(file_path.relative_to(BASE_DIR))])
            files_added.append(file_path.name)
            print(f"  ✓ Added: {file_path.name}")
        else:
            print(f"  ⚠ Skipped (not found): {file_pattern}")
    
    # Also add README and other docs if they exist
    doc_files = ["README.md", "QUICK_START.md"]
    for doc_file in doc_files:
        doc_path = BASE_DIR / doc_file
        if doc_path.exists():
            try:
                run_command(["git", "add", str(doc_path.relative_to(BASE_DIR))], check=False)
                if doc_file not in files_added:
                    files_added.append(doc_file)
                    print(f"  ✓ Added: {doc_file}")
            except:
                pass
    
    return files_added

def commit_changes(is_first_commit=False):
    """Commit changes"""
    print("Committing changes...")
    
    # Check if there are changes
    try:
        status_result = run_command(["git", "status", "--porcelain"], check=False, capture_output=True)
        if not status_result or not status_result.strip():
            print("  ⚠ No changes to commit")
            return False
    except:
        pass
    
    # Commit
    if is_first_commit:
        commit_message = f"Initial commit: nuttyfi32 package v{VERSION}"
    else:
        commit_message = f"Update nuttyfi32 package v{VERSION}"
    
    try:
        run_command(["git", "commit", "-m", commit_message])
        print(f"  ✓ Committed: {commit_message}")
        return True
    except Exception as e:
        print(f"  ⚠ Commit failed: {e}")
        return False

def push_to_github(is_first_push=False):
    """Push to GitHub"""
    print(f"Pushing to {REPO_URL} branch {BRANCH}...")
    
    try:
        if is_first_push:
            # First push - set upstream
            run_command(["git", "push", "-u", "origin", BRANCH, "--force"])
        else:
            # Subsequent pushes
            run_command(["git", "push", "origin", BRANCH, "--force"])
        
        print(f"  ✓ Pushed to {BRANCH} branch")
        return True
    except Exception as e:
        print(f"  ❌ Push failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if repository exists at: https://github.com/itsbhupendrasingh/nuttyfi32")
        print("2. Verify you have push access")
        print("3. Check your Git credentials")
        return False

def show_summary(files_added, is_first_time):
    """Show summary"""
    print("\n" + "=" * 70)
    print(" " * 20 + "GitHub Push Summary")
    print("=" * 70)
    
    print(f"\n📦 Files Added: {len(files_added)}")
    for file in files_added:
        print(f"   ✓ {file}")
    
    print(f"\n🌿 Branch: {BRANCH}")
    print(f"🔗 Repository: {REPO_URL}")
    
    if is_first_time:
        print("\n✅ First-time push completed!")
        print("\n📋 Next Steps:")
        print("1. Verify files on GitHub:")
        print(f"   https://github.com/itsbhupendrasingh/nuttyfi32/tree/{BRANCH}")
        print("\n2. Create GitHub Release:")
        print("   https://github.com/itsbhupendrasingh/nuttyfi32/releases/new")
        print(f"   - Tag: {VERSION}")
        print(f"   - Title: nuttyfi32 v{VERSION}")
        if ZIP_FILE.exists():
            print(f"   - Upload: {ZIP_FILE.name}")
    else:
        print("\n✅ Push completed!")
    
    print("\n📄 Arduino IDE JSON URL:")
    print(f"   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/{BRANCH}/package_nuttyfi32_index.json")
    print("=" * 70)

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 20 + "nuttyfi32 GitHub Push Script")
    print("=" * 70)
    print()
    
    # Check git
    if not check_git_installed():
        input("\nPress Enter to exit...")
        return 1
    
    # Check files exist
    if not JSON_FILE.exists():
        print(f"ERROR: {JSON_FILE.name} not found!")
        print("Please run build_nuttyfi32_complete.py first")
        input("\nPress Enter to exit...")
        return 1
    
    try:
        # Initialize git
        print("\n[Step 1/4] Initializing Git Repository...")
        is_new_repo = init_git_repo()
        
        # Add files
        print("\n[Step 2/4] Adding Files to Git...")
        files_added = add_files_to_git()
        
        if not files_added:
            print("ERROR: No files to add!")
            input("\nPress Enter to exit...")
            return 1
        
        # Commit
        print("\n[Step 3/4] Committing Changes...")
        is_first_commit = is_new_repo
        commit_success = commit_changes(is_first_commit)
        
        if not commit_success and not is_new_repo:
            print("No changes to commit. Repository is up to date.")
            input("\nPress Enter to exit...")
            return 0
        
        # Push
        print("\n[Step 4/4] Pushing to GitHub...")
        is_first_push = is_new_repo
        push_success = push_to_github(is_first_push)
        
        if push_success:
            show_summary(files_added, is_first_push)
        else:
            print("\n⚠️  Push failed. You may need to:")
            print("1. Create the repository on GitHub first")
            print("2. Set up authentication (SSH keys or personal access token)")
            print("3. Try pushing manually: git push -u origin Master")
        
        input("\nPress Enter to continue...")
        return 0 if push_success else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    exit(main())
