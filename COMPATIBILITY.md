# AriTyper - Compatibility Information

## Supported Operating Systems

### Windows
- ✅ **Windows 8** - Fully supported (with fallback features for older APIs)
- ✅ **Windows 8.1** - Fully supported
- ✅ **Windows 10** - Fully supported (all versions)
- ✅ **Windows 11** - Fully supported

**Notes for Windows:**
- Window transparency/alpha effects may not work on Windows 8 (app will function normally without them)
- All core features work on Windows 8+
- Window activation uses fallback methods on older versions if needed

### macOS
- ✅ **macOS 10.12 (Sierra)** - Fully supported
- ✅ **macOS 10.13 (High Sierra)** - Fully supported
- ✅ **macOS 10.14 (Mojave)** - Fully supported
- ✅ **macOS 10.15 (Catalina)** - Fully supported
- ✅ **macOS 11 (Big Sur)** - Fully supported
- ✅ **macOS 12 (Monterey)** - Fully supported
- ✅ **macOS 13 (Ventura)** - Fully supported
- ✅ **macOS 14 (Sonoma)** - Fully supported
- ✅ **macOS 15+ (Latest)** - Fully supported

**Notes for macOS:**
- Requires accessibility permissions (System Preferences > Security & Privacy > Accessibility)
- All features work across macOS versions
- Window management uses native macOS APIs

## Python Version Requirements

- **Minimum**: Python 3.6
- **Recommended**: Python 3.7 or higher
- **Tested on**: Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12

## Dependency Compatibility

All dependencies are configured with version ranges that support older OS versions:

- **pdfplumber**: >=0.7.0 (supports older systems)
- **python-docx**: >=0.8.11 (widely compatible)
- **PyGetWindow**: >=0.0.9 (cross-platform)
- **PyAutoGUI**: >=0.9.50 (Windows 8+ and macOS 10.12+)
- **pywin32**: >=300 (Windows 8, 10, 11)
- **pyobjc-framework-Quartz**: >=6.0 (macOS 10.12+)

## Backward Compatibility Features

The application includes several backward compatibility features:

1. **Graceful Degradation**: 
   - Alpha transparency effects are optional (app works without them on Windows 8)
   - Window activation uses multiple fallback methods
   - Animation effects are skipped if not supported

2. **Error Handling**:
   - All OS-specific features are wrapped in try-catch blocks
   - Fallback methods are used when primary methods fail
   - Application continues to function even if some features aren't available

3. **Version Detection**:
   - Automatic OS version detection
   - Compatible API selection based on detected OS
   - User warnings for unsupported configurations

## Known Limitations

### Windows 8
- Window transparency (alpha) effects may not work
- Some visual animations may be simplified
- All core functionality remains intact

### Older macOS (10.12-10.13)
- Some modern UI features may be simplified
- Window management uses slightly different methods
- All functionality works correctly

## Testing Recommendations

Before deploying on older systems:

1. **Windows 8**: Test window selection and typing functionality
2. **macOS 10.12**: Verify accessibility permissions are granted
3. **Python 3.6**: Ensure all dependencies install correctly

## Support

If you encounter compatibility issues:

1. Check that you're using a supported OS version
2. Verify Python version is 3.6 or higher
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Check system permissions (especially on macOS)

For specific compatibility questions, refer to the main README.md or contact support.

