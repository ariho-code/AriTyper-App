# Quick Test Instructions

## To Run AriTyper:

**Windows (Command Prompt):**
```
run.bat
```

**Windows (PowerShell):**
```
.\run.ps1
```

**Linux / macOS:**
```
./run.sh
```

The launcher installs everything it needs on the first run, then opens AriTyper
straight to the typing screen. There is no password, license key or activation
step — the app is free.

To run it manually instead:
```
pip install -r requirements.txt
python arityper_activated.py
```

## If It Doesn't Work:

1. **Check for errors in the console/terminal**
   - Look for any error messages
   - Share them if you need help

2. **Verify Python version:**
   ```
   python --version
   ```
   Should be 3.8 or higher

3. **Check dependencies:**
   ```
   pip list | findstr "pdfplumber python-docx PyPDF2 PyGetWindow PyAutoGUI"
   ```

4. **Confirm the app is unlocked and openable:**
   ```
   python test_open_access.py
   ```

## Common Issues:

- **`'python' is not recognized`**: Python isn't on your PATH. Reinstall it from
  python.org and tick "Add python.exe to PATH", then open a new terminal.
- **PowerShell refuses to run the script**: use
  `powershell -ExecutionPolicy Bypass -File .\run.ps1`
- **Window doesn't appear**: check Tkinter is working: `python -m tkinter`
- **Import errors**: delete the `.venv` folder and run the launcher again
- **Typing does nothing on Linux/macOS**: window targeting needs `PyGetWindow`,
  which is Windows-only. The UI and document extraction still work.
