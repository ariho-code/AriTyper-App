#!/usr/bin/env python3
"""
AriTyper Working Version - Simple and Functional
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import threading
import time
import json
import os
import sys
import socket
import hashlib
import platform
from datetime import datetime

# Try to import document processing libraries
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Try to import Windows libraries
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class AriTyperWorking:
    def __init__(self, root):
        self.root = root
        self.server_url = "http://localhost:5000"
        self.device_id = self.generate_device_id()
        self.target_window = None
        self.is_typing = False
        self.selected_file = None
        
        self.setup_window()
        self.create_ui()
        self.check_license()
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("AriTyper - Working Version")
        self.root.geometry("900x600")
        self.root.configure(bg="#1a1a1a")
        
    def create_ui(self):
        """Create user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Label(main_frame, text="🚀 AriTyper - Professional Typing Tool", 
                          font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#00ff88")
        header.pack(pady=(0, 20))
        
        # Device info
        device_label = tk.Label(main_frame, text=f"Device: {self.device_id}", 
                               font=("Courier", 10), bg="#1a1a1a", fg="#888888")
        device_label.pack(pady=(0, 20))
        
        # License status
        self.license_label = tk.Label(main_frame, text="🔒 Checking license...", 
                                     font=("Arial", 12), bg="#1a1a1a", fg="#ffaa00")
        self.license_label.pack(pady=(0, 20))
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg="#1a1a1a")
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Text input
        left_frame = tk.Frame(content_frame, bg="#2a2a2a", relief="ridge", bd=2)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="📝 Text Content", font=("Arial", 14, "bold"),
                bg="#2a2a2a", fg="#00aaff").pack(pady=10)
        
        self.text_area = scrolledtext.ScrolledText(
            left_frame, font=("Consolas", 11), bg="#1a1a1a", fg="#ffffff",
            wrap=tk.WORD, height=15, relief="flat", bd=0, padx=10, pady=10
        )
        self.text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Action buttons
        button_frame = tk.Frame(left_frame, bg="#2a2a2a")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="📋 Paste", font=("Arial", 10),
                 bg="#ff6600", fg="white", command=self.paste_text).pack(side="left", padx=5)
        tk.Button(button_frame, text="📂 Load File", font=("Arial", 10),
                 bg="#0066cc", fg="white", command=self.load_file).pack(side="left", padx=5)
        tk.Button(button_frame, text="🗑️ Clear", font=("Arial", 10),
                 bg="#cc0000", fg="white", command=self.clear_text).pack(side="right", padx=5)
        
        # Right panel - Controls
        right_frame = tk.Frame(content_frame, bg="#2a2a2a", relief="ridge", bd=2)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        
        tk.Label(right_frame, text="⚙️ Controls", font=("Arial", 14, "bold"),
                bg="#2a2a2a", fg="#00aaff").pack(pady=10)
        
        # Window selection
        tk.Label(right_frame, text="Target Window:", font=("Arial", 10),
                bg="#2a2a2a", fg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
        
        tk.Button(right_frame, text="🪟 Select Window", font=("Arial", 10),
                 bg="#0066cc", fg="white", command=self.select_window).pack(fill="x", padx=10, pady=(0, 10))
        
        self.window_info = tk.Label(right_frame, text="No window selected", 
                                   font=("Arial", 9), bg="#2a2a2a", fg="#888888")
        self.window_info.pack(padx=10, pady=(0, 15))
        
        # Speed control
        tk.Label(right_frame, text="Typing Speed:", font=("Arial", 10),
                bg="#2a2a2a", fg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.speed_var = tk.DoubleVar(value=50)
        speed_scale = ttk.Scale(right_frame, from_=1, to=100, variable=self.speed_var,
                               orient="horizontal", length=150)
        speed_scale.pack(padx=10, pady=(0, 5))
        
        self.speed_label = tk.Label(right_frame, text="50%", font=("Arial", 9),
                                   bg="#2a2a2a", fg="#00ff88")
        self.speed_label.pack(padx=10, pady=(0, 15))
        
        # Progress
        tk.Label(right_frame, text="Progress:", font=("Arial", 10),
                bg="#2a2a2a", fg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(right_frame, variable=self.progress_var,
                                      maximum=100, length=150)
        progress_bar.pack(padx=10, pady=(0, 5))
        
        self.progress_label = tk.Label(right_frame, text="0%", font=("Arial", 9),
                                      bg="#2a2a2a", fg="#00ff88")
        self.progress_label.pack(padx=10, pady=(0, 15))
        
        # Control buttons
        self.start_btn = tk.Button(right_frame, text="▶️ Start Typing", font=("Arial", 10),
                                   bg="#00cc66", fg="white", command=self.start_typing)
        self.start_btn.pack(fill="x", padx=10, pady=(0, 5))
        
        self.stop_btn = tk.Button(right_frame, text="⏹️ Stop", font=("Arial", 10),
                                  bg="#cc0000", fg="white", state="disabled", command=self.stop_typing)
        self.stop_btn.pack(fill="x", padx=10, pady=(0, 15))
        
        # Status
        self.status_label = tk.Label(main_frame, text="Ready to type", 
                                    font=("Arial", 10), bg="#1a1a1a", fg="#888888")
        self.status_label.pack(pady=(10, 0))
        
    def generate_device_id(self):
        """Generate unique device ID"""
        parts = []
        try:
            parts.append(socket.gethostname())
        except:
            pass
        parts.append(platform.system())
        parts.append(platform.machine())
        try:
            import uuid
            parts.append(str(uuid.getnode()))
        except:
            pass
        h = hashlib.sha256("|".join(parts).encode()).hexdigest()
        return f"ARI-{h[:16].upper()}"
        
    def get_device_info(self):
        """Get device information for synchronization"""
        try:
            import psutil
            return {
                "os": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": socket.gethostname(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "python_version": platform.python_version()
            }
        except:
            return {
                "os": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "hostname": socket.gethostname()
            }
        
    def check_license(self):
        """Check license with enhanced webapp synchronization"""
        def check_thread():
            try:
                # Check local license file
                if os.path.exists("license.json"):
                    with open("license.json") as f:
                        license_data = json.load(f)
                        
                    # Enhanced validation with server
                    response = requests.post(
                        f"{self.server_url}/api/device/validate_license",
                        json={
                            "device_id": self.device_id, 
                            "license_key": license_data.get("license_key"),
                            "app_version": "2.0.0",
                            "sync_data": {
                                "last_sync": license_data.get("last_sync"),
                                "usage_count": license_data.get("usage_count", 0),
                                "device_info": self.get_device_info()
                            }
                        },
                        timeout=15
                    )
                    
                    if response.status_code == 200 and response.json().get("valid"):
                        self.root.after(0, self.unlock_app)
                        return
                        
            except:
                pass
                
            # Show activation required
            self.root.after(0, lambda: self.license_label.config(
                text="🔒 License Required - Contact Admin", fg="#cc0000"))
            self.root.after(0, lambda: self.status_label.config(
                text="Please contact admin to activate your license"))
                
        threading.Thread(target=check_thread, daemon=True).start()
        
    def unlock_app(self):
        """Unlock the app"""
        self.license_label.config(text="✅ Licensed - Ready to Use", fg="#00ff88")
        self.status_label.config(text="License verified - Ready to type")
        
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", clipboard_text)
            self.status_label.config(text=f"Pasted {len(clipboard_text)} characters", fg="#00ff88")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {str(e)}")
            
    def clear_text(self):
        """Clear text area"""
        self.text_area.delete("1.0", tk.END)
        self.status_label.config(text="Text cleared", fg="#888888")
        
    def load_file(self):
        """Load text from file with exact formatting preservation"""
        file_types = [
            ("All Files", "*.*"),
            ("Text Files", "*.txt"),
            ("Word Documents", "*.docx"),
            ("PDF Files", "*.pdf")
        ]
        
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            try:
                content = ""
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif file_ext == '.docx' and DOCX_AVAILABLE:
                    doc = Document(file_path)
                    # Preserve exact paragraph structure and alignment
                    content = ""
                    for para in doc.paragraphs:
                        # Check alignment and add appropriate formatting
                        alignment = self._get_paragraph_alignment(para)
                        if para.text.strip():
                            # Add alignment markers for typing
                            formatted_line = self._format_line_with_alignment(para.text, alignment)
                            content += formatted_line + "\n"
                        else:
                            content += "\n"  # Preserve empty lines for spacing
                elif file_ext == '.pdf' and PDF_AVAILABLE:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page_num, page in enumerate(pdf_reader.pages):
                            page_text = page.extract_text()
                            # Analyze and preserve text structure and alignment
                            lines = page_text.split('\n')
                            for line in lines:
                                if line.strip():
                                    # Detect alignment based on spacing
                                    alignment = self._detect_line_alignment(line)
                                    formatted_line = self._format_line_with_alignment(line.strip(), alignment)
                                    content += formatted_line + "\n"
                                else:
                                    content += "\n"  # Preserve empty lines
                            if page_num < len(pdf_reader.pages) - 1:
                                content += "\n"  # Add page break
                else:
                    messagebox.showinfo("Info", "File format not supported or libraries missing")
                    return
                    
                # Store the original content for typing with formatting
                self.original_content = content
                self.document_formatting = self._analyze_document_formatting(content)
                    
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.selected_file = file_path
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}", fg="#00ff88")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def _get_paragraph_alignment(self, paragraph):
        """Detect paragraph alignment from DOCX"""
        try:
            # Check paragraph alignment property
            if hasattr(paragraph, 'paragraph_format'):
                alignment = paragraph.paragraph_format.alignment
                if alignment == 1:  # WD_ALIGN_PARAGRAPH.CENTER
                    return 'center'
                elif alignment == 2:  # WD_ALIGN_PARAGRAPH.RIGHT
                    return 'right'
                elif alignment == 3:  # WD_ALIGN_PARAGRAPH.JUSTIFY
                    return 'justify'
            return 'left'
        except:
            return 'left'
            
    def _detect_line_alignment(self, line):
        """Enhanced alignment detection for headings and titles"""
        if not line.strip():
            return 'left'
            
        # Count leading and trailing spaces
        leading_spaces = len(line) - len(line.lstrip())
        trailing_spaces = len(line) - len(line.rstrip())
        total_length = len(line.strip())
        stripped_line = line.strip()
        
        # Enhanced detection for headings and titles
        # Check if it looks like a heading (shorter, centered, or has specific patterns)
        is_potential_heading = (
            total_length < 60 and  # Short text
            (leading_spaces > 3 or trailing_spaces > 3)  # Has spacing
        )
        
        # Check for title patterns (all caps, title case, etc.)
        is_title_like = (
            stripped_line == stripped_line.upper() or  # ALL CAPS
            stripped_line.istitle() or  # Title Case
            any(word.isupper() for word in stripped_line.split() if len(word) > 3)  # Some capitalized words
        )
        
        # Enhanced center detection
        if (leading_spaces > 3 and trailing_spaces > 3) or (is_potential_heading and is_title_like):
            return 'center'
        elif trailing_spaces > 15:
            return 'right'
        elif leading_spaces > 15:
            return 'left'
        else:
            return 'left'
            
    def _format_line_with_alignment(self, text, alignment):
        """Format line with alignment markers for typing"""
        if alignment == 'center':
            # Add center alignment marker
            return f"[CENTER]{text}"
        elif alignment == 'right':
            # Add right alignment marker
            return f"[RIGHT]{text}"
        elif alignment == 'justify':
            # Add justify alignment marker
            return f"[JUSTIFY]{text}"
        else:
            # Left alignment (default)
            return text
            
    def _analyze_document_formatting(self, content):
        """Analyze document for formatting patterns"""
        formatting_info = {
            'lines': [],
            'alignment_map': {},
            'spacing_map': {}
        }
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check for alignment markers
            alignment = 'left'
            if line.startswith('[CENTER]'):
                alignment = 'center'
                text = line[8:]  # Remove marker
            elif line.startswith('[RIGHT]'):
                alignment = 'right'
                text = line[7:]  # Remove marker
            elif line.startswith('[JUSTIFY]'):
                alignment = 'justify'
                text = line[9:]  # Remove marker
            else:
                text = line
                
            # Calculate spacing needs
            leading_spaces = len(text) - len(text.lstrip())
            
            formatting_info['lines'].append({
                'text': text,
                'alignment': alignment,
                'leading_spaces': leading_spaces,
                'original_line': line
            })
            
        return formatting_info
                
    def _preserve_document_structure(self, content):
        """Preserve document structure and formatting"""
        # Remove excessive blank lines but preserve paragraph structure
        lines = content.split('\n')
        cleaned_lines = []
        prev_blank = False
        
        for line in lines:
            if line.strip():
                cleaned_lines.append(line.rstrip())
                prev_blank = False
            else:
                # Only add blank line if previous line wasn't blank
                if not prev_blank:
                    cleaned_lines.append("")
                prev_blank = True
                
        return '\n'.join(cleaned_lines)
                
    def select_window(self):
        """Select target window for typing"""
        if not WIN32_AVAILABLE:
            messagebox.showinfo("Info", "Window selection requires Windows with pywin32")
            return
            
        try:
            def enum_windows_callback(hwnd, windows):
                try:
                    # Get window title and check if it's visible
                    title = win32gui.GetWindowText(hwnd)
                    if win32gui.IsWindowVisible(hwnd) and title.strip():
                        # Get window class name for better identification
                        class_name = win32gui.GetClassName(hwnd)
                        # Get window rect for additional info
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                        
                        # Only include windows that are reasonably sized (not system windows)
                        if width > 100 and height > 50:
                            windows.append((hwnd, title, class_name, width, height))
                except:
                    pass
                return True
                
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Sort windows by title for better organization
            windows.sort(key=lambda x: x[1].lower())
            
            if not windows:
                messagebox.showinfo("Info", "No accessible windows found")
                return
                
            # Create selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Select Target Window")
            dialog.geometry("600x400")
            dialog.configure(bg="#1a1a1a")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            tk.Label(dialog, text="Select window to type into:", font=("Arial", 12, "bold"),
                    bg="#1a1a1a", fg="white").pack(pady=10)
            
            # Instructions
            tk.Label(dialog, text="Choose the application window where you want to type", 
                    font=("Arial", 9), bg="#1a1a1a", fg="#888888").pack(pady=(0, 10))
            
            # Create frame for listbox with scrollbar
            list_frame = tk.Frame(dialog, bg="#2a2a2a", relief="ridge", bd=2)
            list_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")
            
            # Listbox with better formatting
            listbox = tk.Listbox(list_frame, font=("Consolas", 9), bg="#1a1a1a", fg="white",
                                selectmode="single", yscrollcommand=scrollbar.set,
                                relief="flat", bd=0, highlightthickness=0)
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Populate listbox with formatted window info
            for hwnd, title, class_name, width, height in windows:
                # Format: [Title] (Class: name) - WxH
                display_text = f"{title[:40]}... [{class_name[:15]}] {width}x{height}"
                listbox.insert(tk.END, display_text)
            
            # Status label
            status_label = tk.Label(dialog, text=f"Found {len(windows)} windows", 
                                   font=("Arial", 9), bg="#1a1a1a", fg="#00ff88")
            status_label.pack(pady=(0, 10))
                
            def select():
                selection = listbox.curselection()
                if selection:
                    hwnd, title, class_name, width, height = windows[selection[0]]
                    self.target_window = hwnd
                    
                    # Update window info with better formatting
                    info_text = f"{title[:30]}... ({width}x{height})"
                    self.window_info.config(text=f"Target: {info_text}", fg="#00ff88")
                    
                    # Show success message with window details
                    messagebox.showinfo("Success", f"Selected: {title}\nClass: {class_name}\nSize: {width}x{height}")
                    
                    dialog.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select a window first")
                    
            def refresh():
                """Refresh window list"""
                dialog.destroy()
                self.select_window()
            
            # Button frame
            button_frame = tk.Frame(dialog, bg="#1a1a1a")
            button_frame.pack(pady=10)
            
            tk.Button(button_frame, text="🔄 Refresh", font=("Arial", 9),
                     bg="#ff6600", fg="white", command=refresh).pack(side="left", padx=5)
            
            tk.Button(button_frame, text="✓ Select", font=("Arial", 10, "bold"),
                     bg="#00cc66", fg="white", command=select).pack(side="left", padx=5)
            
            tk.Button(button_frame, text="✕ Cancel", font=("Arial", 9),
                     bg="#cc0000", fg="white", command=dialog.destroy).pack(side="left", padx=5)
            
            # Double-click to select
            listbox.bind("<Double-Button-1>", lambda e: select())
            
            # Focus on first item
            if windows:
                listbox.selection_set(0)
                listbox.focus_set()
                     
        except Exception as e:
            messagebox.showerror("Error", f"Window selection failed: {str(e)}")
            
    def start_typing(self):
        """Start typing into selected window with exact formatting preservation"""
        text_content = self.text_area.get("1.0", tk.END)
        if not text_content.strip():
            messagebox.showwarning("No Text", "Please enter or paste text first")
            return
            
        if not self.target_window:
            messagebox.showwarning("No Window", "Please select a target window first")
            return
            
        self.is_typing = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Typing in progress...", fg="#ffaa00")
        
        def type_thread():
            try:
                # Focus target window
                if WIN32_AVAILABLE:
                    try:
                        win32gui.ShowWindow(self.target_window, win32con.SW_RESTORE)
                        time.sleep(0.3)
                        win32gui.SetForegroundWindow(self.target_window)
                        time.sleep(0.3)
                    except:
                        pass
                
                speed = self.speed_var.get()
                delay = 0.05 * max(0.05, 1.05 - speed / 100)
                
                # Process content line by line to preserve formatting
                lines = text_content.split('\n')
                total_lines = len(lines)
                
                for line_num, line in enumerate(lines):
                    if not self.is_typing:
                        break
                    
                    # Handle alignment markers and spacing
                    processed_line = self._process_line_for_typing(line)
                    
                    # Type the processed line character by character
                    for char in processed_line:
                        if not self.is_typing:
                            break
                            
                        try:
                            if WIN32_AVAILABLE:
                                # Type character with proper formatting
                                self._type_character_with_formatting(char)
                            else:
                                # Fallback for non-Windows
                                pass
                                
                        except:
                            # Continue on error
                            pass
                            
                        # Apply delay between characters
                        time.sleep(delay)
                    
                    # Add line break except for last line
                    if line_num < total_lines - 1:
                        try:
                            if WIN32_AVAILABLE:
                                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                                time.sleep(0.01)
                                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                        except:
                            pass
                        time.sleep(delay * 2)  # Extra delay for line breaks
                    
                    # Update progress based on lines
                    progress = int((line_num + 1) / total_lines * 100)
                    self.root.after(0, lambda p=progress: self.update_progress(p))
                    
                if self.is_typing:
                    self.root.after(0, self.typing_complete)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Typing Error", str(e)))
                self.root.after(0, self.stop_typing)
                
        threading.Thread(target=type_thread, daemon=True).start()
        
    def _process_line_for_typing(self, line):
        """Process line to handle alignment and spacing"""
        # Check for alignment markers
        if line.startswith('[CENTER]'):
            # For center alignment, calculate approximate centering
            text = line[8:]  # Remove marker
            # Add leading spaces to approximate centering
            centered_text = self._approximate_center_text(text)
            return centered_text
        elif line.startswith('[RIGHT]'):
            # For right alignment, add leading spaces
            text = line[7:]  # Remove marker
            right_aligned_text = self._approximate_right_align(text)
            return right_aligned_text
        elif line.startswith('[JUSTIFY]'):
            # For justified text, add spaces between words
            text = line[9:]  # Remove marker
            justified_text = self._approximate_justify(text)
            return justified_text
        else:
            # Left alignment (default)
            return line
            
    def _approximate_center_text(self, text):
        """Enhanced center alignment with better spacing for headings"""
        if not text.strip():
            return text
            
        text = text.strip()
        text_length = len(text)
        
        # Dynamic width based on text length (better for headings)
        if text_length < 20:
            target_width = 80  # Short titles get more centering space
        elif text_length < 40:
            target_width = 90  # Medium titles
        else:
            target_width = 100  # Longer text
            
        # Calculate perfect centering
        if text_length >= target_width:
            return text
            
        leading_spaces = (target_width - text_length) // 2
        
        # Add extra space for visual appeal on headings
        if text_length < 30:  # Very short headings
            leading_spaces += 2
            
        return ' ' * leading_spaces + text
        
    def _approximate_right_align(self, text):
        """Approximate right alignment with spaces"""
        if not text.strip():
            return text
            
        # Estimate right position (assume 80 character width)
        target_width = 80
        text_length = len(text.strip())
        
        if text_length >= target_width:
            return text.strip()
            
        # Calculate leading spaces for right alignment
        leading_spaces = target_width - text_length
        return ' ' * leading_spaces + text.strip()
        
    def _approximate_justify(self, text):
        """Approximate justified text by adding spaces"""
        if not text.strip():
            return text
            
        words = text.strip().split()
        if len(words) <= 1:
            return text.strip()
            
        # Add extra spaces between words for justification
        target_width = 80
        total_word_chars = sum(len(word) for word in words)
        needed_spaces = target_width - total_word_chars
        spaces_between = needed_spaces // (len(words) - 1)
        
        justified_text = ''
        for i, word in enumerate(words):
            justified_text += word
            if i < len(words) - 1:
                justified_text += ' ' * (1 + spaces_between)
                
        return justified_text
        
    def _type_character_with_formatting(self, char):
        """Type character with proper formatting"""
        if char == '\n':
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif char == '\t':
            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif char == ' ':
            win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            # Regular character typing
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                vk_code = vk & 0xFF
                shift_needed = vk & 0x100
                
                if shift_needed:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                win32api.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                if shift_needed:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                # Skip problematic characters
                pass
        
    def _type_special_char(self, char):
        """Type special characters using alternative method"""
        try:
            # Try using Unicode input method for special characters
            if ord(char) > 127:  # Non-ASCII character
                # Use clipboard method for special characters as fallback
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(char)
                win32clipboard.CloseClipboard()
                
                # Paste the character
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(ord('V'), 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.01)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                # Try direct VK code
                vk_code = ord(char.upper())
                if 32 <= vk_code <= 126:  # Printable ASCII
                    shift_needed = char.isupper()
                    if shift_needed:
                        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                        time.sleep(0.01)
                    win32api.keybd_event(vk_code, 0, 0, 0)
                    time.sleep(0.01)
                    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                    if shift_needed:
                        time.sleep(0.01)
                        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        except:
            pass  # Skip character if all methods fail
        
    def stop_typing(self):
        """Stop typing"""
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Typing stopped", fg="#888888")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        
    def update_progress(self, value):
        """Update progress display"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{value}%")
        
    def typing_complete(self):
        """Handle typing completion"""
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="✅ Typing completed!", fg="#00ff88")

def main():
    try:
        print("Starting AriTyper Working Version...")
        root = tk.Tk()
        app = AriTyperWorking(root)
        print("AriTyper ready!")
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
