# AriTyper - Quick Start Guide

## System Compatibility

**Supported Operating Systems:**
- Windows 8, Windows 10, Windows 11
- macOS 10.12 (Sierra) and later (including latest versions)

**Python Version:** 3.6 or higher (3.7+ recommended)

## First Time Setup

1. **Install Python** (3.6 or higher) if you haven't already

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python arityper.py
   ```

4. **Enter License Key**: `#Code4good@1425`
   
   ⚠️ **Important**: The password is case-sensitive and must be entered exactly as shown (including the # symbol at the start).
   
   If you're having trouble, you can test the password by running:
   ```bash
   python test_auth.py
   ```

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

- **Authentication fails**: Check that you're entering the exact license key
- **Window not found**: Use "Refresh" to update the window list
- **Typing doesn't work**: Make sure you clicked into the target field within 5 seconds
- **macOS permissions**: Grant accessibility permissions in System Preferences

