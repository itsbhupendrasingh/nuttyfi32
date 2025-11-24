# 🚀 Quick Start Guide - nuttyfi32 Package

## ✅ एक ही Script से सब कुछ!

### Step 1: Script Run करें
```batch
python build_nuttyfi32_complete.py
```

या बस double-click करें:
```batch
build_and_push.bat
```

## 📋 Script क्या करता है:

1. ✅ **पुरानी ZIP files delete** करता है (nuttyfi32-*.zip)
2. ✅ **ESP32 BSP extract** करता है
3. ✅ **Package name change** करता है (esp32 → nuttyfi32)
4. ✅ **boards.txt में nuttyfi32 board add** करता है
5. ✅ **नई ZIP file बनाता है** (nuttyfi32-1.0.0.zip)
6. ✅ **Checksum calculate** करता है
7. ✅ **JSON file update** करता है
8. ✅ **Temp files clean** करता है

## 📁 ZIP File Structure:

```
nuttyfi32-1.0.0.zip
├── boards.txt          (nuttyfi32 board added)
├── platform.txt        (name updated)
├── package.json
├── cores/
├── libraries/
├── tools/
└── ... (all ESP32 BSP files)
```

**Important:** ZIP के अंदर folder name `esp32` नहीं होगा - सभी files root level पर होंगी (Arduino IDE की requirement)

## 🎯 Result:

- ✅ **ZIP File:** `nuttyfi32-1.0.0.zip` (link में जो name है वही)
- ✅ **JSON Updated:** checksum और size automatically update
- ✅ **Old Files Deleted:** पुरानी ZIP files automatically remove
- ✅ **Only Latest ZIP:** folder में सिर्फ latest ZIP file रहेगी

## 📝 Next Steps:

1. **GitHub Release बनाएं:**
   - https://github.com/itsbhupendrasingh/nuttyfi32/releases/new
   - Tag: `1.0.0`
   - Upload: `nuttyfi32-1.0.0.zip`

2. **GitHub Push (Optional):**
   ```batch
   python push_to_github.py
   ```

## ⚙️ Configuration:

Script में version change करने के लिए:
```python
VERSION = "1.0.0"  # यहाँ version change करें
```

## ⚠️ Important Notes:

- ✅ **ZIP name:** `nuttyfi32-1.0.0.zip` (link के अनुसार)
- ✅ **Folder inside ZIP:** Root level (Arduino IDE compatible)
- ✅ **Old ZIPs:** Automatically deleted
- ✅ **Only one ZIP:** Latest ZIP file ही folder में रहेगी
- ✅ **Auto sync:** JSON और ZIP हमेशा sync रहेंगे

## 🔄 Changes के बाद:

जब भी changes करें:
1. Script फिर से run करें
2. पुरानी ZIP automatically delete होगी
3. नई ZIP बनेगी
4. JSON automatically update होगा

**बार-बार manual cleanup की जरूरत नहीं!** 🎉

