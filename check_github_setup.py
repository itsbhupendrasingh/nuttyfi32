#!/usr/bin/env python3
"""
GitHub Setup Diagnostic Script
This script checks if everything is ready for GitHub push
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
REPO_URL = "https://github.com/itsbhupendrasingh/nuttyfi32.git"
BRANCH = "Master"

def check_git():
    """Check if git is installed"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git installed: {result.stdout.strip()}")
            return True
    except:
        pass
    print("❌ Git not found!")
    print("   Install from: https://git-scm.com/downloads")
    return False

def check_repo_exists():
    """Check if repository exists on GitHub"""
    try:
        result = subprocess.run(
            ["git", "ls-remote", REPO_URL],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Repository exists on GitHub")
            return True
        else:
            print("❌ Repository not found on GitHub")
            print(f"   Create it at: https://github.com/new")
            print(f"   Name: nuttyfi32")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Cannot check repository (timeout)")
        return None
    except:
        print("❌ Cannot check repository (network issue?)")
        return None

def check_local_repo():
    """Check local git repository"""
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        print("✅ Local git repository initialized")
        
        # Check remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                print(f"✅ Remote configured: {remote_url}")
                if remote_url != REPO_URL:
                    print(f"   ⚠️  Expected: {REPO_URL}")
            else:
                print("❌ Remote not configured")
                print(f"   Run: git remote add origin {REPO_URL}")
        except:
            print("❌ Cannot check remote")
        
        # Check branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                print(f"✅ Current branch: {current_branch}")
                if current_branch != BRANCH:
                    print(f"   ⚠️  Expected: {BRANCH}")
                    print(f"   Run: git branch -M {BRANCH}")
        except:
            pass
        
        return True
    else:
        print("⚠️  Local git repository not initialized")
        print("   Will be initialized automatically on first push")
        return False

def check_credentials():
    """Check git credentials"""
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Git user.name: {result.stdout.strip()}")
        else:
            print("⚠️  Git user.name not set")
            print("   Run: git config --global user.name 'Your Name'")
    except:
        pass
    
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Git user.email: {result.stdout.strip()}")
        else:
            print("⚠️  Git user.email not set")
            print("   Run: git config --global user.email 'your@email.com'")
    except:
        pass
    
    print("\n📝 Authentication:")
    print("   For push, you'll need:")
    print("   - Personal Access Token (recommended)")
    print("   - Or SSH keys configured")
    print("   - GitHub → Settings → Developer settings → Personal access tokens")

def main():
    """Main diagnostic"""
    print("=" * 70)
    print(" " * 20 + "GitHub Setup Diagnostic")
    print("=" * 70)
    print()
    
    print("[1/4] Checking Git Installation...")
    git_ok = check_git()
    print()
    
    if not git_ok:
        print("\n❌ Git not installed. Please install Git first.")
        input("\nPress Enter to exit...")
        return 1
    
    print("[2/4] Checking Local Repository...")
    local_ok = check_local_repo()
    print()
    
    print("[3/4] Checking GitHub Repository...")
    remote_ok = check_repo_exists()
    print()
    
    print("[4/4] Checking Git Configuration...")
    check_credentials()
    print()
    
    print("=" * 70)
    print(" " * 20 + "Diagnostic Summary")
    print("=" * 70)
    
    if git_ok and (remote_ok or remote_ok is None):
        print("\n✅ Basic setup looks good!")
        print("\n📋 Next Steps:")
        if not remote_ok:
            print("1. Create repository: https://github.com/new (name: nuttyfi32)")
        print("2. Run: python build_nuttyfi32_complete.py")
        print("3. When prompted for credentials:")
        print("   - Username: your GitHub username")
        print("   - Password: Personal Access Token (not password)")
    else:
        print("\n⚠️  Some issues found. Please fix them above.")
    
    print("=" * 70)
    input("\nPress Enter to continue...")
    return 0

if __name__ == "__main__":
    exit(main())

