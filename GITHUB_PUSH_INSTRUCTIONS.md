# GitHub Push Instructions

## Repository
- **URL:** https://github.com/itsbhupendrasingh/nuttyfi32
- **Branch:** master

---

## Quick Push - Run This File:
👉 **PUSH_TO_GITHUB.bat** (Double-click)

---

## Manual Push Commands:

### Step 1: Navigate to folder
```cmd
cd "D:\esp32 bsp\esp bsp\nuttyfi32"
```

### Step 2: Initialize Git (if not done)
```cmd
git init
```

### Step 3: Add remote
```cmd
git remote add origin https://github.com/itsbhupendrasingh/nuttyfi32.git
```

### Step 4: Add all files
```cmd
git add .
```

### Step 5: Commit
```cmd
git commit -m "Initial commit: nuttyfi32 BSP v1.0.0"
```

### Step 6: Set branch to master
```cmd
git branch -M master
```

### Step 7: Push to GitHub
```cmd
git push -u origin master
```

---

## If Push Fails:

### Authentication Required:
1. Use GitHub Personal Access Token
2. Or use GitHub Desktop
3. Or configure Git credentials

### First Time Setup:
```cmd
git config --global user.name "itsbhupendrasingh"
git config --global user.email "itsbhupendrasingh@gmail.com"
```

---

## After Push:

1. ✅ Code pushed to GitHub
2. ⚠️ Create Release on GitHub:
   - Go to: https://github.com/itsbhupendrasingh/nuttyfi32/releases
   - Click "Create a new release"
   - Tag: v1.0.0
   - Upload: nuttyfi32-1.0.0.zip
   - Update JSON file with SHA256 and size
   - Upload JSON file to releases

3. ⚠️ Update JSON file:
   - Calculate SHA256 of zip file
   - Update package_nuttyfi32_index.json
   - Push updated JSON

---

## Files Updated:
✅ GitHub URLs updated in:
- package.json
- package_nuttyfi32_index.json

⚠️ Still need to update:
- SHA256 hash in JSON
- File size in JSON

