# Quick Test Instructions

## To Run AriTyper:

1. **Make sure dependencies are installed:**
   ```
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```
   python arityper.py
   ```

3. **When the authentication dialog appears:**
   - Enter the password: `#Code4good@1425`
   - Press Enter or click "Authenticate"
   - The main application window should appear

## If It Doesn't Work:

1. **Check for errors in the console/terminal**
   - Look for any error messages
   - Share them if you need help

2. **Test password separately:**
   ```
   python test_auth.py
   ```
   Enter: `#Code4good@1425`

3. **Verify Python version:**
   ```
   python --version
   ```
   Should be 3.6 or higher

4. **Check dependencies:**
   ```
   pip list | findstr "pdfplumber python-docx PyGetWindow PyAutoGUI"
   ```

## Common Issues:

- **Dialog doesn't appear**: Check if Tkinter is working: `python -m tkinter`
- **Password not accepted**: Make sure you're typing exactly `#Code4good@1425` (including the #)
- **Import errors**: Run `pip install -r requirements.txt` again

