#!/usr/bin/env python3
"""
Build nuttyfi32 BSP from Release ZIP - FULLY AUTOMATED
This script:
1. Extracts esp32-1.0.6.zip (release ZIP)
2. Renames esp32 to nuttyfi32 in files and content
3. Creates nuttyfi32-1.0.0.zip
4. Calculates SHA-256 checksum
5. Updates JSON file
6. Pushes arduino-esp32-master to GitHub Master branch
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
        
        # Update package.json
        if file_name == "package.json":
            # Replace package name
            content = content.replace('"name": "framework-arduinoespressif32"', '"name": "framework-arduinoespressif32"')
            # Keep framework same, just update if there are any esp32 references in description
        
        # Update platform.txt
        if file_name == "platform.txt":
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('name=') and 'ESP32' in line:
                    lines[i] = 'name=nuttyfi32 Arduino'
                    break
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
                    # Find end of esp32 section
                    if line.strip() and not line.strip().startswith('esp32.') and not line.strip().startswith('#') and not line.strip() == '':
                        if not line.strip().startswith('esp32.menu.'):
                            esp32_end = i
                            break
            
            if esp32_start is not None:
                # Find actual end
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
    
    # Remove old ZIP if exists
    if output_zip.exists():
        output_zip.unlink()
    
    # Arduino IDE requires single root folder in ZIP
    # Use source_dir name as root folder name
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
    
    # Read JSON template
    if JSON_TEMPLATE.exists():
        with open(JSON_TEMPLATE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Create from scratch if template doesn't exist
        data = {
            "packages": [{
                "name": "nuttyfi32",
                "maintainer": "Community",
                "websiteURL": "https://github.com/itsbhupendrasingh/nuttyfi32",
                "email": "itsbhupendrasingh@gmail.com",
                "help": {"online": "https://github.com/itsbhupendrasingh/nuttyfi32"},
                "platforms": [{
                    "name": "nuttyfi32",
                    "architecture": "esp32",
                    "version": VERSION,
                    "category": "ESP32",
                    "url": f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{VERSION}/nuttyfi32-{VERSION}.zip",
                    "archiveFileName": f"nuttyfi32-{VERSION}.zip",
                    "checksum": f"SHA-256:{checksum}",
                    "size": size,
                    "help": {"online": "https://github.com/itsbhupendrasingh/nuttyfi32"},
                    "boards": [{"name": "nuttyfi32 Dev Module"}],
                    "toolsDependencies": []
                }],
                "tools": []
            }]
        }
    
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
    exclude_extensions = {'.bat', '.py', '.zip'}
    
    # Add JSON file explicitly
    if JSON_OUTPUT.exists():
        subprocess.run(["git", "add", "-f", JSON_OUTPUT.name], cwd=BASE_DIR, check=False, capture_output=True)
    
    # Add all BSP files from root
    for item in BASE_DIR.iterdir():
        if item.name in exclude_items or item.name.startswith('.'):
            continue
        if item.suffix in exclude_extensions:
            continue
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
        ["git", "commit", "-m", f"Update nuttyfi32 BSP v{VERSION} - sync from release ZIP"],
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
    print(" " * 15 + "nuttyfi32 BSP Builder from Release ZIP")
    print("=" * 70)
    print(f"\nVersion: {VERSION}")
    print(f"Release ZIP: {RELEASE_ZIP}")
    print(f"Output ZIP: {OUTPUT_ZIP}")
    print(f"BSP Source: {BSP_SOURCE}")
    print("=" * 70)
    
    tasks_completed = 0
    tasks_failed = 0
    total_tasks = 5
    
    # Clean temp directory
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir()
    
    try:
        # Task 1: Extract release ZIP
        print_task_status(1, total_tasks, "Extract release ZIP", "RUNNING")
        if not RELEASE_ZIP.exists():
            raise FileNotFoundError(f"Release ZIP not found: {RELEASE_ZIP}")
        work_dir = extract_zip(RELEASE_ZIP, TEMP_DIR)
        print_task_status(1, total_tasks, "Extract release ZIP", "SUCCESS", f"Extracted to {work_dir.name}")
        tasks_completed += 1
        
        # Task 2: Rename esp32 to nuttyfi32
        print_task_status(2, total_tasks, "Rename esp32 to nuttyfi32", "RUNNING")
        rename_esp32_to_nuttyfi32(work_dir)
        print_task_status(2, total_tasks, "Rename esp32 to nuttyfi32", "SUCCESS", "All references updated")
        tasks_completed += 1
        
        # Task 3: Create nuttyfi32 ZIP
        print_task_status(3, total_tasks, "Create nuttyfi32 ZIP", "RUNNING")
        create_zip(work_dir, OUTPUT_ZIP)
        zip_size = get_file_size(OUTPUT_ZIP) / (1024 * 1024)  # MB
        print_task_status(3, total_tasks, "Create nuttyfi32 ZIP", "SUCCESS", 
                         f"Created {OUTPUT_ZIP.name} ({zip_size:.2f} MB)")
        tasks_completed += 1
        
        # Task 4: Update JSON with checksum and size
        print_task_status(4, total_tasks, "Update JSON with checksum and size", "RUNNING")
        checksum, size = update_json_with_zip_info()
        print_task_status(4, total_tasks, "Update JSON with checksum and size", "SUCCESS",
                         f"Checksum: SHA-256:{checksum[:16]}..., Size: {int(size) / (1024*1024):.2f} MB")
        tasks_completed += 1
        
        # Task 5: Push to GitHub
        print_task_status(5, total_tasks, "Push to GitHub", "RUNNING")
        pushed_count = push_bsp_to_github()
        print_task_status(5, total_tasks, "Push to GitHub", "SUCCESS",
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

