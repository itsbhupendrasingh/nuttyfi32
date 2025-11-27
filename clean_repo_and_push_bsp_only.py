#!/usr/bin/env python3
"""
Clean GitHub Repo and Push ONLY arduino-esp32-master folder
This script:
1. Removes ALL files from GitHub repo
2. Pushes ONLY arduino-esp32-master folder (source code)
3. Does NOT push script files, JSON files, etc.
"""

import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"
BSP_FOLDER = BASE_DIR / "arduino-esp32-master"

# Get token from .github_token file
def get_token():
    """Get GitHub token from .github_token file"""
    config_file = BASE_DIR / ".github_token"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                token = f.read().strip()
            if token:
                return token
        except:
            pass
    
    print("\n⚠️  Token not found in .github_token file!")
    token = input("Enter GitHub Personal Access Token: ").strip()
    return token if token else None

def clean_repo_completely():
    """Remove ALL files from git and GitHub"""
    print("=" * 70)
    print(" " * 10 + "Cleaning GitHub Repo - Removing ALL Files")
    print("=" * 70)
    print()
    
    # Remove everything from git tracking
    print("[Step 1/5] Removing all files from git...")
    
    # Get list of all tracked files
    result = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True)
    tracked_files = result.stdout.strip().split('\n')
    
    if tracked_files and tracked_files[0]:
        print(f"  Found {len(tracked_files)} tracked files to remove...")
        # Remove all tracked files
        for file in tracked_files:
            if file.strip():
                subprocess.run(["git", "rm", "--cached", file], cwd=BASE_DIR, check=False, capture_output=True)
        print("  ✓ All tracked files removed from git")
    else:
        print("  ℹ️  No tracked files found")
    
    # Reset staging
    subprocess.run(["git", "reset"], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Check if there are any staged deletions to commit
    result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
    changes = result.stdout.strip()
    
    if changes:
        # Check if there are deletions (D status)
        deletions = [line for line in changes.split('\n') if line.startswith('D ')]
        if deletions:
            print(f"\n[Step 2/5] Committing deletion of {len(deletions)} files...")
            subprocess.run(
                ["git", "commit", "-m", "Remove all files - preparing for BSP source only"],
                cwd=BASE_DIR,
                check=False
            )
            print("  ✓ Deletion committed")
        else:
            print("  ℹ️  No deletions to commit")
    else:
        print("  ℹ️  No changes to commit (repo already clean)")
    
    return True

def push_only_bsp():
    """Push ONLY arduino-esp32-master folder"""
    print("\n[Step 3/5] Adding ONLY arduino-esp32-master folder...")
    
    if not BSP_FOLDER.exists():
        print(f"  ❌ ERROR: {BSP_FOLDER} folder not found!")
        return False
    
    # First, check current status
    print("  Checking current git status...")
    status_result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
    
    # Remove arduino-esp32-master from git if it exists
    print("  Removing old arduino-esp32-master from git (if exists)...")
    subprocess.run(["git", "rm", "-r", "--cached", "arduino-esp32-master"], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Add ONLY arduino-esp32-master folder
    print(f"  Adding: arduino-esp32-master/ (ALL files and folders)")
    result = subprocess.run(
        ["git", "add", "-f", "arduino-esp32-master/"],
        cwd=BASE_DIR,
        check=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 and result.stderr:
        print(f"  ⚠️  Warning: {result.stderr[:200]}")
    
    # Count files
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(BSP_FOLDER):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        file_count += len([f for f in files if not f.startswith('.')])
        dir_count += len(dirs)
    
    print(f"  ✓ Added {file_count} files from {dir_count} folders")
    
    # Check what's staged (only staged files, not untracked)
    result = subprocess.run(["git", "status", "--porcelain", "--cached"], cwd=BASE_DIR, capture_output=True, text=True)
    staged_changes = result.stdout.strip()
    
    if not staged_changes:
        print("  ⚠️  No files staged! Checking status...")
        # Check full status
        result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
        all_changes = result.stdout.strip()
        if all_changes:
            print(f"  Found changes but not staged:")
            print(all_changes[:500])
        return False
    
    # Show what's being added (first 10 files)
    print(f"\n  Files staged for commit:")
    lines = staged_changes.split('\n')[:10]
    for line in lines:
        if line.strip():
            status = line[:2]
            file = line[3:]
            if 'arduino-esp32-master' in file:
                print(f"    {status} {file}")
    if len(staged_changes.split('\n')) > 10:
        print(f"    ... and {len(staged_changes.split('\n')) - 10} more files")
    
    return True

def commit_and_push():
    """Commit and push ONLY BSP folder"""
    print("\n[Step 4/5] Committing BSP source code...")
    
    # Check if there are staged changes
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=BASE_DIR, capture_output=True, text=True)
    staged_files = result.stdout.strip()
    
    if not staged_files:
        print("  ⚠️  No files staged for commit!")
        print("  Checking git status...")
        status_result = subprocess.run(["git", "status"], cwd=BASE_DIR, capture_output=True, text=True)
        print(status_result.stdout)
        return False
    
    print(f"  Committing {len(staged_files.split())} files...")
    
    subprocess.run(
        ["git", "commit", "-m", "Add nuttyfi32 BSP source code (arduino-esp32-master)"],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Committed")
    
    # Get token
    token = get_token()
    if not token:
        print("  ❌ Token required!")
        return False
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Set remote
    print("\n[Step 5/5] Configuring remote and pushing...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", repo_url],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Remote configured")
    
    # Push
    print(f"\n  Pushing to {BRANCH} branch...")
    print("  ⚠️  This will take time (large files)...")
    print("  Please wait, do not close this window...")
    
    try:
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=1200  # 20 minutes
        )
        print("\n  ✅ SUCCESS! BSP source code pushed to GitHub!")
        return True
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (20 minutes)")
        print("  Try: git push -u origin Master (manually)")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 10 + "Clean Repo & Push ONLY BSP Source")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Remove ALL files from GitHub repo")
    print("  2. Push ONLY arduino-esp32-master/ folder")
    print("  3. Script files, JSON files will NOT be pushed")
    print()
    print("⚠️  WARNING: This will delete everything in the repo!")
    print()
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return 1
    
    try:
        # Step 1 & 2: Clean repo
        clean_repo_completely()
        
        # Step 3: Add only BSP
        if not push_only_bsp():
            print("\n❌ Failed to add BSP folder")
            input("\nPress Enter to exit...")
            return 1
        
        # Step 4 & 5: Commit and push
        success = commit_and_push()
        
        if success:
            print("\n" + "=" * 70)
            print(" " * 20 + "✅ SUCCESS!")
            print("=" * 70)
            print(f"\n📦 BSP source code pushed to:")
            print(f"   https://github.com/itsbhupendrasingh/nuttyfi32")
            print(f"🌿 Branch: {BRANCH}")
            print(f"\n📁 Only arduino-esp32-master/ folder is in the repo")
            print("=" * 70)
        else:
            print("\n⚠️  Push failed")
        
        input("\nPress Enter to continue...")
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    exit(main())

