# Arduino IDE Preferences URL

## JSON File Location
The package index JSON file is located at:
```
nuttyfi32/package/package_nuttyfi32_index.json
```

## Option 1: GitHub Raw URL (Recommended)
Once the JSON file is pushed to GitHub, use this URL:

```
https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
```

**Format:** `https://raw.githubusercontent.com/username/repo/branch/path/to/file.json`

## Option 2: GitHub Pages (If enabled)
If you enable GitHub Pages, you can use:

```
https://itsbhupendrasingh.github.io/nuttyfi32/package/package_nuttyfi32_index.json
```

## Option 3: Host on GitHub Releases
Upload the JSON file as a release asset and use a direct link.

---

## How to Add to Arduino IDE

### Step 1: Open Arduino IDE Preferences
1. Open Arduino IDE
2. Go to **File** → **Preferences** (or **Arduino** → **Preferences** on Mac)
3. Scroll down to **Additional Boards Manager URLs**

### Step 2: Add the URL
1. Click the button next to "Additional Boards Manager URLs"
2. Add this URL (one per line):
   ```
   https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
   ```
3. Click **OK**

### Step 3: Install the Board Package
1. Go to **Tools** → **Board** → **Boards Manager**
2. Search for "nuttyfi32"
3. Click **Install** on the nuttyfi32 package

---

## Important Notes

⚠️ **The JSON file MUST be publicly accessible**
- Make sure the file is in the GitHub repository
- Make sure the repository is public (or you have access)
- The raw URL must return the JSON content (not HTML)

✅ **After pushing to GitHub:**
1. Verify the URL works by opening it in a browser
2. You should see the JSON content, not a GitHub page
3. Then add it to Arduino IDE preferences

---

## Verify URL Works
Test the URL in your browser:
```
https://raw.githubusercontent.com/itsbhupendrasingh/nuttyfi32/master/package/package_nuttyfi32_index.json
```

You should see the JSON content, not a 404 error.

