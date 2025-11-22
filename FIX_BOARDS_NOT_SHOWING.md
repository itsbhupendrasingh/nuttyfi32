# Fix: Boards Not Showing in Arduino IDE

## 🔴 Main Problem
Arduino IDE **rejects JSON files with placeholder values**. Your JSON has:
- `"checksum": "SHA-256:PLACEHOLDER_SHA256_HASH_HERE"` ❌
- `"size": "PLACEHOLDER_SIZE_HERE"` ❌

Arduino IDE requires **real SHA256 hash and file size**.

---

## ✅ Solution Steps

### Step 1: Get SHA256 and Size from Zip File

**PowerShell Command:**
```powershell
cd "D:\esp32 bsp\esp bsp"
$file = Get-Item "nuttyfi32-1.0.0.zip"
$size = $file.Length
$hash = (Get-FileHash -Path "nuttyfi32-1.0.0.zip" -Algorithm SHA256).Hash
Write-Host "Size: $size"
Write-Host "SHA256: $hash"
```

**Or use Python:**
```cmd
cd "D:\esp32 bsp\esp bsp"
python update_json_simple.py
```

### Step 2: Update JSON File

Open: `nuttyfi32/package/package_nuttyfi32_index.json`

**Line 19:** Replace:
```json
"checksum": "SHA-256:PLACEHOLDER_SHA256_HASH_HERE"
```
With:
```json
"checksum": "SHA-256:YOUR_ACTUAL_HASH_HERE"
```

**Line 20:** Replace:
```json
"size": "PLACEHOLDER_SIZE_HERE"
```
With:
```json
"size": "YOUR_ACTUAL_SIZE_HERE"
```

### Step 3: Verify JSON File is Valid

1. Test JSON syntax: https://jsonlint.com/
2. Make sure no errors

### Step 4: Push to GitHub

```cmd
cd "D:\esp32 bsp\esp bsp\nuttyfi32"
git add package/package_nuttyfi32_index.json
git commit -m "Fix: Update SHA256 and size in JSON"
git push origin master
```

### Step 5: Verify GitHub URL

Open in browser:
```
https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
```

**You should see:**
- JSON content (not HTML)
- Real SHA256 hash (not PLACEHOLDER)
- Real size (not PLACEHOLDER)

### Step 6: Restart Arduino IDE

1. **Close Arduino IDE completely**
2. **Reopen Arduino IDE**
3. Go to **Tools** → **Board** → **Boards Manager**
4. Search for **"nuttyfi32"**
5. Board should appear now! ✅

---

## 🔍 Other Possible Issues

### Issue 1: Wrong Branch Name
If your default branch is **"main"** (not "master"), use:
```
https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/main/package/package_nuttyfi32_index.json
```

### Issue 2: JSON File Not Pushed
Make sure `package_nuttyfi32_index.json` is in GitHub repository.

### Issue 3: Arduino IDE Cache
Clear Arduino IDE cache:
- Windows: `%LOCALAPPDATA%\Arduino15\staging\packages`
- Delete contents and restart Arduino IDE

### Issue 4: URL Format Wrong
Make sure URL in Preferences is:
```
https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
```

---

## ⚡ Quick Fix Script

Run this to automatically update JSON:

```cmd
cd "D:\esp32 bsp\esp bsp"
python update_json_simple.py
```

Then push to GitHub and restart Arduino IDE.

---

## ✅ Checklist

- [ ] SHA256 hash is real (not PLACEHOLDER)
- [ ] File size is real (not PLACEHOLDER)
- [ ] JSON file is valid (no syntax errors)
- [ ] JSON file is pushed to GitHub
- [ ] GitHub URL returns JSON (not 404)
- [ ] Arduino IDE is restarted
- [ ] Correct URL in Arduino Preferences

---

## 🎯 Most Important

**Arduino IDE will NOT show boards if JSON has placeholder values!**

You MUST update:
1. SHA256 hash → Real hash from zip file
2. File size → Real size from zip file

Then push to GitHub and restart Arduino IDE.

