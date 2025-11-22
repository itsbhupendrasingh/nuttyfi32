# Fix: Compiler Toolchain Error

## Error
```
exec: "/bin/xtensa-esp32-elf-g++": executable file not found in %PATH%
```

## Problem
The compiler prefix was incorrectly constructed as `{build.tarch}-{build.target}-elf-` which creates `xtensa-esp32-elf-`, but the actual compiler tool is named `xtensa-esp-elf-gcc` (without "32").

## Solution
Changed `platform.txt` line 28 from:
```
compiler.prefix={build.tarch}-{build.target}-elf-
```

To:
```
compiler.prefix={build.tarch}-esp-elf-
```

This matches the actual tool name: `xtensa-esp-elf-gcc` → prefix: `xtensa-esp-elf-`

## Next Steps
1. ✅ Fixed in platform.txt
2. Push to GitHub:
   ```cmd
   cd "D:\esp32 bsp\esp bsp\nuttyfi32"
   git add platform.txt
   git commit -m "Fix: Correct compiler prefix to match toolchain"
   git push origin master
   ```
3. In Arduino IDE:
   - Go to **Tools** → **Board** → **Boards Manager**
   - Find **nuttyfi32** package
   - Click **Update** or **Reinstall**
4. Try compiling again - should work now! ✅

## Verification
After update, the compiler should find:
- `xtensa-esp-elf-g++` (correct)
- Not `xtensa-esp32-elf-g++` (wrong)

