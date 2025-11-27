#!/usr/bin/env python3
"""
Complete nuttyfi32 BSP Builder and Pusher
This script does EVERYTHING:
1. Clean old ZIP files
2. Create new ZIP from arduino-esp32-master
3. Update JSON with checksum, size, version
4. Remove all files from GitHub
5. Push arduino-esp32-master contents to GitHub ROOT
6. Keep screen open at end
"""

import os
import json
import zipfile
import shutil
import hashlib
import subprocess
from pathlib import Path

# ==================== CONFIGURATION ====================
VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
BSP_SOURCE = BASE_DIR / "arduino-esp32-master"
OUTPUT_ZIP = BASE_DIR / f"nuttyfi32-{VERSION}.zip"
JSON_FILE = BASE_DIR / "package_nuttyfi32_index.json"
GITHUB_BRANCH = "Master"
# =======================================================

def calculate_sha256(file_path):
    """Calculate SHA-256 checksum"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().upper()

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

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

def print_task_status(task_num, total, task_name, status, details=""):
    """Print task status"""
    status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⏳"
    print(f"\n[{task_num}/{total}] {task_name}")
    print(f"  {status_icon} {status}")
    if details:
        print(f"  └─ {details}")

def calculate_bsp_hash():
    """Calculate hash of BSP source folder to detect changes"""
    hasher = hashlib.sha256()
    
    # Get all files and their modification times
    file_info = []
    for root, dirs, files in os.walk(BSP_SOURCE):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.')]
        
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(BSP_SOURCE)
            mtime = file_path.stat().st_mtime
            size = file_path.stat().st_size
            file_info.append((str(rel_path), mtime, size))
    
    # Sort for consistent hashing
    file_info.sort()
    
    # Create hash from file info
    for path, mtime, size in file_info:
        hasher.update(f"{path}:{mtime}:{size}".encode())
    
    return hasher.hexdigest()

def check_if_zip_needs_update():
    """Check if ZIP file needs to be updated based on BSP changes"""
    if not OUTPUT_ZIP.exists():
        print("  ℹ️  ZIP file not found - will create new one")
        return True
    
    # Calculate current BSP hash
    current_hash = calculate_bsp_hash()
    
    # Check if we have a stored hash
    hash_file = BASE_DIR / ".zip_hash"
    if hash_file.exists():
        try:
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()
            
            if current_hash == stored_hash:
                print("  ✓ No changes in BSP source - ZIP is up to date")
                return False
            else:
                print("  ⚠️  Changes detected in BSP source - ZIP needs update")
                return True
        except:
            pass
    
    # If no stored hash, assume update needed
    print("  ℹ️  No previous hash found - will create/update ZIP")
    return True

def clean_old_zips():
    """Delete all old nuttyfi32-*.zip files"""
    old_zips = list(BASE_DIR.glob("nuttyfi32-*.zip"))
    deleted_count = 0
    for old_zip in old_zips:
        if old_zip != OUTPUT_ZIP:  # Don't delete the one we're about to create
            old_zip.unlink()
            deleted_count += 1
    return deleted_count

def create_zip_from_bsp():
    """Create ZIP file from arduino-esp32-master folder"""
    if not BSP_SOURCE.exists():
        raise FileNotFoundError(f"BSP source not found: {BSP_SOURCE}")
    
    print(f"  Creating ZIP from: {BSP_SOURCE}")
    print(f"  Output ZIP: {OUTPUT_ZIP}")
    
    # Remove existing ZIP if it exists
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()
        print("  ✓ Deleted old ZIP file")
    
    # Create ZIP with files at root level
    file_count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BSP_SOURCE):
            # Skip hidden files and folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                # Get relative path from BSP_SOURCE
                arcname = file_path.relative_to(BSP_SOURCE)
                zipf.write(file_path, arcname)
                file_count += 1
    
    # Save hash for future comparison
    current_hash = calculate_bsp_hash()
    hash_file = BASE_DIR / ".zip_hash"
    with open(hash_file, 'w') as f:
        f.write(current_hash)
    
    return file_count

def update_json_with_zip_info():
    """Update JSON file with ZIP checksum, size, and version"""
    if not OUTPUT_ZIP.exists():
        raise FileNotFoundError(f"ZIP file not found: {OUTPUT_ZIP}")
    
    # Calculate checksum and size
    checksum = calculate_sha256(OUTPUT_ZIP)
    size = str(get_file_size(OUTPUT_ZIP))
    
    # Read JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update platform info
    platform = data['packages'][0]['platforms'][0]
    platform['version'] = VERSION
    platform['url'] = f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{VERSION}/nuttyfi32-{VERSION}.zip"
    platform['archiveFileName'] = f"nuttyfi32-{VERSION}.zip"
    platform['checksum'] = f"SHA-256:{checksum}"
    platform['size'] = size
    
    # Write JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return checksum, size


def push_bsp_to_github_root():
    """Push arduino-esp32-master contents to GitHub ROOT (not the folder itself)"""
    token = get_token()
    if not token:
        raise ValueError("Token not found in .github_token file!")
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    if not BSP_SOURCE.exists():
        raise FileNotFoundError(f"BSP source not found: {BSP_SOURCE}")
    
    # Configure git
    subprocess.run(["git", "config", "http.postBuffer", "524288000"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "config", "http.timeout", "600"], cwd=BASE_DIR, check=False)
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=BASE_DIR, check=True)
    
    # Copy all contents from arduino-esp32-master to root (not the folder itself)
    print("  Syncing files from arduino-esp32-master to root...")
    file_count = 0
    
    for item in BSP_SOURCE.iterdir():
        if item.name.startswith('.'):
            continue
        
        dest = BASE_DIR / item.name
        
        # Skip if it's a script file or ZIP
        if item.name.endswith(('.bat', '.py', '.zip', '.json')) and item != JSON_FILE:
            continue
        
        # Remove existing if it exists (except arduino-esp32-master folder itself)
        if dest.exists() and dest != BSP_SOURCE:
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        
        # Copy to root
        if item.is_dir():
            shutil.copytree(item, dest)
            # Count files
            for root, dirs, files in os.walk(dest):
                file_count += len([f for f in files if not f.startswith('.')])
        else:
            shutil.copy2(item, dest)
            file_count += 1
    
    print(f"  Synced {file_count} files to root level")
    
    # Add files to git (from root, NOT from arduino-esp32-master folder)
    print("  Adding changes to git...")
    
    exclude_items = {'arduino-esp32-master', '.git', '.github_token', 'temp_bsp_copy'}
    exclude_extensions = {'.bat', '.py', '.zip'}  # Exclude scripts and ZIP (ZIP is too large)
    
    # Add JSON file explicitly (it should be pushed)
    if JSON_FILE.exists():
        subprocess.run(["git", "add", "-f", JSON_FILE.name], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Add all BSP files from root
    for item in BASE_DIR.iterdir():
        if item.name in exclude_items or item.name.startswith('.'):
            continue
        if item.suffix in exclude_extensions:
            continue
        # Skip JSON as it's already added above
        if item.name == JSON_FILE.name:
            continue
        
        if item.is_file():
            subprocess.run(["git", "add", "-f", item.name], cwd=BASE_DIR, check=False, capture_output=True)
        elif item.is_dir():
            subprocess.run(["git", "add", "-f", f"{item.name}/"], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Check if there are any changes to commit
    result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  ℹ️  No changes to commit - everything is up to date")
        return file_count
    
    # Commit
    subprocess.run(
        ["git", "commit", "-m", f"Update nuttyfi32 BSP v{VERSION} - sync changes"],
        cwd=BASE_DIR,
        check=True
    )
    
    # Push
    print("  ⚠️  Pushing to GitHub (this will take time)...")
    print("  Please wait, do NOT close this window...")
    
    result = subprocess.run(
        ["git", "push", "origin", GITHUB_BRANCH],
        cwd=BASE_DIR,
        check=True,
        timeout=1800,
        capture_output=True,
        text=True
    )
    
    return file_count

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 15 + "nuttyfi32 BSP Builder & Pusher")
    print("=" * 70)
    print(f"\nVersion: {VERSION}")
    print(f"BSP Source: {BSP_SOURCE}")
    print(f"Output ZIP: {OUTPUT_ZIP}")
    print("\n⚠️  Note: Only changes will be pushed (no cleaning)")
    print("=" * 70)
    
    tasks_completed = 0
    tasks_failed = 0
    # Total tasks will be dynamic: 5 if ZIP update needed, 2 if not
    
    try:
        # Task 1: Check if ZIP needs update
        print_task_status(1, total_tasks, "Check if ZIP needs update", "RUNNING")
        zip_needs_update = check_if_zip_needs_update()
        
        if zip_needs_update:
            print_task_status(1, total_tasks, "Check if ZIP needs update", "SUCCESS", "Changes detected - ZIP will be updated")
            
            # Task 2: Clean old ZIP files
            print_task_status(2, total_tasks, "Clean old ZIP files", "RUNNING")
            deleted = clean_old_zips()
            print_task_status(2, total_tasks, "Clean old ZIP files", "SUCCESS", f"Deleted {deleted} old ZIP(s)")
            tasks_completed += 1
            
            # Task 3: Create ZIP from arduino-esp32-master
            print_task_status(3, total_tasks, "Create ZIP from arduino-esp32-master", "RUNNING")
            file_count = create_zip_from_bsp()
            zip_size = get_file_size(OUTPUT_ZIP) / (1024 * 1024)  # MB
            print_task_status(3, total_tasks, "Create ZIP from arduino-esp32-master", "SUCCESS", 
                             f"Created {OUTPUT_ZIP.name} ({file_count} files, {zip_size:.2f} MB)")
            tasks_completed += 1
            
            # Task 4: Update JSON with checksum and size
            print_task_status(4, total_tasks, "Update JSON with checksum and size", "RUNNING")
            checksum, size = update_json_with_zip_info()
            print_task_status(4, total_tasks, "Update JSON with checksum and size", "SUCCESS",
                             f"Checksum: SHA-256:{checksum[:16]}..., Size: {int(size) / (1024*1024):.2f} MB")
            tasks_completed += 1
            
            # Task 5: Push changes to GitHub
            print_task_status(5, total_tasks, "Push changes to GitHub", "RUNNING")
            pushed_count = push_bsp_to_github_root()
            print_task_status(5, total_tasks, "Push changes to GitHub", "SUCCESS",
                             f"Pushed changes ({pushed_count} files synced)")
            tasks_completed += 1
        else:
            print_task_status(1, total_tasks, "Check if ZIP needs update", "SUCCESS", "No changes - ZIP is up to date")
            tasks_completed += 1
            
            # Task 2: Push changes to GitHub (ZIP already exists, no need to recreate)
            print_task_status(2, total_tasks, "Push changes to GitHub", "RUNNING")
            pushed_count = push_bsp_to_github_root()
            print_task_status(2, total_tasks, "Push changes to GitHub", "SUCCESS",
                             f"Pushed changes ({pushed_count} files synced)")
            tasks_completed += 1
        
    except Exception as e:
        tasks_failed += 1
        print_task_status(total_tasks, total_tasks, "Error", "FAILED", str(e))
        import traceback
        traceback.print_exc()
    
    # Final Summary
    print("\n" + "=" * 70)
    print(f"✅ Completed: {tasks_completed} tasks | ❌ Failed: {tasks_failed} tasks")
    print("=" * 70)
    
    if tasks_failed == 0:
        print("\n" + " " * 20 + "✅ ALL TASKS COMPLETED!")
        print("=" * 70)
        print(f"\n📦 ZIP File: {OUTPUT_ZIP.name}")
        print(f"📄 JSON File: {JSON_FILE.name}")
        print(f"🔗 GitHub: https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {GITHUB_BRANCH}")
        print(f"\n📁 Files are in GitHub ROOT (not in arduino-esp32-master folder)")
        print("=" * 70)
    else:
        print("\n⚠️  WARNING! Some Tasks Failed")
        print("=" * 70)
        print("Please check the errors above and try again.")
        print("=" * 70)
    
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        input("\nPress Enter to close this window...")
        exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close this window...")
        exit(1)

