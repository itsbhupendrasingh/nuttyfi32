# Troubleshooting - Boards Not Showing in Arduino IDE

## Common Issues & Solutions

### Issue 1: Placeholder Values in JSON ❌
**Problem:** JSON file has `PLACEHOLDER_SHA256_HASH_HERE` and `PLACEHOLDER_SIZE_HERE`

**Solution:** Arduino IDE requires valid SHA256 hash and size. These MUST be real values.

### Issue 2: JSON File Not Accessible
**Problem:** The raw GitHub URL returns 404 or HTML instead of JSON

**Check:**
1. Open this URL in browser:
   ```
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
   ```
2. You should see JSON content, not a 404 error
3. If 404, the file is not pushed to GitHub or branch name is wrong

### Issue 3: Wrong Branch Name
**Problem:** Branch might be "main" instead of "master"

**Check:**
- If your default branch is "main", use:
  ```
  https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/main/package/package_nuttyfi32_index.json
  ```

### Issue 4: Invalid JSON Format
**Problem:** JSON has syntax errors

**Check:**
- Validate JSON at: https://jsonlint.com/
- Make sure all brackets and quotes are correct

### Issue 5: Arduino IDE Cache
**Problem:** Arduino IDE cached old/empty JSON

**Solution:**
1. Close Arduino IDE completely
2. Delete cache (optional):
   - Windows: `%LOCALAPPDATA%\Arduino15\staging\packages`
   - Mac: `~/Library/Arduino15/staging/packages`
   - Linux: `~/.arduino15/staging/packages`
3. Restart Arduino IDE
4. Try again

### Issue 6: Checksum Format Wrong
**Problem:** SHA256 hash format is incorrect

**Correct format:**
```json
"checksum": "SHA-256:abc123def456..."
```

**Wrong format:**
```json
"checksum": "PLACEHOLDER_SHA256_HASH_HERE"
"checksum": "abc123def456..."  // Missing SHA-256: prefix
```

---

## Step-by-Step Fix

### Step 1: Get Actual SHA256 and Size
```powershell
cd "D:\esp32 bsp\esp bsp"
$file = Get-Item "nuttyfi32-1.0.0.zip"
$size = $file.Length
$hash = (Get-FileHash -Path "nuttyfi32-1.0.0.zip" -Algorithm SHA256).Hash
Write-Host "Size: $size"
Write-Host "SHA256: $hash"
```

### Step 2: Update JSON File
Replace in `package_nuttyfi32_index.json`:
- Line 19: `"checksum": "SHA-256:PLACEHOLDER_SHA256_HASH_HERE"` → `"checksum": "SHA-256:YOUR_ACTUAL_HASH"`
- Line 20: `"size": "PLACEHOLDER_SIZE_HERE"` → `"size": "YOUR_ACTUAL_SIZE"`

### Step 3: Verify JSON File
1. Push updated JSON to GitHub
2. Test URL in browser
3. Make sure it returns valid JSON

### Step 4: Restart Arduino IDE
1. Close Arduino IDE
2. Reopen Arduino IDE
3. Go to Boards Manager
4. Search for "nuttyfi32"

---

## Quick Test

1. **Test JSON URL:**
   ```
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
   ```

2. **Check JSON is valid:**
   - Open URL in browser
   - Should see JSON, not HTML
   - Copy JSON and paste at https://jsonlint.com/

3. **Check Arduino IDE:**
   - File → Preferences
   - Verify URL is added correctly
   - Restart Arduino IDE
   - Try Boards Manager again

---

## Most Likely Issue

⚠️ **Placeholder values in JSON** - Arduino IDE rejects JSON files with invalid checksum/size.

**Fix:** Update JSON with real SHA256 hash and file size before pushing to GitHub.

