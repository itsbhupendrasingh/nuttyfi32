#!/usr/bin/env python3
"""
Correct Script - Push files from arduino-esp32-master to GitHub ROOT
1. Remove ALL files from GitHub FIRST
2. Push files from arduino-esp32-master/ to ROOT (not the folder itself)
"""

import subprocess
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"
BSP_FOLDER = BASE_DIR / "arduino-esp32-master"
TEMP_COPY = BASE_DIR / "temp_bsp_copy"

def get_token():
    """Get token from .github_token file"""
    config_file = BASE_DIR / ".github_token"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return f.read().strip()
        except:
            pass
    return None

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 10 + "Push arduino-esp32-master Contents to ROOT")
    print("=" * 70)
    print()
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Token not found in .github_token file!")
        input("\nPress Enter to exit...")
        return 1
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Configure git
    print("[Config] Setting up git...")
    subprocess.run(["git", "config", "http.postBuffer", "524288000"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "config", "http.timeout", "600"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=BASE_DIR, check=True)
    print("  ✓ Git configured")
    
    # Step 1: Remove ALL files from GitHub FIRST
    print("\n[Step 1/4] Removing ALL files from GitHub...")
    result = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True)
    tracked_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    
    if tracked_files:
        print(f"  Found {len(tracked_files)} files to remove...")
        for file in tracked_files:
            subprocess.run(["git", "rm", "-r", "--cached", file], cwd=BASE_DIR, check=False, capture_output=True)
        
        subprocess.run(
            ["git", "commit", "-m", "Remove all files - clean repository"],
            cwd=BASE_DIR,
            check=False,
            capture_output=True
        )
        
        subprocess.run(
            ["git", "push", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=False,
            capture_output=True
        )
        print(f"  ✓ Removed {len(tracked_files)} files")
    else:
        print("  ℹ️  Repository already empty")
    
    # Step 2: Copy arduino-esp32-master contents to ROOT level
    print("\n[Step 2/4] Copying arduino-esp32-master contents to ROOT...")
    if not BSP_FOLDER.exists():
        print(f"  ❌ {BSP_FOLDER} not found!")
        input("\nPress Enter to exit...")
        return 1
    
    # Copy all contents from arduino-esp32-master to root (not the folder itself)
    print("  Copying files to root level (not the folder)...")
    file_count = 0
    
    for item in BSP_FOLDER.iterdir():
        if item.name.startswith('.'):
            continue
        
        dest = BASE_DIR / item.name
        
        # Remove existing if it exists (except arduino-esp32-master folder itself)
        if dest.exists() and dest != BSP_FOLDER:
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        
        # Copy to root
        if item.is_dir():
            shutil.copytree(item, dest)
            # Count files in this directory
            for root, dirs, files in os.walk(dest):
                file_count += len([f for f in files if not f.startswith('.')])
        else:
            shutil.copy2(item, dest)
            file_count += 1
    
    print(f"  ✓ Copied {file_count} files to root level")
    
    # Step 3: Add files to git (from root, NOT from arduino-esp32-master folder)
    print("\n[Step 3/4] Adding files to git (from ROOT, not from arduino-esp32-master folder)...")
    
    # Add all files/folders that are now in root (copied from arduino-esp32-master)
    # But exclude arduino-esp32-master folder itself, and script files
    exclude_items = {'arduino-esp32-master', '.git', '.github_token', 'temp_bsp_copy'}
    exclude_extensions = {'.bat', '.py', '.zip'}
    
    for item in BASE_DIR.iterdir():
        if item.name in exclude_items or item.name.startswith('.'):
            continue
        if item.suffix in exclude_extensions:
            continue
        
        if item.is_file():
            subprocess.run(["git", "add", "-f", item.name], cwd=BASE_DIR, check=False, capture_output=True)
        elif item.is_dir():
            subprocess.run(["git", "add", "-f", f"{item.name}/"], cwd=BASE_DIR, check=False, capture_output=True)
    
    print("  ✓ Files added to git (from root level)")
    
    # Commit
    subprocess.run(
        ["git", "commit", "-m", "Add BSP files to root (from arduino-esp32-master)"],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Committed")
    
    # Step 4: Push
    print("\n[Step 4/4] Pushing to GitHub...")
    print("  ⚠️  This will take time (large files)...")
    print("  Please wait, do NOT close this window...")
    print()
    
    try:
        result = subprocess.run(
            ["git", "push", "origin", BRANCH],
            cwd=BASE_DIR,
            check=True,
            timeout=1800,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📦 Files pushed to GitHub ROOT!")
        print(f"🔗 https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {BRANCH}")
        print(f"\n📁 Files are in ROOT (not in arduino-esp32-master folder)")
        print("=" * 70)
        
        input("\nPress Enter to close this window...")
        return 0
        
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout")
        input("\nPress Enter to close this window...")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed!")
        if e.stderr:
            print(f"  Error: {e.stderr[:500]}")
        input("\nPress Enter to close this window...")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close this window...")
        exit(1)

