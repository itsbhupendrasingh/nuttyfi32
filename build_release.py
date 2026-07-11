#!/usr/bin/env python3
"""
Build script for NuttyFi32 Arduino Board Support Package.

Creates a release zip, computes SHA-256 checksum and file size,
then updates package_nuttyfi32_index.json with the correct values.

Usage:
    python build_release.py
    python build_release.py --version 1.0.0
"""

import argparse
import copy
import hashlib
import json
import os
import zipfile

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

INCLUDE_DIRS = [
    "cores",
    "libraries",
    "tools",
    "variants",
]

INCLUDE_FILES = [
    "boards.txt",
    "platform.txt",
    "programmers.txt",
]

EXCLUDE_PATTERNS = [
    ".git",
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
]


def should_exclude(path):
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path:
            return True
    return False


def build_zip(version):
    zip_name = f"nuttyfi32-{version}.zip"
    zip_path = os.path.join(REPO_DIR, zip_name)
    prefix = f"nuttyfi32-{version}"

    print(f"Building {zip_name}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in INCLUDE_FILES:
            full = os.path.join(REPO_DIR, f)
            if os.path.exists(full):
                arcname = f"{prefix}/{f}"
                zf.write(full, arcname)
                print(f"  + {arcname}")

        for d in INCLUDE_DIRS:
            dir_path = os.path.join(REPO_DIR, d)
            if not os.path.isdir(dir_path):
                continue
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [x for x in dirs if not should_exclude(x)]
                for fname in files:
                    if should_exclude(fname):
                        continue
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, REPO_DIR)
                    arcname = f"{prefix}/{rel}"
                    zf.write(full, arcname)

    file_size = os.path.getsize(zip_path)

    sha256 = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    checksum = sha256.hexdigest()

    print(f"\nZip created: {zip_path}")
    print(f"Size: {file_size} bytes")
    print(f"SHA-256: {checksum}")

    return zip_path, file_size, checksum


def version_key(v):
    """Sort key for a semver-ish version string, so 1.0.10 > 1.0.9."""
    parts = []
    for chunk in str(v).split("."):
        num = ""
        while chunk and chunk[0].isdigit():
            num += chunk[0]
            chunk = chunk[1:]
        parts.append((int(num) if num else 0, chunk))
    return parts


def update_package_index(version, size, checksum):
    """Add this version to the index, keeping every previously released version.

    Boards Manager only offers versions that are listed in platforms[], so an
    entry must never be removed once it has been published -- dropping one makes
    that release uninstallable even though its asset is still on GitHub.
    """
    index_path = os.path.join(REPO_DIR, "package_nuttyfi32_index.json")

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    platforms = data["packages"][0]["platforms"]
    if not platforms:
        raise SystemExit("index has no platform entries to use as a template")

    existing = next((p for p in platforms if p["version"] == version), None)
    if existing is None:
        newest = max(platforms, key=lambda p: version_key(p["version"]))
        existing = copy.deepcopy(newest)
        platforms.append(existing)
        action = "added"
    else:
        action = "updated"

    existing["version"] = version
    existing["checksum"] = f"SHA-256:{checksum}"
    existing["size"] = str(size)
    existing["url"] = f"https://github.com/itsbhupendrasingh/nuttyfi32/releases/download/{version}/nuttyfi32-{version}.zip"
    existing["archiveFileName"] = f"nuttyfi32-{version}.zip"

    platforms.sort(key=lambda p: version_key(p["version"]))

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nUpdated {index_path}")
    print(f"  {action} version: {version}")
    print(f"  checksum: SHA-256:{checksum}")
    print(f"  size: {size}")
    print(f"  index now offers: {', '.join(p['version'] for p in platforms)}")


def main():
    parser = argparse.ArgumentParser(description="Build NuttyFi32 BSP release")
    parser.add_argument("--version", default="1.0.0", help="Version number (default: 1.0.0)")
    args = parser.parse_args()

    zip_path, size, checksum = build_zip(args.version)
    update_package_index(args.version, size, checksum)

    print("\nDone! Next steps:")
    print(f"  1. Upload {os.path.basename(zip_path)} to GitHub release {args.version}")
    print(f"  2. Push updated package_nuttyfi32_index.json to repo")
    print(f"  3. Users add this URL in Arduino IDE preferences:")
    print(f"     https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/Master/package_nuttyfi32_index.json")


if __name__ == "__main__":
    main()
