#!/usr/bin/env python3
"""
Complete Clean and Push Script
This script:
1. Removes old/unwanted files from git
2. Adds ALL files from arduino-esp32-master folder
3. Pushes everything to GitHub
"""

import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"

# Get token from environment variable or config file (NOT hardcoded for security)
def get_token():
    """Get GitHub token from environment variable or config file"""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    # Try config file (not tracked by git)
    config_file = BASE_DIR / ".github_token"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                token = f.read().strip()
            if token:
                return token
        except:
            pass
    
    # Prompt user if not found
    print("\n⚠️  GitHub token not found!")
    print("   Option 1: Set environment variable:")
    print("      set GITHUB_TOKEN=ghp_your_token_here")
    print("   Option 2: Create .github_token file with your token")
    print("   Option 3: Enter token now (will be used for this session only)")
    token = input("\nEnter GitHub Personal Access Token: ").strip()
    return token if token else None

TOKEN = get_token()
if not TOKEN:
    print("❌ Token required to push to GitHub")
    exit(1)

REPO_URL = f"https://{TOKEN}@github.com/itsbhupendrasingh/nuttyfi32.git"

def clean_git():
    """Remove all files from git, clean everything"""
    print("Cleaning git repository...")
    
    # Remove everything from git tracking
    try:
        subprocess.run(["git", "rm", "-r", "--cached", "."], cwd=BASE_DIR, check=False, capture_output=True)
    except:
        pass
    
    # Reset staging
    subprocess.run(["git", "reset"], cwd=BASE_DIR, check=False, capture_output=True)
    
    print("  ✓ Cleaned - ready to add all files fresh")

def add_all_files():
    """Add ALL files from arduino-esp32-master and project files"""
    print("\nAdding ALL files to git...")
    
    files_added = []
    
    # 1. Add .gitignore first
    gitignore = BASE_DIR / ".gitignore"
    if gitignore.exists():
        subprocess.run(["git", "add", ".gitignore"], cwd=BASE_DIR, check=False)
        files_added.append(".gitignore")
    
    # 2. Add ENTIRE arduino-esp32-master folder (ALL files, ALL subfolders)
    bsp_source = BASE_DIR / "arduino-esp32-master"
    if bsp_source.exists():
        print(f"  Adding arduino-esp32-master/ (COMPLETE - ALL files and folders)...")
        print(f"    This includes: cores/, libraries/, tools/, variants/, docs/, etc.")
        
        # Add entire folder recursively - ALL files
        result = subprocess.run(
            ["git", "add", "-f", "arduino-esp32-master/"], 
            cwd=BASE_DIR, 
            check=False,
            capture_output=True,
            text=True
        )
        
        # Count files being added
        file_count = 0
        dir_count = 0
        for root, dirs, files in os.walk(bsp_source):
            # Skip .git and other hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            file_count += len([f for f in files if not f.startswith('.')])
            dir_count += len(dirs)
        
        files_added.append(f"arduino-esp32-master/ ({file_count} files, {dir_count} folders - COMPLETE)")
        print(f"  ✓ Added {file_count} files from {dir_count} folders")
        
        if result.returncode != 0 and result.stderr:
            print(f"    Note: {result.stderr[:200]}")
    
    # 3. Add all project files
    project_files = [
        "package_nuttyfi32_index.json",
        "build_nuttyfi32_complete.py",
        "push_to_github.py",
        "push_with_token.py",
        "build_and_push.bat",
        "README.md",
        "QUICK_START.md",
        "GITHUB_SETUP.md",
        "FIX_GITHUB_PUSH.md",
        "PERSONAL_ACCESS_TOKEN_GUIDE.md",
        "check_github_setup.py",
        "clean_and_push_all.py",
    ]
    
    for file in project_files:
        file_path = BASE_DIR / file
        if file_path.exists():
            subprocess.run(["git", "add", str(file_path.relative_to(BASE_DIR))], cwd=BASE_DIR, check=False)
            files_added.append(file)
    
    print(f"\n  ✓ Total files/folders added: {len(files_added)}")
    return files_added

def commit_and_push():
    """Commit and push everything"""
    print("\nChecking changes...")
    
    # Check if there are changes
    result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
    changes = result.stdout.strip()
    
    if not changes:
        print("  ⚠️  No changes to commit")
        return False
    
    # Show what's being added
    print(f"  Files to commit:")
    lines = changes.split('\n')[:20]  # Show first 20
    for line in lines:
        if line.strip():
            status = line[:2]
            file = line[3:]
            print(f"    {status} {file}")
    if len(changes.split('\n')) > 20:
        print(f"    ... and {len(changes.split('\n')) - 20} more files")
    
    # Commit
    print("\nCommitting ALL files...")
    subprocess.run(
        ["git", "commit", "-m", "Complete nuttyfi32 BSP: All source files from arduino-esp32-master"],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Committed")
    
    # Set remote with token
    print("\nConfiguring remote with token...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", REPO_URL],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Remote configured")
    
    # Push
    print(f"\nPushing to {BRANCH} branch...")
    print("  ⚠️  This will take time (large files)...")
    print("  Please wait, do not close this window...")
    
    try:
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=1200  # 20 minutes for very large uploads
        )
        print("\n  ✅ SUCCESS! All files pushed to GitHub!")
        return True
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (20 minutes)")
        print("  Large files may need more time")
        print("  Try: git push -u origin Master (manually)")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 15 + "Complete Clean and Push - ALL Files")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Clean
        print("[Step 1/3] Cleaning git staging...")
        clean_git()
        
        # Step 2: Add all files
        print("\n[Step 2/3] Adding ALL files...")
        files_added = add_all_files()
        
        if not files_added:
            print("  ❌ No files to add!")
            input("\nPress Enter to exit...")
            return 1
        
        # Step 3: Commit and push
        print("\n[Step 3/3] Committing and pushing...")
        success = commit_and_push()
        
        if success:
            print("\n" + "=" * 70)
            print(" " * 20 + "✅ SUCCESS!")
            print("=" * 70)
            print(f"\n📦 All files pushed to: https://github.com/itsbhupendrasingh/nuttyfi32")
            print(f"🌿 Branch: {BRANCH}")
            print(f"\n📁 Files pushed:")
            for file in files_added:
                print(f"   ✓ {file}")
            print("\n📋 Next: Upload ZIP file via GitHub Release")
            print("=" * 70)
        else:
            print("\n⚠️  Push failed or no changes")
        
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

