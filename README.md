# nuttyfi32 BSP Package Builder

This repository contains scripts to build and publish the **nuttyfi32** Arduino BSP package, which is a customized version of ESP32 Arduino core.

## 📋 Requirements

- Python 3.6 or higher
- Git (for pushing to GitHub)
- ESP32 BSP source files (either `arduino-esp32-master` folder or `esp32-*.zip`)

## 🚀 Quick Start

### Option 1: Automated Build and Push (Recommended)

Simply run:
```batch
build_and_push.bat
```

This will:
1. Build the nuttyfi32 package ZIP
2. Calculate checksum and update JSON
3. Push to GitHub

### Option 2: Manual Steps

#### Step 1: Build Package
```batch
python build_nuttyfi32_package.py
```

This script will:
- Extract ESP32 BSP (if ZIP provided)
- Rename package references from `esp32` to `nuttyfi32`
- Add `nuttyfi32 Dev Module` board entry
- Create `nuttyfi32-1.0.0.zip`
- Calculate SHA-256 checksum
- Update `package_nuttyfi32_index.json`

#### Step 2: Push to GitHub
```batch
python push_to_github.py
```

This script will:
- Initialize git repository (if needed)
- Commit changes
- Push to GitHub `Master` branch

#### Step 3: Create GitHub Release

After pushing, create a GitHub release:
1. Go to: https://github.com/itsbhupendrasingh/nuttyfi32/releases/new
2. Tag: `1.0.0`
3. Title: `nuttyfi32 v1.0.0`
4. Upload: `nuttyfi32-1.0.0.zip`

## 📁 File Structure

```
D:\esp32 bsp\v1.0\
├── arduino-esp32-master\     # ESP32 BSP source (or use ZIP)
├── esp32-1.0.6.zip          # Alternative: ESP32 BSP ZIP source
├── package_nuttyfi32_index.json  # Package index JSON
├── build_nuttyfi32_package.py   # Build script
├── push_to_github.py             # GitHub push script
├── build_and_push.bat            # All-in-one script
└── README.md                      # This file
```

## 🔧 Configuration

Edit these variables in the scripts to change version:

- `VERSION = "1.0.0"` in `build_nuttyfi32_package.py`
- `VERSION = "1.0.0"` in `push_to_github.py`

## 📦 Package Details

- **Package Name**: nuttyfi32
- **Architecture**: esp32 (kept as-is for compatibility)
- **Board Name**: nuttyfi32 Dev Module
- **GitHub URL**: https://github.com/itsbhupendrasingh/nuttyfi32

## 🎯 Usage in Arduino IDE

1. Open Arduino IDE
2. Go to **File > Preferences**
3. In **Additional Board Manager URLs**, add:
   ```
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/Master/package_nuttyfi32_index.json
   ```
4. Go to **Tools > Board > Boards Manager**
5. Search for **nuttyfi32**
6. Install the package
7. Select **Tools > Board > nuttyfi32 Dev Module**

## ✅ What Gets Changed

- Package name: `esp32` → `nuttyfi32`
- Platform name in `platform.txt`: `ESP32 Arduino` → `nuttyfi32 Arduino`
- Board entry added: `nuttyfi32 Dev Module` (in `boards.txt`)
- JSON package index updated with correct URLs and checksums

## ⚠️ Important Notes

- **Architecture remains `esp32`**: Core files keep `esp32` architecture for compatibility
- **All ESP32 boards still work**: ESP32 Dev Board, ESP32-S3, etc. all available
- **Version sync**: Make sure version in scripts matches JSON and release tag

## 🐛 Troubleshooting

### Build fails
- Check if `arduino-esp32-master` folder or `esp32-*.zip` exists
- Ensure Python 3.6+ is installed
- Check file permissions

### Push fails
- Verify Git is installed: `git --version`
- Check GitHub credentials are configured
- Ensure repository exists at: https://github.com/itsbhupendrasingh/nuttyfi32

### Package not found in Arduino IDE
- Verify JSON URL is correct
- Check GitHub branch name is `Master` (capital M)
- Ensure release is created with correct tag

## 📝 Version History

- **v1.0.0**: Initial release

## 🤝 Support

For issues or questions, visit: https://github.com/itsbhupendrasingh/nuttyfi32

