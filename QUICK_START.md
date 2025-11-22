# Quick Start Guide - nuttyfi32 BSP

## For End Users (Installing nuttyfi32 BSP)

### Step 1: Add Board Manager URL
1. Open **Arduino IDE**
2. Go to **File** → **Preferences**
3. In **Additional Boards Manager URLs**, add:
   ```
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
   ```
4. Click **OK**

### Step 2: Install Board Package
1. Go to **Tools** → **Board** → **Boards Manager**
2. Search for **"nuttyfi32"**
3. Click **Install** on the nuttyfi32 package (version 1.0.0)

### Step 3: Select Board
1. Go to **Tools** → **Board**
2. Select **nuttyfi32 Dev Board** (or any other nuttyfi32 board)

### Step 4: Start Coding!
You're ready to use nuttyfi32 boards in Arduino IDE!

---

## Available Boards
- nuttyfi32 Dev Board
- nuttyfi32-S2 Dev Board
- nuttyfi32-S3 Dev Board
- nuttyfi32-C3 Dev Board
- nuttyfi32-C6 Dev Board
- nuttyfi32-H2 Dev Board
- nuttyfi32-P4 Dev Board

---

## Troubleshooting

### JSON URL Not Working?
1. Make sure the JSON file is pushed to GitHub
2. Check the URL in browser: https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
3. You should see JSON content, not a 404 error

### Board Not Found?
1. Make sure you added the correct URL in Preferences
2. Restart Arduino IDE
3. Check Boards Manager for "nuttyfi32" package

### Download Fails?
1. Check GitHub release exists: https://github.com/itsbhupendrasingh/nuttyfi32/releases/tag/1.0.0
2. Verify zip file is uploaded to release
3. Check SHA256 hash matches in JSON file

