#!/usr/bin/env python3
"""
Complete nuttyfi32 BSP Builder - FULLY AUTOMATED
Sab kuch automatically handle karta hai:
1. ZIP file check - agar changes hain to naya ZIP banata hai
2. SHA-256 calculate karta hai
3. JSON me automatically add karta hai (SHA, size, version)
4. Purani ZIP delete karta hai agar nayi ban rahi ho
5. GitHub push karta hai
6. Sab steps automatically, koi miss nahi
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
RELEASE_ZIP = BASE_DIR / "esp32-1.0.6.zip"  # Source release ZIP
OUTPUT_ZIP = BASE_DIR / f"nuttyfi32-{VERSION}.zip"  # Output ZIP
BSP_SOURCE = BASE_DIR / "arduino-esp32-master"  # Repo folder for GitHub
JSON_TEMPLATE = BASE_DIR / "package" / "package_nuttyfi32_index.template.json"
JSON_OUTPUT = BASE_DIR / "package_nuttyfi32_index.json"
TEMP_DIR = BASE_DIR / "temp_build"
GITHUB_BRANCH = "Master"
# =======================================================

def run_git(cmd, allow_failure=False, capture_output=False, timeout=None):
    """Run a git command with consistent defaults."""
    result = subprocess.run(
        ["git"] + cmd,
        cwd=BASE_DIR,
        text=True,
        capture_output=capture_output,
        timeout=timeout,
        check=False
    )
    if result.returncode != 0 and not allow_failure:
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        raise RuntimeError(
            f"git {' '.join(cmd)} failed (code {result.returncode})\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )
    return result

def ensure_git_ready():
    """Abort any half-done rebase/merge so automation starts clean."""
    git_dir = BASE_DIR / ".git"
    rebase_markers = [git_dir / "rebase-apply", git_dir / "rebase-merge"]
    if any(marker.exists() for marker in rebase_markers):
        print("  ⚠️  Incomplete rebase detected. Aborting before continuing...")
        run_git(["rebase", "--abort"], allow_failure=True)

def sync_with_remote():
    """Fetch + rebase onto origin to avoid push rejection."""
    print("  🔄 Syncing with origin...")
    run_git(["fetch", "origin", GITHUB_BRANCH])
    result = run_git(["pull", "--rebase", "origin", GITHUB_BRANCH], allow_failure=True, capture_output=True)
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        raise RuntimeError(
            "git pull --rebase failed. Resolve conflicts manually and rerun.\n"
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )
    print("  ✓ Repository is up to date with origin")

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

def calculate_zip_hash(zip_path):
    """Calculate hash of ZIP file contents to detect changes"""
    if not zip_path.exists():
        return None
    
    hasher = hashlib.sha256()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Get all file info (name, size, CRC)
            file_info = []
            for info in zf.infolist():
                if not info.filename.startswith('.'):
                    file_info.append((info.filename, info.file_size, info.CRC))
            
            # Sort for consistent hashing
            file_info.sort()
            
            # Create hash from file info
            for filename, size, crc in file_info:
                hasher.update(f"{filename}:{size}:{crc}".encode())
    except:
        return None
    
    return hasher.hexdigest()

def check_if_zip_needs_update():
    """Check if ZIP needs to be updated based on source changes"""
    # Check if output ZIP exists
    if not OUTPUT_ZIP.exists():
        print("  ℹ️  Output ZIP not found - will create new one")
        return True

    # If release ZIP exists, compare hashes
    if RELEASE_ZIP.exists():
        source_hash = calculate_zip_hash(RELEASE_ZIP)
    elif BSP_SOURCE.exists():
        print("  ℹ️  Release ZIP missing - rebuilding from local folder")
        return True
    else:
        raise FileNotFoundError(
            f"Neither {RELEASE_ZIP.name} nor {BSP_SOURCE.name} found. Cannot continue."
        )

    stored_hash_file = BASE_DIR / ".zip_hash"
    
    if stored_hash_file.exists():
        try:
            with open(stored_hash_file, 'r') as f:
                stored_hash = f.read().strip()
            
            if source_hash == stored_hash:
                print("  ✓ No changes in source ZIP - existing ZIP is up to date")
                return False
            else:
                print("  ⚠️  Changes detected in source ZIP - will create new ZIP")
                return True
        except:
            pass
    
    # If no stored hash, assume update needed
    print("  ℹ️  No previous hash found - will create/update ZIP")
    return True

def delete_old_zips():
    """Delete old nuttyfi32 ZIP files (keep only current version)"""
    old_zips = list(BASE_DIR.glob("nuttyfi32-*.zip"))
    deleted_count = 0
    for old_zip in old_zips:
        if old_zip != OUTPUT_ZIP:
            old_zip.unlink()
            deleted_count += 1
            print(f"    ✓ Deleted: {old_zip.name}")
    return deleted_count

def extract_zip(zip_path, extract_to):
    """Extract ZIP file and return work directory"""
    print(f"  Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("  ✓ Extraction complete!")
    
    # Find extracted folder(s)
    extracted_items = list(extract_to.iterdir())
    extracted_folders = [d for d in extracted_items if d.is_dir()]
    extracted_files = [f for f in extracted_items if f.is_file()]
    
    # If multiple top-level items, wrap in a single folder
    if len(extracted_folders) > 1 or (extracted_folders and extracted_files):
        # Multiple top-level items - wrap in single folder
        wrapper_dir = extract_to / "nuttyfi32_bsp"
        wrapper_dir.mkdir()
        
        # Move all items into wrapper
        for item in extracted_items:
            dest = wrapper_dir / item.name
            if item.is_dir():
                shutil.move(str(item), str(dest))
            else:
                shutil.move(str(item), str(dest))
        
        print(f"  ✓ Wrapped in single root folder: {wrapper_dir.name}/")
        return wrapper_dir
    elif extracted_folders:
        # Single folder - use it directly
        return extracted_folders[0]
    elif extracted_files:
        # Only files - wrap in folder
        wrapper_dir = extract_to / "nuttyfi32_bsp"
        wrapper_dir.mkdir()
        for item in extracted_files:
            shutil.move(str(item), str(wrapper_dir / item.name))
        print(f"  ✓ Wrapped files in root folder: {wrapper_dir.name}/")
        return wrapper_dir
    else:
        raise FileNotFoundError("No content found in extracted ZIP!")

def prepare_bsp_source():
    """Return a working directory populated with ESP32 BSP sources."""
    if RELEASE_ZIP.exists():
        print("  ℹ️  Using ESP32 release ZIP as source")
        return extract_zip(RELEASE_ZIP, TEMP_DIR)
    if BSP_SOURCE.exists():
        print("  ℹ️  Release ZIP missing, using local arduino-esp32-master folder")
        dest = TEMP_DIR / "nuttyfi32_source"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(BSP_SOURCE, dest)
        return dest
    raise FileNotFoundError(
        f"Neither {RELEASE_ZIP.name} nor {BSP_SOURCE.name} folder found. Provide at least one source."
    )

def ensure_bsp_source_folder():
    """Make sure BSP_SOURCE exists by extracting the release ZIP if needed."""
    if BSP_SOURCE.exists():
        return
    if not RELEASE_ZIP.exists():
        raise FileNotFoundError(f"BSP source not found: {BSP_SOURCE} and release ZIP missing")
    print("  ℹ️  BSP source folder missing, extracting from release ZIP...")
    if BSP_SOURCE.exists():
        shutil.rmtree(BSP_SOURCE)
    with zipfile.ZipFile(RELEASE_ZIP, 'r') as zip_ref:
        zip_ref.extractall(BASE_DIR)
    # If the zip contains esp32-1.0.6/ etc., rename to expected folder
    extracted_folder = BASE_DIR / "esp32-1.0.6"
    if extracted_folder.exists() and not BSP_SOURCE.exists():
        extracted_folder.rename(BSP_SOURCE)

def rename_esp32_to_nuttyfi32(directory):
    """Rename esp32 references to nuttyfi32 in files and content"""
    print("  Renaming esp32 to nuttyfi32...")
    
    # 1. Rename package JSON file
    package_dir = directory / "package"
    if package_dir.exists():
        old_json = package_dir / "package_esp32_index.template.json"
        new_json = package_dir / "package_nuttyfi32_index.template.json"
        if old_json.exists():
            shutil.move(str(old_json), str(new_json))
            print(f"    ✓ Renamed: package_esp32_index.template.json -> package_nuttyfi32_index.template.json")
    
    # 2. Update content in key files
    files_to_update = [
        "package.json",
        "platform.txt",
        "boards.txt",
    ]
    
    for file_name in files_to_update:
        file_path = directory / file_name
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update platform.txt
        if file_name == "platform.txt":
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('name=') and 'ESP32' in line:
                    lines[i] = 'name=nuttyfi32 Arduino'
                    break
            python_keys = [
                "tools.esptool_py.network_cmd",
                "tools.gen_esp32part.cmd",
                "recipe.objcopy.bin.pattern.linux",
                "tools.esptool_py.upload.pattern.linux",
            ]
            def replace_python_with_python3(line, key):
                prefix = f"{key}=python"
                if line.startswith(prefix):
                    return f"{key}=python3{line[len(prefix):]}"
                return line
            for i, line in enumerate(lines):
                for key in python_keys:
                    new_line = replace_python_with_python3(line, key)
                    if new_line != line:
                        line = new_line
                lines[i] = line
            content = '\n'.join(lines)
        
        # Update boards.txt - add nuttyfi32 board
        if file_name == "boards.txt":
            lines = content.split('\n')
            
            # Find esp32.name line
            esp32_start = None
            esp32_end = None
            for i, line in enumerate(lines):
                if line.strip() == "esp32.name=ESP32 Dev Module" and esp32_start is None:
                    esp32_start = i
                elif esp32_start is not None and esp32_end is None:
                    if line.strip() and not line.strip().startswith('esp32.') and not line.strip().startswith('#') and not line.strip() == '':
                        if not line.strip().startswith('esp32.menu.'):
                            esp32_end = i
                            break
            
            if esp32_start is not None:
                if esp32_end is None:
                    esp32_end = len(lines)
                    for i in range(esp32_start + 1, len(lines)):
                        line = lines[i].strip()
                        if '.name=' in line and not line.startswith('esp32.') and not line.startswith('#'):
                            esp32_end = i
                            break
                
                # Extract esp32 section
                esp32_section = lines[esp32_start:esp32_end]
                
                # Create nuttyfi32 section
                nuttyfi32_section = []
                nuttyfi32_section.append("")
                nuttyfi32_section.append("##############################################################")
                nuttyfi32_section.append("# nuttyfi32 Dev Module")
                nuttyfi32_section.append("##############################################################")
                nuttyfi32_section.append("")
                
                for line in esp32_section:
                    if line.strip().startswith('esp32.'):
                        nuttyfi32_line = line.replace('esp32.', 'nuttyfi32.', 1)
                        nuttyfi32_section.append(nuttyfi32_line)
                    elif line.strip() == '' or line.strip().startswith('#'):
                        nuttyfi32_section.append(line)
                
                # Insert nuttyfi32 section after esp32 section
                lines[esp32_end:esp32_end] = nuttyfi32_section
                print(f"    ✓ Added nuttyfi32 board entry to boards.txt")
            
            content = '\n'.join(lines)
        
        # Write updated content
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    ✓ Updated: {file_name}")

def create_zip(source_dir, output_zip):
    """Create ZIP file from directory - ensures single root folder for Arduino IDE"""
    print(f"  Creating ZIP: {output_zip.name}...")
    
    # Remove existing ZIP if it exists
    if output_zip.exists():
        output_zip.unlink()
        print("    ✓ Deleted old ZIP file")
    
    # Arduino IDE requires single root folder in ZIP
    root_folder_name = source_dir.name
    
    file_count = 0
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip hidden files
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                # Ensure all files are under single root folder
                relative_path = file_path.relative_to(source_dir)
                arcname = f"{root_folder_name}/{relative_path}"
                zipf.write(file_path, arcname)
                file_count += 1
    
    # Save hash for future comparison
    source_hash = None
    if RELEASE_ZIP.exists():
        source_hash = calculate_zip_hash(RELEASE_ZIP)
    if source_hash:
        hash_file = BASE_DIR / ".zip_hash"
        with open(hash_file, 'w') as f:
            f.write(source_hash)
    
    print(f"  ✓ ZIP created: {output_zip.name} ({file_count} files)")
    print(f"    Root folder in ZIP: {root_folder_name}/")
    return output_zip

def update_json_with_zip_info():
    """Update JSON file with ZIP checksum, size, and version"""
    if not OUTPUT_ZIP.exists():
        raise FileNotFoundError(f"ZIP file not found: {OUTPUT_ZIP}")
    
    # Calculate checksum and size
    checksum = calculate_sha256(OUTPUT_ZIP)
    size = str(get_file_size(OUTPUT_ZIP))
    
    print(f"  Checksum: SHA-256:{checksum}")
    print(f"  Size: {size} bytes ({int(size) / (1024*1024):.2f} MB)")
    
    # Read existing JSON or template
    if JSON_OUTPUT.exists():
        # Read existing JSON to preserve tools
        with open(JSON_OUTPUT, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif JSON_TEMPLATE.exists():
        with open(JSON_TEMPLATE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Create from scratch if neither exists (should not happen)
        raise FileNotFoundError(f"Neither {JSON_OUTPUT} nor {JSON_TEMPLATE} found!")
    
    # Update platform info
    platform = data['packages'][0]['platforms'][0]
    platform['version'] = VERSION
    platform['url'] = f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{VERSION}/nuttyfi32-{VERSION}.zip"
    platform['archiveFileName'] = f"nuttyfi32-{VERSION}.zip"
    platform['checksum'] = f"SHA-256:{checksum}"
    platform['size'] = size
    
    # Write JSON
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"  ✓ JSON updated: {JSON_OUTPUT.name}")
    return checksum, size

def push_bsp_to_github():
    """Push arduino-esp32-master to GitHub Master branch"""
    token = get_token()
    if not token:
        raise ValueError("Token not found in .github_token file!")
    
    repo_url = f"https://{token}@github.com/itsbhupendrasingh/nuttyfi32.git"
    
    if not BSP_SOURCE.exists():
        ensure_bsp_source_folder()
    
    # Configure git
    run_git(["config", "http.postBuffer", "524288000"], allow_failure=True)
    run_git(["config", "http.timeout", "600"], allow_failure=True)
    run_git(["remote", "set-url", "origin", repo_url])
    
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
            for root, dirs, files in os.walk(dest):
                file_count += len([f for f in files if not f.startswith('.')])
        else:
            shutil.copy2(item, dest)
            file_count += 1
    
    print(f"  Synced {file_count} files to root level")
    
    # Add files to git
    print("  Adding changes to git...")
    
    exclude_items = {'arduino-esp32-master', '.git', '.github_token', 'temp_build'}
    exclude_extensions = {'.bat', '.zip'}
    
    # Add JSON file explicitly
    if JSON_OUTPUT.exists():
        run_git(["add", "-f", JSON_OUTPUT.name], allow_failure=True, capture_output=True)
        print(f"    ✓ Added: {JSON_OUTPUT.name}")
    
    # Add all BSP files from root (only if they exist and are not excluded)
    added_count = 0
    for item in BASE_DIR.iterdir():
        if item.name in exclude_items or item.name.startswith('.'):
            continue
        if item.suffix in exclude_extensions:
            continue
        if item.name == JSON_OUTPUT.name:
            continue
        
        # Only add if file/dir exists and is not already in git or has changes
        if item.is_file():
            result = run_git(["add", "-f", item.name], allow_failure=True, capture_output=True)
            if result.returncode == 0:
                added_count += 1
        elif item.is_dir():
            result = run_git(["add", "-f", f"{item.name}/"], allow_failure=True, capture_output=True)
            if result.returncode == 0:
                added_count += 1
    
    if added_count > 0:
        print(f"    ✓ Added {added_count} items to git")
    
    # Always add critical automation scripts so they are tracked
    auto_scripts = [
        "build_nuttyfi32_complete_auto_final.py",
        "build_nuttyfi32_package.py",
        "build_nuttyfi32_complete_auto.py",
        "build_nuttyfi32_from_release_zip.py",
        "build_and_push_complete.py",
        "build_and_push.bat",
    ]
    for script in auto_scripts:
        script_path = BASE_DIR / script
        if script_path.exists():
            run_git(["add", script], allow_failure=True)
            print(f"    ✓ Forced add: {script}")
    
    # Check if there are any staged changes to commit
    result = run_git(["diff", "--cached", "--name-only"], capture_output=True)
    staged_files = result.stdout.strip().split('\n')
    staged_files = [f for f in staged_files if f.strip()]
    
    if not staged_files:
        print("  ℹ️  No changes to commit - everything is up to date")
        return file_count
    
    print(f"  ✓ {len(staged_files)} files staged for commit")
    
    # Commit
    run_git(["commit", "-m", f"Update nuttyfi32 BSP v{VERSION} - auto build"])
    
    # Push
    print("  ⚠️  Pushing to GitHub (this will take time)...")
    print("  Please wait, do NOT close this window...")
    
    result = run_git(["push", "origin", GITHUB_BRANCH], capture_output=True, timeout=1800)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    
    return file_count

def main():
    """Main function - sab kuch automatically"""
    print("=" * 70)
    print(" " * 15 + "nuttyfi32 BSP - COMPLETE AUTOMATED BUILDER")
    print("=" * 70)
    print(f"\nVersion: {VERSION}")
    print(f"Release ZIP: {RELEASE_ZIP}")
    print(f"Output ZIP: {OUTPUT_ZIP}")
    print(f"BSP Source: {BSP_SOURCE}")
    print("=" * 70)
    
    tasks_completed = 0
    tasks_failed = 0
    total_tasks = 7
    task_idx = 1
    
    # Clean temp directory
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir()
    
    try:
        # Task 1: Sync with GitHub
        print_task_status(task_idx, total_tasks, "Sync with GitHub", "RUNNING")
        ensure_git_ready()
        sync_with_remote()
        print_task_status(task_idx, total_tasks, "Sync with GitHub", "SUCCESS", "Local branch in sync with origin")
        tasks_completed += 1
        task_idx += 1

        # Task 1: Check if ZIP needs update
        print_task_status(task_idx, total_tasks, "Check if ZIP needs update", "RUNNING")
        zip_needs_update = check_if_zip_needs_update()
        if zip_needs_update:
            detail = "Changes detected - ZIP will be updated"
        else:
            detail = "No changes - ZIP is up to date"
        print_task_status(task_idx, total_tasks, "Check if ZIP needs update", "SUCCESS", detail)
        tasks_completed += 1
        task_idx += 1
        
        if zip_needs_update:
            # Task 3: Delete old ZIP files
            print_task_status(task_idx, total_tasks, "Delete old ZIP files", "RUNNING")
            deleted = delete_old_zips()
            print_task_status(task_idx, total_tasks, "Delete old ZIP files", "SUCCESS", f"Deleted {deleted} old ZIP(s)")
            tasks_completed += 1
            task_idx += 1
            
            # Task 4: Prepare source and rename
            print_task_status(task_idx, total_tasks, "Prepare BSP source", "RUNNING")
            work_dir = prepare_bsp_source()
            rename_esp32_to_nuttyfi32(work_dir)
            print_task_status(task_idx, total_tasks, "Prepare BSP source", "SUCCESS", "Source ready")
            tasks_completed += 1
            task_idx += 1
            
            # Task 5: Create nuttyfi32 ZIP
            print_task_status(task_idx, total_tasks, "Create nuttyfi32 ZIP", "RUNNING")
            create_zip(work_dir, OUTPUT_ZIP)
            zip_size = get_file_size(OUTPUT_ZIP) / (1024 * 1024)  # MB
            print_task_status(task_idx, total_tasks, "Create nuttyfi32 ZIP", "SUCCESS", 
                             f"Created {OUTPUT_ZIP.name} ({zip_size:.2f} MB)")
            tasks_completed += 1
            task_idx += 1
            
            # Task 6: Update JSON with checksum and size
            print_task_status(task_idx, total_tasks, "Update JSON with checksum and size", "RUNNING")
            checksum, size = update_json_with_zip_info()
            print_task_status(task_idx, total_tasks, "Update JSON with checksum and size", "SUCCESS",
                             f"Checksum: SHA-256:{checksum[:16]}..., Size: {int(size) / (1024*1024):.2f} MB")
            tasks_completed += 1
            task_idx += 1
        
        # Task 7: Push to GitHub (always run)
        print_task_status(total_tasks, total_tasks, "Push to GitHub", "RUNNING")
        pushed_count = push_bsp_to_github()
        print_task_status(total_tasks, total_tasks, "Push to GitHub", "SUCCESS",
                         f"Pushed changes ({pushed_count} files synced)")
        tasks_completed += 1
        
    except Exception as e:
        tasks_failed += 1
        print_task_status(total_tasks, total_tasks, "Error", "FAILED", str(e))
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup temp directory
        if TEMP_DIR.exists():
            print(f"\nCleaning up temp directory...")
            shutil.rmtree(TEMP_DIR)
    
    # Final Summary
    print("\n" + "=" * 70)
    print(f"✅ Completed: {tasks_completed} tasks | ❌ Failed: {tasks_failed} tasks")
    print("=" * 70)
    
    if tasks_failed == 0:
        print("\n" + " " * 20 + "✅ ALL TASKS COMPLETED!")
        print("=" * 70)
        print(f"\n📦 Release ZIP: {OUTPUT_ZIP.name}")
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

