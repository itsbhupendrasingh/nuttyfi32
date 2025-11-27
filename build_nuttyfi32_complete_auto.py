#!/usr/bin/env python3
"""
Complete nuttyfi32 BSP Builder - FULLY AUTOMATED
This script does EVERYTHING automatically:
1. Create ZIP from arduino-esp32-master
2. Calculate SHA-256 checksum
3. Update JSON file in package/ folder with checksum, size, version
4. Push to GitHub (BSP files + JSON)
5. Everything ready for testing!
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
JSON_TEMPLATE = BASE_DIR / "package" / "package_nuttyfi32_index.template.json"
JSON_OUTPUT = BASE_DIR / "package_nuttyfi32_index.json"
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
    
    return file_count

def update_json_with_zip_info():
    """Update JSON file with ZIP checksum, size, and version"""
    if not OUTPUT_ZIP.exists():
        raise FileNotFoundError(f"ZIP file not found: {OUTPUT_ZIP}")
    
    if not JSON_TEMPLATE.exists():
        raise FileNotFoundError(f"JSON template not found: {JSON_TEMPLATE}")
    
    # Calculate checksum and size
    checksum = calculate_sha256(OUTPUT_ZIP)
    size = str(get_file_size(OUTPUT_ZIP))
    
    print(f"  Checksum: SHA-256:{checksum}")
    print(f"  Size: {size} bytes ({int(size) / (1024*1024):.2f} MB)")
    
    # Read JSON template
    with open(JSON_TEMPLATE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update platform info
    platform = data['packages'][0]['platforms'][0]
    platform['version'] = VERSION
    platform['url'] = f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{VERSION}/nuttyfi32-{VERSION}.zip"
    platform['archiveFileName'] = f"nuttyfi32-{VERSION}.zip"
    platform['checksum'] = f"SHA-256:{checksum}"
    platform['size'] = size
    
    # Write updated JSON to root
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"  ✓ JSON updated: {JSON_OUTPUT}")
    
    return checksum, size

def push_to_github():
    """Push BSP files and JSON to GitHub"""
    token = get_token()
    if not token:
        raise ValueError("Token not found in .github_token file!")
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
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
        if item.name.endswith(('.bat', '.py', '.zip')):
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
    
    # Add files to git
    print("  Adding changes to git...")
    
    exclude_items = {'arduino-esp32-master', '.git', '.github_token', 'temp_bsp_copy'}
    exclude_extensions = {'.bat', '.py', '.zip'}  # Exclude scripts and ZIP
    
    # Add JSON file explicitly
    if JSON_OUTPUT.exists():
        subprocess.run(["git", "add", "-f", JSON_OUTPUT.name], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Add all BSP files from root
    for item in BASE_DIR.iterdir():
        if item.name in exclude_items or item.name.startswith('.'):
            continue
        if item.suffix in exclude_extensions:
            continue
        # Skip JSON as it's already added above
        if item.name == JSON_OUTPUT.name:
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
        ["git", "commit", "-m", f"Update nuttyfi32 BSP v{VERSION} - auto build"],
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
    print(" " * 15 + "nuttyfi32 BSP - FULLY AUTOMATED BUILDER")
    print("=" * 70)
    print(f"\nVersion: {VERSION}")
    print(f"BSP Source: {BSP_SOURCE}")
    print(f"Output ZIP: {OUTPUT_ZIP}")
    print(f"JSON Template: {JSON_TEMPLATE}")
    print(f"JSON Output: {JSON_OUTPUT}")
    print("=" * 70)
    
    tasks_completed = 0
    tasks_failed = 0
    total_tasks = 4
    
    try:
        # Task 1: Create ZIP from arduino-esp32-master
        print_task_status(1, total_tasks, "Create ZIP from arduino-esp32-master", "RUNNING")
        file_count = create_zip_from_bsp()
        zip_size = get_file_size(OUTPUT_ZIP) / (1024 * 1024)  # MB
        print_task_status(1, total_tasks, "Create ZIP from arduino-esp32-master", "SUCCESS", 
                         f"Created {OUTPUT_ZIP.name} ({file_count} files, {zip_size:.2f} MB)")
        tasks_completed += 1
        
        # Task 2: Update JSON with checksum and size
        print_task_status(2, total_tasks, "Update JSON with checksum and size", "RUNNING")
        checksum, size = update_json_with_zip_info()
        print_task_status(2, total_tasks, "Update JSON with checksum and size", "SUCCESS",
                         f"Checksum: SHA-256:{checksum[:16]}..., Size: {int(size) / (1024*1024):.2f} MB")
        tasks_completed += 1
        
        # Task 3: Push changes to GitHub
        print_task_status(3, total_tasks, "Push changes to GitHub", "RUNNING")
        pushed_count = push_to_github()
        print_task_status(3, total_tasks, "Push changes to GitHub", "SUCCESS",
                         f"Pushed changes ({pushed_count} files synced)")
        tasks_completed += 1
        
        # Task 4: Summary
        print_task_status(4, total_tasks, "Build Complete", "SUCCESS", "All tasks completed!")
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
        print(f"📄 JSON File: {JSON_OUTPUT.name}")
        print(f"🔗 GitHub: https://github.com/itsbhupendrasingh/nuttyfi32")
        print(f"🌿 Branch: {GITHUB_BRANCH}")
        print(f"\n✨ Ready for testing!")
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


