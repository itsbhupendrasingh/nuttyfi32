#!/usr/bin/env python3
"""
Simple Script - Clean GitHub and Push arduino-esp32-master
1. Remove ALL files from GitHub FIRST
2. Then push ONLY arduino-esp32-master folder
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRANCH = "Master"
BSP_FOLDER = BASE_DIR / "arduino-esp32-master"

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
    """Main function - does everything automatically"""
    print("=" * 70)
    print(" " * 15 + "Clean and Push - Automatic")
    print("=" * 70)
    print()
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Token not found in .github_token file!")
        print("   Create .github_token file with your GitHub token")
        input("\nPress Enter to exit...")
        return 1
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    # Configure git for large files
    print("[Config] Setting up git for large files...")
    subprocess.run(["git", "config", "http.postBuffer", "524288000"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "config", "http.timeout", "600"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=BASE_DIR, check=True)
    print("  ✓ Git configured")
    
    # Step 1: Remove ALL files from GitHub FIRST
    print("\n[Step 1/4] Removing ALL files from GitHub...")
    print("  This will delete everything in the repository...")
    
    # Get all tracked files
    result = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True)
    tracked_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    
    if tracked_files:
        print(f"  Found {len(tracked_files)} files to remove...")
        # Remove all files
        for file in tracked_files:
            subprocess.run(["git", "rm", "-r", "--cached", file], cwd=BASE_DIR, check=False, capture_output=True)
        
        # Commit deletion
        subprocess.run(
            ["git", "commit", "-m", "Remove all files - clean repository"],
            cwd=BASE_DIR,
            check=False,
            capture_output=True
        )
        
        # Push deletion
        print("  Pushing deletion to GitHub...")
        subprocess.run(
            ["git", "push", "origin", BRANCH, "--force"],
            cwd=BASE_DIR,
            check=False,
            capture_output=True
        )
        print(f"  ✓ Removed {len(tracked_files)} files from GitHub")
    else:
        print("  ℹ️  No files to remove (repository already empty)")
    
    # Step 2: Add ONLY arduino-esp32-master
    print("\n[Step 2/4] Adding arduino-esp32-master folder...")
    if not BSP_FOLDER.exists():
        print(f"  ❌ {BSP_FOLDER} not found!")
        input("\nPress Enter to exit...")
        return 1
    
    subprocess.run(["git", "add", "-f", "arduino-esp32-master/"], cwd=BASE_DIR, check=True)
    
    # Count files
    import os
    file_count = 0
    for root, dirs, files in os.walk(BSP_FOLDER):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        file_count += len([f for f in files if not f.startswith('.')])
    
    print(f"  ✓ Added {file_count} files from arduino-esp32-master/")
    
    # Step 3: Commit
    print("\n[Step 3/4] Committing...")
    subprocess.run(
        ["git", "commit", "-m", "Add arduino-esp32-master folder with all files"],
        cwd=BASE_DIR,
        check=True
    )
    print("  ✓ Committed")
    
    # Step 4: Push
    print("\n[Step 4/4] Pushing to GitHub...")
    print("  ⚠️  This will take time (large files - 24MB)...")
    print("  Please wait, do NOT close this window...")
    print()
    
    try:
        result = subprocess.run(
            ["git", "push", "origin", BRANCH],
            cwd=BASE_DIR,
            check=True,
            timeout=1800,  # 30 minutes
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        print("\n" + "=" * 70)
        print(" " * 20 + "✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📦 All files pushed to GitHub!")
        print(f"🔗 https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {BRANCH}")
        print(f"📁 Folder: arduino-esp32-master/ ({file_count} files)")
        print("\n✅ Task completed successfully!")
        print("=" * 70)
        
        # PAUSE - Screen will NOT close
        print("\n")
        input("Press Enter to close this window...")
        return 0
        
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Push timeout (30 minutes)")
        print("  Try manually: git push origin Master")
        print("\n")
        input("Press Enter to close this window...")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Push failed!")
        if e.stdout:
            print(f"  Output: {e.stdout[:500]}")
        if e.stderr:
            print(f"  Error: {e.stderr[:500]}")
        
        error_text = (e.stderr or e.stdout or "").lower()
        if "408" in error_text or "timeout" in error_text:
            print("\n  💡 Solution: Run push_manual.bat")
        
        print("\n")
        input("Press Enter to close this window...")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        input("\nPress Enter to close this window...")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n")
        input("Press Enter to close this window...")
        exit(1)
