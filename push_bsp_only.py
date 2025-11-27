#!/usr/bin/env python3
"""
Push ONLY arduino-esp32-master folder to GitHub
This script pushes ONLY the BSP source code, nothing else
"""

import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"
BSP_FOLDER = BASE_DIR / "arduino-esp32-master"

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

def push_bsp_only():
    """Push ONLY arduino-esp32-master folder"""
    print("=" * 70)
    print(" " * 15 + "Push BSP Source Code to GitHub")
    print("=" * 70)
    print()
    
    # Check if BSP folder exists
    if not BSP_FOLDER.exists():
        print(f"❌ ERROR: {BSP_FOLDER} folder not found!")
        return False
    
    print(f"📁 BSP Folder: {BSP_FOLDER}")
    print(f"🌿 Branch: {BRANCH}")
    print()
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Token required!")
        return False
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Set remote
    print("[Step 1/5] Configuring remote...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", repo_url],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Remote configured")
    
    # Check current status
    print("\n[Step 2/5] Checking git status...")
    result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
    current_status = result.stdout.strip()
    
    # Remove arduino-esp32-master from git if it exists (to re-add fresh)
    print("\n[Step 3/5] Preparing arduino-esp32-master folder...")
    subprocess.run(["git", "rm", "-r", "--cached", "arduino-esp32-master"], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Add ONLY arduino-esp32-master folder
    print("  Adding arduino-esp32-master/ folder (ALL files and folders)...")
    result = subprocess.run(
        ["git", "add", "-f", "arduino-esp32-master/"],
        cwd=BASE_DIR,
        check=True,
        capture_output=True,
        text=True
    )
    
    # Count files
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(BSP_FOLDER):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        file_count += len([f for f in files if not f.startswith('.')])
        dir_count += len(dirs)
    
    print(f"  ✓ Added {file_count} files from {dir_count} folders")
    
    # Check what's staged (only arduino-esp32-master files)
    print("\n[Step 4/5] Checking staged files...")
    result = subprocess.run(["git", "status", "--porcelain", "--cached"], cwd=BASE_DIR, capture_output=True, text=True)
    staged_files = result.stdout.strip()
    
    if not staged_files:
        print("  ⚠️  No files staged!")
        print("  Checking full status...")
        result = subprocess.run(["git", "status"], cwd=BASE_DIR, capture_output=True, text=True)
        print(result.stdout)
        return False
    
    # Count staged files
    staged_count = len([line for line in staged_files.split('\n') if line.strip() and 'arduino-esp32-master' in line])
    print(f"  ✓ {staged_count} files staged for commit")
    
    # Show first few files
    print("\n  Sample files to be pushed:")
    lines = staged_files.split('\n')[:5]
    for line in lines:
        if line.strip() and 'arduino-esp32-master' in line:
            file = line[3:].strip()
            print(f"    • {file}")
    if staged_count > 5:
        print(f"    ... and {staged_count - 5} more files")
    
    # Commit
    print("\n[Step 5/5] Committing and pushing...")
    print("  Committing changes...")
    subprocess.run(
        ["git", "commit", "-m", "Add nuttyfi32 BSP source code (arduino-esp32-master)"],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Committed")
    
    # Push
    print("\n  Pushing to GitHub...")
    print("  ⚠️  This will take time (large files)...")
    print("  Please wait, do not close this window...")
    
    try:
        result = subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=1200,  # 20 minutes
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📦 BSP source code pushed to GitHub!")
        print(f"🔗 Repository: https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {BRANCH}")
        print(f"📁 Folder: arduino-esp32-master/ ({file_count} files)")
        print("\n📋 Note: ZIP file should be uploaded via GitHub Releases")
        print("=" * 70)
        return True
        
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (20 minutes)")
        print("  Large files may need more time")
        print("  Try: git push -u origin Master (manually)")
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed!")
        print(f"  Exit code: {e.returncode}")
        if e.stdout:
            print(f"\n  Output:\n{e.stdout}")
        if e.stderr:
            print(f"\n  Error:\n{e.stderr}")
        
        # Check if it's a token/authentication issue
        error_text = (e.stderr or e.stdout or "").lower()
        if "authentication" in error_text or "token" in error_text or "unauthorized" in error_text:
            print("\n  ⚠️  Authentication failed!")
            print("  Check your token in .github_token file")
        elif "repository not found" in error_text:
            print("\n  ⚠️  Repository not found!")
            print("  Check repository URL and permissions")
        elif "secret" in error_text or "push protection" in error_text:
            print("\n  ⚠️  GitHub push protection detected!")
            print("  Token might be in code. Check scripts for hardcoded tokens.")
        
        return False

def main():
    """Main function"""
    try:
        success = push_bsp_only()
        
        if not success:
            print("\n❌ Failed to push BSP source code")
        
        print("\n" + "=" * 70)
        input("Press Enter to exit...")
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        input("Press Enter to exit...")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    exit(main())

