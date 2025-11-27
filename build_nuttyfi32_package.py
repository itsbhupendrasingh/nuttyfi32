#!/usr/bin/env python3
"""
Build nuttyfi32 BSP Package Script
This script:
1. Extracts the ESP32 BSP ZIP
2. Renames folders/files from esp32 to nuttyfi32 where needed
3. Creates a new ZIP file with correct name
4. Calculates SHA-256 checksum and file size
5. Updates the package JSON file
"""

import os
import json
import zipfile
import shutil
import hashlib
from pathlib import Path

# Configuration
VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent
BSP_SOURCE = BASE_DIR / "arduino-esp32-master"
ZIP_SOURCE = BASE_DIR / "esp32-1.0.6.zip"
OUTPUT_ZIP = BASE_DIR / f"nuttyfi32-{VERSION}.zip"
JSON_FILE = BASE_DIR / "package_nuttyfi32_index.json"
TEMP_DIR = BASE_DIR / "temp_build"

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

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    print(f"Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete!")

def rename_esp32_to_nuttyfi32(directory):
    """Rename esp32 references to nuttyfi32 in folder structure and files"""
    print("Renaming esp32 to nuttyfi32...")
    
    # Files and folders to rename (only package-related, not core files)
    rename_patterns = [
        # Package folder structure
        ("package/package_esp32_index.template.json", "package/package_nuttyfi32_index.template.json"),
    ]
    
    # Rename files
    for old_name, new_name in rename_patterns:
        old_path = directory / old_name
        new_path = directory / new_name
        if old_path.exists():
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
            print(f"  Renamed: {old_name} -> {new_name}")
    
    # Update content in key files (only package name, not architecture)
    files_to_update = [
        "package.json",
        "platform.txt",
        "boards.txt",
    ]
    
    for file_name in files_to_update:
        file_path = directory / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only replace package name references, keep architecture as esp32
            # Replace "ESP32 Arduino" with "nuttyfi32 Arduino" in package.json
            if file_name == "package.json":
                content = content.replace('"name": "framework-arduinoespressif32"', '"name": "framework-arduinoespressif32"')
                # Keep framework name same, just update description if needed
                content = content.replace('"framework-arduinoespressif32"', '"framework-arduinoespressif32"')
            
            # In platform.txt, update name line
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
            
            # In boards.txt, add nuttyfi32 board entry
            if file_name == "boards.txt":
                lines = content.split('\n')
                nuttyfi32_added = False
                
                # Find esp32.name line
                esp32_start = None
                esp32_end = None
                for i, line in enumerate(lines):
                    if line.strip() == "esp32.name=ESP32 Dev Module" and esp32_start is None:
                        esp32_start = i
                    elif esp32_start is not None and esp32_end is None:
                        # Find end of esp32 section (next board that's not esp32.*)
                        if line.strip() and not line.strip().startswith('esp32.') and not line.strip().startswith('#') and not line.strip() == '':
                            # Check if it's a menu item continuation
                            if not line.strip().startswith('esp32.menu.'):
                                esp32_end = i
                                break
                
                if esp32_start is not None:
                    # Find actual end by looking for next board definition
                    if esp32_end is None:
                        esp32_end = len(lines)
                        for i in range(esp32_start + 1, len(lines)):
                            line = lines[i].strip()
                            # Next board definition (has .name= and doesn't start with esp32.)
                            if '.name=' in line and not line.startswith('esp32.') and not line.startswith('#'):
                                esp32_end = i
                                break
                    
                    # Extract all esp32 properties
                    esp32_section = lines[esp32_start:esp32_end]
                    
                    # Create nuttyfi32 section by replacing esp32. with nuttyfi32.
                    nuttyfi32_section = []
                    nuttyfi32_section.append("")
                    nuttyfi32_section.append("##############################################################")
                    nuttyfi32_section.append("# nuttyfi32 Dev Module (same as ESP32 Dev Module)")
                    nuttyfi32_section.append("##############################################################")
                    nuttyfi32_section.append("")
                    
                    for line in esp32_section:
                        if line.strip().startswith('esp32.'):
                            # Replace esp32. with nuttyfi32.
                            nuttyfi32_line = line.replace('esp32.', 'nuttyfi32.', 1)
                            nuttyfi32_section.append(nuttyfi32_line)
                        elif line.strip() == '' or line.strip().startswith('#'):
                            # Keep empty lines and comments
                            nuttyfi32_section.append(line)
                    
                    # Insert nuttyfi32 section after esp32 section
                    lines[esp32_end:esp32_end] = nuttyfi32_section
                    nuttyfi32_added = True
                    print(f"  Added nuttyfi32 board entry to boards.txt")
                
                content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Updated: {file_name}")

def create_zip(source_dir, output_zip):
    """Create ZIP file from directory"""
    print(f"Creating ZIP: {output_zip.name}...")
    
    # Remove old ZIP if exists
    if output_zip.exists():
        output_zip.unlink()
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip temp directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print(f"ZIP created: {output_zip}")
    return output_zip

def update_json_with_checksum(json_file, zip_file, version):
    """Update JSON file with checksum and size"""
    print("Updating JSON file...")
    
    # Calculate checksum and size
    checksum = calculate_sha256(zip_file)
    size = get_file_size(zip_file)
    
    print(f"  Checksum: SHA-256:{checksum}")
    print(f"  Size: {size} bytes")
    
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
    
    print(f"JSON updated: {json_file}")

def main():
    """Main function"""
    print("=" * 60)
    print("nuttyfi32 BSP Package Builder")
    print("=" * 60)
    print()
    
    # Check if source exists
    if not BSP_SOURCE.exists() and not ZIP_SOURCE.exists():
        print(f"ERROR: Neither {BSP_SOURCE.name} folder nor {ZIP_SOURCE.name} found!")
        print("Please ensure you have either:")
        print(f"  - {BSP_SOURCE.name} folder, OR")
        print(f"  - {ZIP_SOURCE.name} file")
        return 1
    
    # Clean temp directory
    if TEMP_DIR.exists():
        print(f"Cleaning temp directory: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir()
    
    try:
        # Extract if ZIP source exists
        if ZIP_SOURCE.exists():
            extract_zip(ZIP_SOURCE, TEMP_DIR)
            # Find extracted folder
            extracted_folders = [d for d in TEMP_DIR.iterdir() if d.is_dir()]
            if extracted_folders:
                work_dir = extracted_folders[0]
            else:
                print("ERROR: No folder found in extracted ZIP!")
                return 1
        else:
            # Use BSP source directly
            print(f"Using BSP source: {BSP_SOURCE}")
            work_dir = TEMP_DIR / "nuttyfi32"
            shutil.copytree(BSP_SOURCE, work_dir)
        
        # Rename esp32 to nuttyfi32 (only package-related)
        rename_esp32_to_nuttyfi32(work_dir)
        
        # Create ZIP
        create_zip(work_dir, OUTPUT_ZIP)
        
        # Update JSON
        update_json_with_checksum(JSON_FILE, OUTPUT_ZIP, VERSION)
        
        print()
        print("=" * 60)
        print("SUCCESS! Package built successfully!")
        print("=" * 60)
        print(f"Output ZIP: {OUTPUT_ZIP}")
        print(f"Updated JSON: {JSON_FILE}")
        print()
        print("Next steps:")
        print("1. Review the generated files")
        print("2. Run push_to_github.py to upload to GitHub")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup temp directory
        if TEMP_DIR.exists():
            print(f"Cleaning up temp directory...")
            shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    exit(main())

