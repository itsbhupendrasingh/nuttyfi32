# 🔐 Personal Access Token Guide - nuttyfi32 Push

## ✅ Quick Steps to Get Token:

### Step 1: Generate Token
1. Go to: **https://github.com/settings/tokens**
2. Click: **"Generate new token"** → **"Generate new token (classic)"**
3. Fill details:
   - **Note:** `nuttyfi32-push` (या कोई भी name)
   - **Expiration:** 90 days (या no expiration)
   - **Select scopes:** ✅ **`repo`** (full control of private repositories)
4. Click: **"Generate token"**

### Step 2: Copy Token
- Token start होगा: `ghp_` से
- **IMMEDIATELY COPY** - यह दोबारा नहीं दिखेगा!
- Example: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Use Token
जब script run करें और credentials prompt हो:
- **Username:** `itsbhupendrasingh`
- **Password:** Token paste करें (GitHub password नहीं!)

## 🚀 Script Run करें:

```batch
python build_nuttyfi32_complete.py
```

जब push हो, तो:
```
Username for 'https://github.com': itsbhupendrasingh
Password for 'https://itsbhupendrasingh@github.com': [Token paste करें]
```

## ⚠️ Important:

- ✅ **Token = Password** (GitHub password नहीं!)
- ✅ Token को safe रखें (किसी को share न करें)
- ✅ अगर token expire हो, नया generate करें

## 🔄 Alternative: Manual Push

अगर script में issue हो, तो manually:

```bash
cd "D:\esp32 bsp\v1.0"
git add .
git commit -m "Update nuttyfi32 package v1.0.0"
git push -u origin Master
```

जब prompt हो:
- Username: `itsbhupendrasingh`
- Password: `[Your Personal Access Token]`

## 📝 Token Permissions:

Minimum required:
- ✅ **repo** - Full control of private repositories
  - This includes: push, pull, create releases, etc.

## 🆘 Token Lost?

अगर token खो गया:
1. Old token को revoke करें: https://github.com/settings/tokens
2. New token generate करें
3. Script फिर run करें

## ✅ Verification:

Token सही है या नहीं check करने के लिए:
```bash
git push -u origin Master
```

अगर push successful हो, तो token सही है! 🎉


