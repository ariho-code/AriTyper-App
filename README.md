# AriTyper - Professional Document Typing Software

A premium Python application that extracts text from PDF or Word documents and types it rapidly into browser windows that don't accept pasting, with full formatting preservation.

## 🔐 Authentication

This software requires a license key to use. Contact the vendor to obtain your license key.

## ✨ Features

- 📄 **Multi-format Support**: Extract text from PDF and Word (.docx, .doc) documents
- 🎨 **Format Preservation**: Maintains text alignment (center, left, right) from source documents
- ⚡ **Ultra-Fast Typing**: Configurable typing speed (1ms - extreme speed to 100ms+ normal speed)
- 🖥️ **Cross-Platform**: Works on Windows 8, 10, 11 and macOS 10.12+ (including older and latest versions)
- 🎯 **Window Targeting**: Select specific browser/application windows to type into
- 🔒 **Password Protected**: Secure authentication system
- 🎭 **Modern UI**: Beautiful dark-themed interface with smooth animations
- ✅ **Smart Focus Management**: Only types in the selected window, allows you to continue using your computer
- 🔧 **Backward Compatible**: Gracefully handles older OS versions with fallback mechanisms

## 📦 Installation

1. Ensure you have Python 3.6 or higher installed (3.7+ recommended).
   
   **System Requirements:**
   - **Windows**: Windows 8, Windows 10, or Windows 11
   - **macOS**: macOS 10.12 (Sierra) or later (including latest versions)

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Note: On macOS, you may need to install additional dependencies. The script will handle platform-specific requirements automatically.

## 🚀 Usage

1. Run the application:
```bash
python arityper.py
```

2. Enter your license key when prompted.

3. Click **"Select Document"** to choose your PDF or Word file.

4. The extracted text will appear in the preview area with formatting preserved.

5. Click **"Refresh"** next to Target Window, then double-click to select your browser window.

6. Adjust typing speed (in milliseconds):
   - **1-5ms**: Extreme speed (for very fast typing)
   - **10-20ms**: Fast speed
   - **50ms+**: Normal/human-like speed

7. Click **"🚀 START TYPING"**.

8. **Important**: You have 5 seconds to click into the text field in your target application where you want the text to be typed.

9. The application will automatically type the extracted text with formatting preserved.

## ⚙️ Typing Speed Guide

- **1ms**: Extremely fast (1000 characters/second) - Use with caution
- **5ms**: Very fast (200 characters/second)
- **10ms**: Fast (100 characters/second)
- **20ms**: Moderate-fast (50 characters/second)
- **50ms**: Normal typing speed (20 characters/second)
- **100ms+**: Slow, human-like typing

## 🔧 Creating an Executable

This project includes build scripts that create a **small build** (and avoid accidentally bundling huge packages from your global Python environment).

### Windows (recommended: faster startup)

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1 -Mode onedir
```

### Windows (single-file, slower startup)

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1 -Mode onefile
```

### Cross-platform (Python build helper)

```bash
python build_executable.py --mode onedir
```

Build output is in the `dist` folder.

## ⚠️ Important Notes

- **Mouse Safety**: Move your mouse to the top-left corner of the screen to abort typing (PyAutoGUI failsafe)
- **Window Focus**: Make sure to click into the target text field within the 5-second countdown
- **Formatting**: Perfect centering depends on the target field width. The application preserves alignment from source documents
- **Cross-Platform**: Works on both Windows and macOS with automatic platform detection
- **Window Selection**: The application will only type in the selected window, allowing you to continue using other applications

## 🐛 Troubleshooting

- **Authentication Failed**: Ensure you're entering the correct license key
- **Window Not Found**: Use "Refresh" to update the window list, then select your target window
- **Typing Not Working**: 
  - Ensure you've clicked into the target field within 5 seconds
  - Check that the target window is still active and focused
  - Verify typing speed is set appropriately
- **Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **macOS Permissions**: On macOS, you may need to grant accessibility permissions to Terminal/Python in System Preferences > Security & Privacy > Accessibility
- **Older OS Compatibility**: If animations don't work (e.g., Windows 8), the app will continue to function normally without them
- **Window Activation Issues**: On very old systems, window activation may use fallback methods

## 📝 License

Commercial Software - License key required.

## 🆘 Support

## 👤 Credits / Developer

**Developed by Timothy Ariho**

- **LinkedIn**: `https://www.linkedin.com/in/timothy-ariho-aab4ab216/`
- **X**: `https://x.com/arih0tim`
- **Phone**: `0743249384`
- **Email**: `timothy.arihoz@protonmail.com`

For technical support, license inquiries, or **custom software development**, please contact the developer.
