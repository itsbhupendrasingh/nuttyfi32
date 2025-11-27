#!/usr/bin/env python3
"""
Simple Script to Delete ALL Files from GitHub Repo
This will empty the entire repository
"""

import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"

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
    
    print("\n⚠️  Token not found!")
    token = input("Enter GitHub Personal Access Token: ").strip()
    return token if token else None

def delete_all_files():
    """Delete ALL files from GitHub repo"""
    print("=" * 70)
    print(" " * 15 + "Delete ALL Files from GitHub")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will DELETE ALL files from the repository!")
    print()
    confirm = input("Are you sure? Type 'DELETE ALL' to confirm: ").strip()
    if confirm != "DELETE ALL":
        print("Cancelled.")
        return False
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Token required!")
        return False
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Set remote
    print("\n[Step 1/4] Setting remote URL...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", repo_url],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Remote configured")
    
    # Get all tracked files
    print("\n[Step 2/4] Getting list of all files in repo...")
    result = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True)
    tracked_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    
    if tracked_files:
        print(f"  Found {len(tracked_files)} files to delete")
        
        # Remove all files from git
        print("\n[Step 3/4] Removing all files from git...")
        for file in tracked_files:
            subprocess.run(["git", "rm", "-r", "--cached", file], cwd=BASE_DIR, check=False, capture_output=True)
        print(f"  ✓ Removed {len(tracked_files)} files")
        
        # Commit deletion
        print("\n[Step 4/4] Committing deletion...")
        subprocess.run(
            ["git", "commit", "-m", "Delete all files - empty repository"],
            cwd=BASE_DIR,
            check=True
        )
        print("  ✓ Deletion committed")
        
        # Push
        print("\nPushing to GitHub...")
        print("  This will delete ALL files from the repository!")
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=300
        )
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print("\n📦 All files deleted from GitHub repository")
        print(f"🌿 Branch: {BRANCH}")
        print(f"\n🔗 Repository: https://github.com/itsbhupendrasingh/nuttyfi32")
        print("=" * 70)
        return True
    else:
        print("  ℹ️  Repository is already empty")
        return True

def main():
    """Main function"""
    try:
        success = delete_all_files()
        if success:
            print("\n✅ Repository is now empty!")
        else:
            print("\n❌ Failed to delete files")
        
        print("\n" + "=" * 70)
        input("Press Enter to exit...")
        return 0 if success else 1
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        print("\nError details:")
        if hasattr(e, 'stderr') and e.stderr:
            print(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
        input("\nPress Enter to exit...")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    exit(main())



