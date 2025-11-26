#!/usr/bin/env python3
"""
Quick Push Script with Token
This script pushes to GitHub using the provided token
"""

import subprocess
from pathlib import Path

import os

BASE_DIR = Path(__file__).parent
BRANCH = "Master"
REPO_URL = "https://github.com/itsbhupendrasingh/nuttyfi32.git"

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

def push_with_token():
    """Push using token in URL"""
    print("=" * 70)
    print("Pushing to GitHub with Token...")
    print("=" * 70)
    print()
    
    # Configure remote with token
    remote_with_token = f"https://{TOKEN}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    try:
        # Set remote URL with token
        print("Setting remote URL with token...")
        subprocess.run(
            ["git", "remote", "set-url", "origin", remote_with_token],
            cwd=BASE_DIR,
            check=True
        )
        print("  ✓ Remote configured")
        
        # Add files - including ESP32 BSP source
        print("\nAdding files to git...")
        
        # Add ESP32 BSP source folder (most important - this is the main source code)
        bsp_source = BASE_DIR / "arduino-esp32-master"
        if bsp_source.exists():
            print(f"  Adding ESP32 BSP source: arduino-esp32-master/")
            subprocess.run(["git", "add", "arduino-esp32-master/"], cwd=BASE_DIR, check=False)
            print(f"  ✓ Added: arduino-esp32-master/ (entire folder with nuttyfi32 changes)")
        
        # Add other files
        files_to_add = [
            "package_nuttyfi32_index.json",
            "build_nuttyfi32_complete.py",
            "push_to_github.py",
            "build_and_push.bat",
            "README.md",
            "QUICK_START.md",
            "GITHUB_SETUP.md",
            "FIX_GITHUB_PUSH.md",
            "PERSONAL_ACCESS_TOKEN_GUIDE.md",
            "check_github_setup.py",
        ]
        
        for file in files_to_add:
            file_path = BASE_DIR / file
            if file_path.exists():
                subprocess.run(["git", "add", str(file_path.relative_to(BASE_DIR))], cwd=BASE_DIR, check=False)
                print(f"  ✓ Added: {file}")
        
        # Check if there are changes
        result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
        if not result.stdout.strip():
            print("\n⚠️  No changes to commit")
            return True
        
        # Commit
        print("\nCommitting changes...")
        subprocess.run(
            ["git", "commit", "-m", "Update nuttyfi32 package v1.0.0"],
            cwd=BASE_DIR,
            check=True
        )
        print("  ✓ Committed")
        
        # Push
        print(f"\nPushing to {BRANCH} branch...")
        print("  (This may take a few minutes...)")
        
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=600  # 10 minutes
        )
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Pushed to GitHub!")
        print("=" * 70)
        print(f"\n📄 Files pushed to: {REPO_URL}")
        print(f"🌿 Branch: {BRANCH}")
        print("\n📋 Next Step:")
        print("   Upload ZIP file via GitHub Release:")
        print("   https://github.com/itsbhupendrasingh/nuttyfi32/releases/new")
        print("   - Tag: 1.0.0")
        print("   - Upload: nuttyfi32-1.0.0.zip")
        print("=" * 70)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("\n⚠️  Push timeout. Large files may take longer.")
        print("   Try: git push -u origin Master (manually)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = push_with_token()
    input("\nPress Enter to continue...")
    exit(0 if success else 1)

