#!/usr/bin/env python3
"""
Retry Push - Push already committed BSP files
"""

import subprocess
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

def retry_push():
    """Retry pushing to GitHub"""
    print("=" * 70)
    print(" " * 20 + "Retry Push to GitHub")
    print("=" * 70)
    print()
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Token required!")
        return False
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Set remote
    print("[Step 1/3] Setting remote URL...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", repo_url],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Remote configured")
    
    # Check if there are commits to push
    print("\n[Step 2/3] Checking commits...")
    result = subprocess.run(
        ["git", "log", "--oneline", f"origin/{BRANCH}..HEAD"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )
    
    commits_to_push = result.stdout.strip()
    if not commits_to_push:
        print("  ℹ️  No new commits to push")
        print("  Checking if branch is ahead...")
        result = subprocess.run(
            ["git", "status", "-sb"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    else:
        print(f"  Commits to push:")
        for line in commits_to_push.split('\n'):
            if line.strip():
                print(f"    • {line}")
    
    # Push
    print("\n[Step 3/3] Pushing to GitHub...")
    print("  ⚠️  This will take time (large files)...")
    print("  Please wait, do not close this window...")
    
    try:
        result = subprocess.run(
            ["git", "push", "-u", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=True,
            timeout=1200,
            capture_output=True,
            text=True
        )
        
        print("\n" + result.stdout)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📦 Pushed to GitHub!")
        print(f"🔗 Repository: https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {BRANCH}")
        print("=" * 70)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed!")
        print(f"  Exit code: {e.returncode}")
        if e.stdout:
            print(f"\n  Output:\n{e.stdout}")
        if e.stderr:
            print(f"\n  Error:\n{e.stderr}")
        
        error_text = (e.stderr or e.stdout or "").lower()
        if "authentication" in error_text or "token" in error_text or "unauthorized" in error_text:
            print("\n  ⚠️  Authentication failed!")
            print("  Check your token in .github_token file")
        elif "repository not found" in error_text:
            print("\n  ⚠️  Repository not found!")
        elif "secret" in error_text or "push protection" in error_text:
            print("\n  ⚠️  GitHub push protection!")
            print("  Check: https://github.com/itsbhupendrasingh/nuttyfi32/security/secret-scanning")
        
        return False
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (20 minutes)")
        return False

if __name__ == "__main__":
    try:
        success = retry_push()
        input("\nPress Enter to exit...")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        exit(1)



