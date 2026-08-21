# AriTyper - Quick Start Guide

## System Compatibility

**Supported Operating Systems:**
- Windows 8, Windows 10, Windows 11
- macOS 10.12 (Sierra) and later (including latest versions)

**Python Version:** 3.6 or higher (3.7+ recommended)

## First Time Setup

AriTyper is free — there is no license key, activation or password.

1. **Install Python** (3.8 or higher) from
   [python.org/downloads](https://www.python.org/downloads/).
   On Windows, tick **"Add python.exe to PATH"** in the installer.

2. **Get AriTyper and start it.** In Command Prompt:

   ```bat
   git clone https://github.com/ariho-code/AriTyper-App
   cd AriTyper-App
   run.bat
   ```

   In PowerShell, use `.\run.ps1` instead of `run.bat`.
   On Linux/macOS, use `./run.sh`.

   No Git? Download the ZIP from GitHub (**Code → Download ZIP**), extract it,
   and double-click **`run.bat`**.

That's all. The first run installs the dependencies automatically (one time
only), then AriTyper opens straight to the typing screen. Later runs start
immediately.

## Basic Usage

1. **Select Document**: Click "Select Document" and choose your PDF or Word file
2. **Preview Text**: Review the extracted text in the preview area
3. **Select Target Window**: 
   - Click "Refresh" to see available windows
   - Double-click your browser/application window from the list
4. **Set Typing Speed**: 
   - For extreme speed: 1-5ms
   - For fast typing: 10-20ms
   - For normal speed: 50-100ms
5. **Start Typing**: 
   - Click "🚀 START TYPING"
   - You have 5 seconds to click into the target text field
   - The application will automatically type the text

## Tips

- **Formatting**: Word documents preserve alignment (center, left, right). PDF formatting is limited.
- **Speed**: Lower values = faster typing. Start with 10ms and adjust as needed.
- **Safety**: Move mouse to top-left corner to abort typing if needed.
- **Window Focus**: The app only types in the selected window, so you can use other apps.

## Building Executable

**Windows (recommended: faster startup)**:
```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1 -Mode onedir
```

**Windows (single-file, slower startup)**:
```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1 -Mode onefile
```

**macOS**:
```bash
python build_executable.py --mode onedir
```

The executable will be in the `dist` folder.

## Troubleshooting

- **App does not open**: Make sure dependencies are installed (`pip install -r requirements.txt`)
- **Window not found**: Use "Refresh" to update the window list
- **Typing doesn't work**: Make sure you clicked into the target field within 5 seconds
- **macOS permissions**: Grant accessibility permissions in System Preferences

