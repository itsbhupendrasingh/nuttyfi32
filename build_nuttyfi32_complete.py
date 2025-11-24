#!/usr/bin/env python3
"""
Complete nuttyfi32 BSP Package Builder and Pusher
This SINGLE script does everything:
1. Cleans old ZIP files
2. Extracts ESP32 BSP
3. Renames package references
4. Creates new ZIP with correct name
5. Calculates checksum and updates JSON
6. Pushes to GitHub (optional)
"""

import os
import json
import zipfile
import shutil
import hashlib
import subprocess
import glob
import sys
from pathlib import Path

# ==================== CONFIGURATION ====================
VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
BSP_SOURCE = BASE_DIR / "arduino-esp32-master"
ZIP_SOURCE = BASE_DIR / "esp32-1.0.6.zip"  # Will auto-detect any esp32-*.zip
OUTPUT_ZIP = BASE_DIR / f"nuttyfi32-{VERSION}.zip"
JSON_FILE = BASE_DIR / "package_nuttyfi32_index.json"
TEMP_DIR = BASE_DIR / "temp_build"
GITHUB_REPO = "https://github.com/itsbhupendrasingh/nuttyfi32.git"
GITHUB_BRANCH = "Master"
PUSH_TO_GITHUB = True  # Set to True to auto-push after build
# =======================================================

def calculate_sha256(file_path):
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().upper()

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def clean_old_zips():
    """Delete all old nuttyfi32-*.zip files"""
    old_zips = list(BASE_DIR.glob("nuttyfi32-*.zip"))
    deleted_count = 0
    for old_zip in old_zips:
        if old_zip != OUTPUT_ZIP:  # Don't delete the one we're about to create
            old_zip.unlink()
            deleted_count += 1
    return deleted_count

def find_esp32_source():
    """Find ESP32 BSP source (folder or ZIP)"""
    # Check for folder first
    if BSP_SOURCE.exists() and BSP_SOURCE.is_dir():
        return "folder", BSP_SOURCE
    
    # Check for specific ZIP
    if ZIP_SOURCE.exists():
        return "zip", ZIP_SOURCE
    
    # Check for any esp32-*.zip
    esp32_zips = list(BASE_DIR.glob("esp32-*.zip"))
    if esp32_zips:
        return "zip", esp32_zips[0]
    
    return None, None

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    # Find extracted folder
    extracted_folders = [d for d in extract_to.iterdir() if d.is_dir()]
    if extracted_folders:
        return extracted_folders[0]
    return extract_to

def rename_esp32_to_nuttyfi32(directory):
    """Rename esp32 references to nuttyfi32 in files"""
    changes_made = []
    
    # Update platform.txt
    platform_file = directory / "platform.txt"
    if platform_file.exists():
        with open(platform_file, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('name=') and 'ESP32' in line:
                lines[i] = 'name=nuttyfi32 Arduino'
                changes_made.append("platform.txt")
                break
        with open(platform_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    # Update boards.txt - Add nuttyfi32 board entry
    boards_file = directory / "boards.txt"
    if boards_file.exists():
        with open(boards_file, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        # Find esp32.name line
        esp32_start = None
        esp32_end = None
        for i, line in enumerate(lines):
            if line.strip() == "esp32.name=ESP32 Dev Module" and esp32_start is None:
                esp32_start = i
            elif esp32_start is not None and esp32_end is None:
                # Find end of esp32 section
                if line.strip() and not line.strip().startswith('esp32.') and not line.strip().startswith('#') and line.strip() != '':
                    if not line.strip().startswith('esp32.menu.'):
                        esp32_end = i
                        break
        
        if esp32_start is not None:
            if esp32_end is None:
                # Find next board definition
                for i in range(esp32_start + 1, len(lines)):
                    line = lines[i].strip()
                    if '.name=' in line and not line.startswith('esp32.') and not line.startswith('#'):
                        esp32_end = i
                        break
                if esp32_end is None:
                    esp32_end = len(lines)
            
            # Extract esp32 section
            esp32_section = lines[esp32_start:esp32_end]
            
            # Create nuttyfi32 section
            nuttyfi32_section = [
                "",
                "##############################################################",
                "# nuttyfi32 Dev Module (same as ESP32 Dev Module)",
                "##############################################################",
                ""
            ]
            
            for line in esp32_section:
                if line.strip().startswith('esp32.'):
                    nuttyfi32_line = line.replace('esp32.', 'nuttyfi32.', 1)
                    nuttyfi32_section.append(nuttyfi32_line)
                elif line.strip() == '' or line.strip().startswith('#'):
                    nuttyfi32_section.append(line)
            
            # Insert after esp32 section
            lines[esp32_end:esp32_end] = nuttyfi32_section
            
            with open(boards_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            changes_made.append("boards.txt (added nuttyfi32 board)")
    
    return ", ".join(changes_made) if changes_made else "No changes needed"

def create_zip(source_dir, output_zip):
    """Create ZIP file from directory - Arduino IDE expects root folder with all files"""
    # Remove old ZIP if exists
    if output_zip.exists():
        output_zip.unlink()
    
    file_count = 0
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip hidden and temp directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                # Arduino IDE expects files at root level of ZIP
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
                file_count += 1
    
    return file_count

def update_json_with_checksum(json_file, zip_file, version):
    """Update JSON file with checksum and size"""
    # Calculate checksum and size
    checksum = calculate_sha256(zip_file)
    size = get_file_size(zip_file)
    
    # Read JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update platform entry
    platform = data['packages'][0]['platforms'][0]
    platform['checksum'] = f"SHA-256:{checksum}"
    platform['size'] = str(size)
    platform['version'] = version
    platform['url'] = f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{version}/nuttyfi32-{version}.zip"
    platform['archiveFileName'] = f"nuttyfi32-{version}.zip"
    
    # Write updated JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return checksum, size

def check_git_installed():
    """Check if git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except:
        return False

def init_git_repo():
    """Initialize git repository"""
    git_dir = BASE_DIR / ".git"
    is_new_repo = False
    
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "branch", "-M", GITHUB_BRANCH], cwd=BASE_DIR, check=True)
        is_new_repo = True
    
    # Check remote
    try:
        subprocess.run(["git", "remote", "get-url", "origin"], cwd=BASE_DIR, check=True, capture_output=True)
    except:
        subprocess.run(["git", "remote", "add", "origin", GITHUB_REPO], cwd=BASE_DIR, check=True)
    
    return is_new_repo

def create_gitignore():
    """Create .gitignore file - only exclude build artifacts, not source code"""
    gitignore_file = BASE_DIR / ".gitignore"
    gitignore_content = """# Python cache
__pycache__/
*.py[cod]
*$py.class
*.pyc

# Build temporary files
temp_build/

# Large ZIP files (upload via releases)
*.zip
!nuttyfi32-*.zip

# Original ESP32 BSP download ZIPs
esp32-*.zip
arduino-esp32-*.zip

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Note: arduino-esp32-master/ folder is INCLUDED - this is the source code!
"""
    # Always update .gitignore to ensure it's correct
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    return True

def add_files_to_git():
    """Add ALL files to git - complete arduino-esp32-master folder and all project files"""
    files_added = []
    
    # Create/update .gitignore first
    create_gitignore()
    subprocess.run(["git", "add", ".gitignore"], cwd=BASE_DIR, check=False)
    files_added.append(".gitignore")
    
    # Add ENTIRE arduino-esp32-master folder with ALL files and subfolders
    bsp_source = BASE_DIR / "arduino-esp32-master"
    if bsp_source.exists() and bsp_source.is_dir():
        print(f"    Adding COMPLETE ESP32 BSP source: arduino-esp32-master/")
        print(f"    (This includes ALL files, folders, cores, libraries, tools, etc.)")
        # Add entire folder recursively - ALL files
        subprocess.run(["git", "add", "arduino-esp32-master/"], cwd=BASE_DIR, check=False)
        # Count files being added
        import os
        file_count = sum([len(files) for r, d, files in os.walk(bsp_source)])
        files_added.append(f"arduino-esp32-master/ ({file_count} files - COMPLETE)")
    
    # Add all project files in root
    print(f"    Adding project files...")
    project_files = [
        "package_nuttyfi32_index.json",
        "build_nuttyfi32_complete.py",
        "push_to_github.py",
        "push_with_token.py",
        "build_and_push.bat",
        "README.md",
        "QUICK_START.md",
        "GITHUB_SETUP.md",
        "FIX_GITHUB_PUSH.md",
        "PERSONAL_ACCESS_TOKEN_GUIDE.md",
        "check_github_setup.py",
    ]
    
    for file_pattern in project_files:
        file_path = BASE_DIR / file_pattern
        if file_path.exists():
            try:
                subprocess.run(["git", "add", str(file_path.relative_to(BASE_DIR))], cwd=BASE_DIR, check=True)
                files_added.append(file_path.name)
            except:
                pass
    
    return files_added

def commit_and_push_to_github(is_new_repo=False):
    """Commit and push to GitHub"""
    if not check_git_installed():
        return False, "Git not installed. Please install Git from https://git-scm.com/downloads"
    
    try:
        # Initialize
        is_new = init_git_repo()
        if is_new:
            is_new_repo = True
        
        # Add files
        files_added = add_files_to_git()
        if not files_added:
            return False, "No files to add. Check if files exist."
        
        # Check if there are changes
        try:
            result = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, check=True, capture_output=True, text=True)
            if not result.stdout.strip():
                return False, "No changes to commit (repository is up to date)"
        except Exception as e:
            pass
        
        # Commit
        if is_new_repo:
            commit_msg = f"Initial commit: nuttyfi32 package v{VERSION}"
        else:
            commit_msg = f"Update nuttyfi32 package v{VERSION}"
        
        try:
            commit_result = subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True, capture_output=True, text=True)
            print(f"    Commit message: {commit_msg}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in e.stderr.lower():
                return False, "Nothing to commit (no changes detected)"
            return False, f"Commit failed: {e.stderr}"
        
        # Push with detailed error handling
        try:
            if is_new_repo:
                push_cmd = ["git", "push", "-u", "origin", GITHUB_BRANCH, "--force"]
            else:
                push_cmd = ["git", "push", "origin", GITHUB_BRANCH, "--force"]
            
            print(f"    Pushing to: {GITHUB_REPO}")
            print(f"    Branch: {GITHUB_BRANCH}")
            print(f"\n    ⚠️  AUTHENTICATION REQUIRED:")
            print(f"    When prompted, enter:")
            print(f"    Username: itsbhupendrasingh")
            print(f"    Password: [Your Personal Access Token - NOT GitHub password]")
            print(f"\n    💡 Note: ZIP file (38MB) excluded from push to avoid timeout")
            print(f"    Upload ZIP manually via GitHub Release after push")
            print()
            
            # Run push command - this will prompt for credentials if needed
            # Increased timeout for large files (ZIP is 38MB)
            push_result = subprocess.run(
                push_cmd, 
                cwd=BASE_DIR, 
                check=True, 
                capture_output=False,  # Don't capture so user can see prompts
                text=True,
                timeout=600  # 10 minutes timeout for large file uploads
            )
            
            return True, f"Successfully pushed {len(files_added)} files to {GITHUB_BRANCH} branch"
            
        except subprocess.CalledProcessError as e:
            # Try to capture error if possible
            error_output = ""
            try:
                if hasattr(e, 'stderr') and e.stderr:
                    error_output += e.stderr
                if hasattr(e, 'stdout') and e.stdout:
                    error_output += e.stdout
            except:
                pass
            
            if not error_output:
                error_output = str(e)
            
            error_lower = error_output.lower()
            
            # Parse common errors
            if "authentication failed" in error_lower or "permission denied" in error_lower or "403" in error_output or "forbidden" in error_lower or "invalid username or password" in error_lower:
                return False, f"Authentication failed - Need Personal Access Token.\n   \n   Steps to fix:\n   1. Go to: https://github.com/settings/tokens\n   2. Click 'Generate new token (classic)'\n   3. Name: 'nuttyfi32-push'\n   4. Select: 'repo' (full control)\n   5. Click 'Generate token'\n   6. COPY the token (starts with 'ghp_')\n   7. Run script again\n   8. When prompted:\n      Username: itsbhupendrasingh\n      Password: [Paste token here - NOT your GitHub password]"
            
            elif "remote: repository not found" in error_lower or "404" in error_output:
                return False, f"Repository not found.\n   But repository exists at: {GITHUB_REPO}\n   Check if you have access permissions"
            
            elif "could not read username" in error_lower:
                return False, f"Credentials prompt failed.\n   Solution: Run manually:\n   git push -u origin Master\n   Then enter:\n   Username: itsbhupendrasingh\n   Password: [Personal Access Token]"
            
            elif "refusing to merge" in error_lower or "unrelated histories" in error_lower:
                return False, f"Branch history conflict.\n   Solution:\n   cd \"{BASE_DIR}\"\n   git pull origin {GITHUB_BRANCH} --allow-unrelated-histories\n   Then run script again"
            
            else:
                return False, f"Push failed.\n   Error: {error_output[:300]}\n   \n   Try manual push:\n   cd \"{BASE_DIR}\"\n   git push -u origin Master\n   \n   Use Personal Access Token as password"
                
        except subprocess.TimeoutExpired:
            return False, f"Push timeout (10 minutes exceeded).\n   Large files may take time.\n   Solution:\n   1. Check internet connection\n   2. Try manual push: git push -u origin Master\n   3. Or exclude large files and push separately"
            
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def print_task_status(task_num, total_tasks, task_name, status, details=""):
    """Print task status with clear indicators"""
    status_icon = "✅" if status == "DONE" else "❌" if status == "FAILED" else "⏳"
    status_text = "COMPLETED" if status == "DONE" else "FAILED" if status == "FAILED" else "IN PROGRESS"
    print(f"\n[{task_num}/{total_tasks}] {task_name}")
    print(f"    Status: {status_icon} {status_text}")
    if details:
        print(f"    {details}")
    print()

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 15 + "nuttyfi32 Complete Package Builder")
    print("=" * 70)
    print()
    
    # Task tracking
    tasks = {
        "clean_old_zips": {"name": "Clean Old ZIP Files", "status": "PENDING", "details": ""},
        "find_source": {"name": "Find ESP32 BSP Source", "status": "PENDING", "details": ""},
        "extract_prepare": {"name": "Extract/Prepare BSP", "status": "PENDING", "details": ""},
        "apply_changes": {"name": "Apply nuttyfi32 Changes", "status": "PENDING", "details": ""},
        "create_zip": {"name": "Create Package ZIP", "status": "PENDING", "details": ""},
        "update_json": {"name": "Update Package JSON", "status": "PENDING", "details": ""},
        "cleanup": {"name": "Cleanup Temp Files", "status": "PENDING", "details": ""}
    }
    
    total_tasks = len(tasks)
    task_num = 0
    
    try:
        # Task 1: Clean old ZIPs
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["clean_old_zips"]["name"], "IN PROGRESS")
        try:
            deleted_count = clean_old_zips()
            tasks["clean_old_zips"]["status"] = "DONE"
            if deleted_count > 0:
                tasks["clean_old_zips"]["details"] = f"Removed {deleted_count} old ZIP file(s)"
            else:
                tasks["clean_old_zips"]["details"] = "No old ZIP files found"
            print_task_status(task_num, total_tasks, tasks["clean_old_zips"]["name"], "DONE", tasks["clean_old_zips"]["details"])
        except Exception as e:
            tasks["clean_old_zips"]["status"] = "FAILED"
            tasks["clean_old_zips"]["details"] = f"Error: {e}"
            print_task_status(task_num, total_tasks, tasks["clean_old_zips"]["name"], "FAILED", tasks["clean_old_zips"]["details"])
        
        # Task 2: Find source
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["find_source"]["name"], "IN PROGRESS")
        source_type, source_path = find_esp32_source()
        if not source_path:
            tasks["find_source"]["status"] = "FAILED"
            tasks["find_source"]["details"] = "No ESP32 BSP source found!"
            print_task_status(task_num, total_tasks, tasks["find_source"]["name"], "FAILED", tasks["find_source"]["details"])
            print("\nPlease ensure you have either:")
            print(f"  - {BSP_SOURCE.name} folder, OR")
            print(f"  - esp32-*.zip file")
            input("\nPress Enter to exit...")
            return 1
        tasks["find_source"]["status"] = "DONE"
        tasks["find_source"]["details"] = f"Found: {source_path.name} ({source_type})"
        print_task_status(task_num, total_tasks, tasks["find_source"]["name"], "DONE", tasks["find_source"]["details"])
        
        # Task 3: Prepare work directory
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["extract_prepare"]["name"], "IN PROGRESS")
        try:
            if TEMP_DIR.exists():
                shutil.rmtree(TEMP_DIR)
            TEMP_DIR.mkdir()
            
            if source_type == "zip":
                work_dir = extract_zip(source_path, TEMP_DIR)
                tasks["extract_prepare"]["details"] = f"Extracted {source_path.name}"
            else:
                work_dir = TEMP_DIR / "nuttyfi32"
                shutil.copytree(source_path, work_dir)
                tasks["extract_prepare"]["details"] = f"Copied {source_path.name} to work directory"
            
            tasks["extract_prepare"]["status"] = "DONE"
            print_task_status(task_num, total_tasks, tasks["extract_prepare"]["name"], "DONE", tasks["extract_prepare"]["details"])
        except Exception as e:
            tasks["extract_prepare"]["status"] = "FAILED"
            tasks["extract_prepare"]["details"] = f"Error: {e}"
            print_task_status(task_num, total_tasks, tasks["extract_prepare"]["name"], "FAILED", tasks["extract_prepare"]["details"])
            input("\nPress Enter to exit...")
            return 1
        
        # Task 4: Apply changes
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["apply_changes"]["name"], "IN PROGRESS")
        try:
            # Apply changes to work directory (for ZIP)
            changes = rename_esp32_to_nuttyfi32(work_dir)
            
            # IMPORTANT: Also apply changes to original BSP source folder for GitHub push
            source_changes = ""
            if BSP_SOURCE.exists() and BSP_SOURCE.is_dir():
                print(f"    Applying changes to original BSP source (arduino-esp32-master/)...")
                try:
                    source_changes = rename_esp32_to_nuttyfi32(BSP_SOURCE)
                    print(f"    ✓ Updated original source: {source_changes}")
                except Exception as e:
                    print(f"    ⚠️  Warning: Could not update original source: {e}")
                    source_changes = f"Warning: {e}"
            
            tasks["apply_changes"]["status"] = "DONE"
            if source_changes:
                tasks["apply_changes"]["details"] = f"Updated: {changes} | Original source: {source_changes}"
            else:
                tasks["apply_changes"]["details"] = f"Updated: {changes}"
            print_task_status(task_num, total_tasks, tasks["apply_changes"]["name"], "DONE", tasks["apply_changes"]["details"])
        except Exception as e:
            tasks["apply_changes"]["status"] = "FAILED"
            tasks["apply_changes"]["details"] = f"Error: {e}"
            print_task_status(task_num, total_tasks, tasks["apply_changes"]["name"], "FAILED", tasks["apply_changes"]["details"])
            input("\nPress Enter to exit...")
            return 1
        
        # Task 5: Create ZIP
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["create_zip"]["name"], "IN PROGRESS")
        try:
            file_count = create_zip(work_dir, OUTPUT_ZIP)
            zip_size = get_file_size(OUTPUT_ZIP) / 1024 / 1024
            tasks["create_zip"]["status"] = "DONE"
            tasks["create_zip"]["details"] = f"Created {OUTPUT_ZIP.name} ({file_count} files, {zip_size:.2f} MB)"
            print_task_status(task_num, total_tasks, tasks["create_zip"]["name"], "DONE", tasks["create_zip"]["details"])
        except Exception as e:
            tasks["create_zip"]["status"] = "FAILED"
            tasks["create_zip"]["details"] = f"Error: {e}"
            print_task_status(task_num, total_tasks, tasks["create_zip"]["name"], "FAILED", tasks["create_zip"]["details"])
            input("\nPress Enter to exit...")
            return 1
        
        # Task 6: Update JSON
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["update_json"]["name"], "IN PROGRESS")
        try:
            checksum, size = update_json_with_checksum(JSON_FILE, OUTPUT_ZIP, VERSION)
            size_mb = size / 1024 / 1024
            tasks["update_json"]["status"] = "DONE"
            tasks["update_json"]["details"] = f"Updated {JSON_FILE.name} (SHA-256: {checksum[:16]}..., {size_mb:.2f} MB)"
            print_task_status(task_num, total_tasks, tasks["update_json"]["name"], "DONE", tasks["update_json"]["details"])
        except Exception as e:
            tasks["update_json"]["status"] = "FAILED"
            tasks["update_json"]["details"] = f"Error: {e}"
            print_task_status(task_num, total_tasks, tasks["update_json"]["name"], "FAILED", tasks["update_json"]["details"])
            input("\nPress Enter to exit...")
            return 1
        
        # Task 7: Cleanup
        task_num += 1
        print_task_status(task_num, total_tasks, tasks["cleanup"]["name"], "IN PROGRESS")
        try:
            if TEMP_DIR.exists():
                shutil.rmtree(TEMP_DIR)
            tasks["cleanup"]["status"] = "DONE"
            tasks["cleanup"]["details"] = "Temp files removed"
            print_task_status(task_num, total_tasks, tasks["cleanup"]["name"], "DONE", tasks["cleanup"]["details"])
        except Exception as e:
            tasks["cleanup"]["status"] = "FAILED"
            tasks["cleanup"]["details"] = f"Warning: {e}"
            print_task_status(task_num, total_tasks, tasks["cleanup"]["name"], "FAILED", tasks["cleanup"]["details"])
        
        # Task 8: Push to GitHub (if enabled)
        if PUSH_TO_GITHUB:
            task_num += 1
            total_tasks += 1
            tasks["push_github"] = {"name": "Push to GitHub", "status": "PENDING", "details": ""}
            print_task_status(task_num, total_tasks, tasks["push_github"]["name"], "IN PROGRESS")
            try:
                git_dir = BASE_DIR / ".git"
                is_new_repo = not git_dir.exists()
                success, message = commit_and_push_to_github(is_new_repo)
                if success:
                    tasks["push_github"]["status"] = "DONE"
                    tasks["push_github"]["details"] = message
                    print_task_status(task_num, total_tasks, tasks["push_github"]["name"], "DONE", tasks["push_github"]["details"])
                else:
                    tasks["push_github"]["status"] = "FAILED"
                    # Format multi-line error messages
                    if "\n" in message:
                        details_lines = message.split("\n")
                        tasks["push_github"]["details"] = details_lines[0] if details_lines[0] else "Push failed"
                        # Print full error with proper formatting
                        print(f"\n    ⚠️  Detailed Error Information:")
                        for i, line in enumerate(details_lines):
                            if line.strip():
                                print(f"    {line}")
                    else:
                        tasks["push_github"]["details"] = message
                    print_task_status(task_num, total_tasks, tasks["push_github"]["name"], "FAILED", tasks["push_github"]["details"])
                    
                    # Show troubleshooting tips
                    print(f"\n    💡 Quick Fix:")
                    print(f"    1. Run diagnostic: python check_github_setup.py")
                    print(f"    2. Check FIX_GITHUB_PUSH.md for detailed solutions")
                    print(f"    3. Or push manually: python push_to_github.py")
            except Exception as e:
                tasks["push_github"]["status"] = "FAILED"
                tasks["push_github"]["details"] = f"Error: {e}"
                print_task_status(task_num, total_tasks, tasks["push_github"]["name"], "FAILED", tasks["push_github"]["details"])
        
        # Final Summary
        print("\n" + "=" * 70)
        print(" " * 25 + "TASK SUMMARY")
        print("=" * 70)
        
        completed = sum(1 for t in tasks.values() if t["status"] == "DONE")
        failed = sum(1 for t in tasks.values() if t["status"] == "FAILED")
        
        for i, (key, task) in enumerate(tasks.items(), 1):
            icon = "✅" if task["status"] == "DONE" else "❌" if task["status"] == "FAILED" else "⏳"
            status = "COMPLETED" if task["status"] == "DONE" else "FAILED" if task["status"] == "FAILED" else "PENDING"
            print(f"  {i}. {icon} {task['name']:<30} [{status}]")
            if task["details"]:
                print(f"     └─ {task['details']}")
        
        print("=" * 70)
        print(f"\nTotal Tasks: {total_tasks} | ✅ Completed: {completed} | ❌ Failed: {failed}")
        
        if failed == 0:
            print("\n" + "=" * 70)
            print(" " * 20 + "✅ SUCCESS! Package Built Successfully!")
            print("=" * 70)
            print(f"\n📦 Output ZIP: {OUTPUT_ZIP.name}")
            print(f"📄 Updated JSON: {JSON_FILE.name}")
            
            # Check if GitHub push was attempted
            github_pushed = False
            if "push_github" in tasks:
                if tasks["push_github"]["status"] == "DONE":
                    github_pushed = True
                    print(f"\n🚀 GitHub Push: ✅ Successfully pushed to {GITHUB_BRANCH} branch")
                    print(f"   Repository: {GITHUB_REPO}")
            
            print("\n📋 Next Steps:")
            if not github_pushed and PUSH_TO_GITHUB:
                print("1. GitHub push failed - you can push manually:")
                print("   python push_to_github.py")
            elif not PUSH_TO_GITHUB:
                print("1. Push to GitHub (optional):")
                print("   python push_to_github.py")
            
            print("2. Create GitHub release:")
            print(f"   https://github.com/itsbhupendrasingh/nuttyfi32/releases/new")
            print(f"   - Tag: {VERSION}")
            print(f"   - Upload: {OUTPUT_ZIP.name}")
            print("\n3. Arduino IDE JSON URL:")
            print(f"   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/{GITHUB_BRANCH}/package_nuttyfi32_index.json")
        else:
            print("\n" + "=" * 70)
            print(" " * 20 + "⚠️  WARNING! Some Tasks Failed")
            print("=" * 70)
            print("\nPlease check the errors above and try again.")
        
        print("=" * 70)
        
        # Pause at the end
        input("\nPress Enter to continue...")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(" " * 25 + "❌ FATAL ERROR")
        print("=" * 70)
        print(f"\nError: {e}")
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        print("=" * 70)
        input("\nPress Enter to exit...")
        return 1
    
    finally:
        # Always cleanup temp directory
        if TEMP_DIR.exists():
            try:
                shutil.rmtree(TEMP_DIR)
            except:
                pass

if __name__ == "__main__":
    exit(main())

