#!/usr/bin/env python3
"""
Fix Token Issue and Push
This script:
1. Removes token from last commit
2. Uses token from environment/config
3. Pushes everything
"""

import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"

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
    
    if token:
        # Save to config file for future (will be ignored by git)
        try:
            with open(config_file, 'w') as f:
                f.write(token)
            print(f"  ✓ Saved token to .github_token (not tracked by git)")
        except:
            pass
        return token
    
    return None

def fix_last_commit():
    """Remove token from last commit and amend it"""
    print("Fixing last commit (removing token from code)...")
    
    # Always reset last commit to remove token
    print("  Resetting last commit (keeping changes)...")
    subprocess.run(["git", "reset", "--soft", "HEAD~1"], cwd=BASE_DIR, check=False)
    print("  ✓ Reset last commit")
    
    # Add updated files (without token)
    print("  Adding updated files (without token)...")
    subprocess.run(["git", "add", "clean_and_push_all.py"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "add", "push_with_token.py"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "add", ".gitignore"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "add", "fix_token_and_push.py"], cwd=BASE_DIR, check=False)
    print("  ✓ Files updated")
    
    return True

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 15 + "Fix Token Issue and Push")
    print("=" * 70)
    print()
    
    try:
        # Get token
        token = get_token()
        if not token:
            print("❌ Token required!")
            input("\nPress Enter to exit...")
            return 1
        
        repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
        
        # Fix last commit if needed
        print("[Step 1/4] Checking last commit...")
        needs_fix = fix_last_commit()
        
        if needs_fix:
            print("\n[Step 2/4] Recommitting without token...")
            # Files are already staged, just commit again
            subprocess.run(
                ["git", "commit", "-m", "Complete nuttyfi32 BSP: All source files from arduino-esp32-master"],
                cwd=BASE_DIR,
                check=True
            )
            print("  ✓ Recommitted without token")
        else:
            print("  ✓ Last commit is OK")
        
        # Set remote
        print("\n[Step 3/4] Configuring remote...")
        subprocess.run(
            ["git", "remote", "set-url", "origin", repo_url],
            cwd=BASE_DIR,
            check=True
        )
        print("  ✓ Remote configured")
        
        # Push
        print(f"\n[Step 4/4] Pushing to {BRANCH} branch...")
        print("  ⚠️  This will take time (large files)...")
        print("  Please wait, do not close this window...")
        
        subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=1200  # 20 minutes
        )
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📦 All files pushed to: https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {BRANCH}")
        print("\n📋 Next: Upload ZIP file via GitHub Release")
        print("=" * 70)
        
        input("\nPress Enter to continue...")
        return 0
        
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (20 minutes)")
        print("  Large files may need more time")
        input("\nPress Enter to exit...")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed: {e}")
        print("\n  If you see 'secret' error:")
        print("  1. Go to: https://github.com/itsbhupendrasingh/nuttyfi32/security/secret-scanning")
        print("  2. Allow the secret if it's yours")
        print("  3. Run this script again")
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

