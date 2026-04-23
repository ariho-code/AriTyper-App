#!/usr/bin/env python3
"""
AriTyper Streamlined - Core Typing Functionality with Modern UI
Simplified version focused on typing performance with clean licensing integration.
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

# Windows-specific imports for enhanced functionality
try:
    import pywintypes
    import win32gui
    import win32con
    import win32api
    import win32clipboard
    import win32com.client
    import pythoncom
    from docx import Document
    import PyPDF2
    from PIL import Image, ImageTk
    import io
    WINDOWS_SUPPORT = True
except ImportError:
    WINDOWS_SUPPORT = False

# ═══════════════════════════════════════════════════════
#  DESIGN TOKENS - Modern Clean UI
# ═══════════════════════════════════════════════════════
BG       = "#0a0e1a"
SURFACE  = "#141929"
CARD     = "#1a1f36"
CARD2    = "#21263a"
BORDER   = "#2a3244"
ACCENT   = "#00d4ff"
ACCENT2  = "#0066cc"
GREEN    = "#00ff88"
RED      = "#ff4757"
ORANGE   = "#ffa502"
YELLOW   = "#ffd93d"
TEXT     = "#ffffff"
MUTED    = "#8892b0"
DIM      = "#495670"

# Typography
FT_TITLE = ("Segoe UI", 24, "bold")
FT_SUB   = ("Segoe UI", 14, "bold")
FT_BODY  = ("Segoe UI", 11)
FT_SM    = ("Segoe UI", 9)
FT_BTN   = ("Segoe UI", 10, "bold")
FT_MONO  = ("Consolas", 10)

# ═══════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════

class GlowButton(tk.Button):
    """Modern button with hover effects"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            font=FT_BTN
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        current_bg = self.cget("bg")
        if current_bg == ACCENT:
            self.config(bg="#00e5ff")
        elif current_bg == GREEN:
            self.config(bg="#00ff99")
        elif current_bg == RED:
            self.config(bg="#ff5568")
        elif current_bg == ORANGE:
            self.config(bg="#ffb515")
            
    def _on_leave(self, e):
        self.config(bg=self.cget("bg").replace("e5", "d4").replace("99", "88").replace("68", "57").replace("b5", "a5"))

class RoundedCard(tk.Frame):
    """Modern card with rounded appearance"""
    def __init__(self, parent, border_color=ACCENT):
        super().__init__(parent, bg=CARD, relief="flat", bd=0)
        self.border_color = border_color
        self._outer = tk.Frame(self, bg=border_color, relief="flat", bd=1)
        self._inner = tk.Frame(self._outer, bg=CARD, relief="flat", bd=0)
        self._inner.pack(fill="both", expand=True, padx=1, pady=1)
        self._outer.pack(fill="both", expand=True)
        
    def pack(self, **kwargs):
        super().pack(**kwargs)
        
    def pack_forget(self):
        super().pack_forget()
        self._outer.pack_forget()

class ProgressArc(tk.Canvas):
    """Modern progress indicator"""
    def __init__(self, parent, w=300, h=8):
        super().__init__(parent, width=w, height=h, bg=CARD, highlightthickness=0)
        self.w, self.h = w, h
        self.pct = 0
        self._draw()
        
    def _draw(self):
        self.delete("all")
        bg_color = CARD2
        fg_color = ACCENT
        
        # Background
        self.create_rectangle(0, 0, self.w, self.h, fill=bg_color, outline="")
        
        # Progress
        if self.pct > 0:
            progress_w = int(self.w * self.pct / 100)
            self.create_rectangle(0, 0, progress_w, self.h, fill=fg_color, outline="")
            
    def set_pct(self, pct):
        self.pct = max(0, min(100, pct))
        self._draw()

# ═══════════════════════════════════════════════════════
#  MAIN APP CLASS
# ═══════════════════════════════════════════════════════

class AriTyperStreamlined:
    """Streamlined AriTyper with focus on core typing functionality"""
    
    def __init__(self, root):
        self.root = root
        self.server_url = "http://localhost:5000"
        self.device_id = self._generate_device_id()
        self.license_data = None
        self.target_window = None
        self.is_typing = False
        self.current_view = "activation"
        self.selected_file = None
        
        self._setup_window()
        self.create_activation_ui()
        self.start_app()
        
    def _setup_window(self):
        """Setup main window with modern styling"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.title("AriTyper - Professional Typing Tool")
        self.root.configure(bg=BG)
        self.root.minsize(800, 600)
        
        # Style ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", background=CARD, troughcolor=CARD2, 
                       slidercolor=ACCENT, sliderlength=20)
        
    # ═══════════════════════════════════════════
    #  ACTIVATION UI
    # ═══════════════════════════════════════════
    def create_activation_ui(self):
        """Clean activation interface"""
        self.activation_frame = tk.Frame(self.root, bg=BG)
        self.activation_frame.pack(fill="both", expand=True)
        
        # Header
        header = RoundedCard(self.activation_frame, border_color=ACCENT)
        header._outer.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(header._inner, text="🚀 AriTyper", font=FT_TITLE, 
                bg=CARD, fg=ACCENT).pack(pady=15)
        tk.Label(header._inner, text="Professional Typing Tool", font=FT_BODY,
                bg=CARD, fg=MUTED).pack()
        
        # Device info
        device_card = RoundedCard(self.activation_frame, border_color=BORDER)
        device_card._outer.pack(fill="x", padx=20, pady=5)
        
        tk.Label(device_card._inner, text=f"Device: {self.device_id}", font=FT_MONO,
                bg=CARD, fg=MUTED).pack(pady=10)
        
        # License status
        self.license_status_label = tk.Label(device_card._inner, text="🔒 Checking license...", 
                                           font=FT_BODY, bg=CARD, fg=ORANGE)
        self.license_status_label.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(self.activation_frame, text="Initializing...", 
                                    font=FT_BODY, bg=BG, fg=MUTED)
        self.status_label.pack(pady=10)
        
    def _build_main_ui(self):
        """Streamlined main typing interface"""
        if hasattr(self, 'activation_frame'):
            self.activation_frame.pack_forget()
            
        self.root.title("AriTyper - Licensed")
        
        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header = RoundedCard(main_frame, border_color=GREEN)
        header._outer.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(header._inner, text="✅ AriTyper - Licensed", font=FT_TITLE,
                bg=CARD, fg=GREEN).pack(pady=10)
        tk.Label(header._inner, text=f"Device: {self.device_id}", font=FT_MONO,
                bg=CARD, fg=MUTED).pack(pady=5)
        
        # Main content area
        content = tk.Frame(main_frame, bg=BG)
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Text input
        left = RoundedCard(content, border_color=ACCENT)
        left._outer.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(left._inner, text="📝 Text Content", font=FT_SUB,
                bg=CARD, fg=ACCENT).pack(pady=10)
        
        # Text input area
        self.text_area = scrolledtext.ScrolledText(
            left._inner, font=("Consolas", 11), bg=CARD2, fg=TEXT,
            wrap=tk.WORD, height=15, relief="flat", bd=0, padx=10, pady=10
        )
        self.text_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Quick actions
        actions = tk.Frame(left._inner, bg=CARD)
        actions.pack(fill="x", padx=15, pady=(0, 15))
        
        GlowButton(actions, text="📋 Paste", bg=ORANGE, fg=TEXT,
                  command=self.paste_text).pack(side="left", padx=(0, 5))
        GlowButton(actions, text="📂 Load File", bg=ACCENT2, fg=TEXT,
                  command=self.load_file).pack(side="left", padx=(0, 5))
        GlowButton(actions, text="🗑️ Clear", bg=RED, fg=TEXT,
                  command=self.clear_text).pack(side="right")
        
        # Right panel - Controls
        right = RoundedCard(content, border_color=BORDER)
        right._outer.pack(side="right", fill="y", padx=(5, 0))
        
        tk.Label(right._inner, text="⚙️ Typing Controls", font=FT_SUB,
                bg=CARD, fg=MUTED).pack(pady=10)
        
        # Window selection
        tk.Label(right._inner, text="Target Window:", font=FT_BODY,
                bg=CARD, fg=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.window_btn = GlowButton(right._inner, text="🪟 Select Window", 
                                     bg=ACCENT2, fg=TEXT, command=self.select_window)
        self.window_btn.pack(fill="x", padx=15, pady=(0, 10))
        
        self.window_info = tk.Label(right._inner, text="No window selected", 
                                   font=FT_SM, bg=CARD, fg=MUTED)
        self.window_info.pack(padx=15, pady=(0, 15))
        
        # Speed control
        tk.Label(right._inner, text="Typing Speed:", font=FT_BODY,
                bg=CARD, fg=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
        
        speed_frame = tk.Frame(right._inner, bg=CARD)
        speed_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.speed_var = tk.DoubleVar(value=50)
        ttk.Scale(speed_frame, from_=1, to=100, variable=self.speed_var,
                 orient="horizontal", length=150).pack(side="left")
        self.speed_label = tk.Label(speed_frame, text="50%", font=FT_MONO,
                                   bg=CARD, fg=ACCENT)
        self.speed_label.pack(side="left", padx=10)
        
        # Progress
        tk.Label(right._inner, text="Progress:", font=FT_BODY,
                bg=CARD, fg=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.progress_bar = ProgressArc(right._inner, w=200, h=8)
        self.progress_bar.pack(padx=15, pady=(0, 5))
        
        self.progress_label = tk.Label(right._inner, text="0%", font=FT_MONO,
                                      bg=CARD, fg=MUTED)
        self.progress_label.pack(padx=15, pady=(0, 15))
        
        # Control buttons
        self.start_btn = GlowButton(right._inner, text="▶️ Start Typing", 
                                   bg=GREEN, fg=TEXT, command=self.start_typing)
        self.start_btn.pack(fill="x", padx=15, pady=(0, 5))
        
        self.stop_btn = GlowButton(right._inner, text="⏹️ Stop", 
                                  bg=RED, fg=TEXT, state="disabled", command=self.stop_typing)
        self.stop_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Status
        self.main_status = tk.Label(main_frame, text="Ready to type", 
                                   font=FT_BODY, bg=BG, fg=MUTED)
        self.main_status.pack(pady=(0, 10))
        
    # ═══════════════════════════════════════════
    #  CORE FUNCTIONALITY
    # ═══════════════════════════════════════════
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_text = ""
            if WINDOWS_SUPPORT:
                try:
                    win32clipboard.OpenClipboard()
                    clipboard_text = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                except:
                    clipboard_text = self.root.clipboard_get()
            else:
                clipboard_text = self.root.clipboard_get()
                
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", clipboard_text)
            self.main_status.config(text=f"Pasted {len(clipboard_text)} characters", fg=GREEN)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {str(e)}")
            
    def clear_text(self):
        """Clear text area"""
        self.text_area.delete("1.0", tk.END)
        self.main_status.config(text="Text cleared", fg=MUTED)
        
    def load_file(self):
        """Load text from file"""
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
                elif file_ext == '.docx' and WINDOWS_SUPPORT:
                    doc = Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                elif file_ext == '.pdf' and WINDOWS_SUPPORT:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ''
                        for page in pdf_reader.pages:
                            content += page.extract_text() + '\n'
                else:
                    messagebox.showinfo("Info", "File format not supported")
                    return
                    
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.selected_file = file_path
                self.main_status.config(text=f"Loaded: {os.path.basename(file_path)}", fg=GREEN)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def select_window(self):
        """Select target window for typing"""
        if not WINDOWS_SUPPORT:
            messagebox.showinfo("Info", "Window selection requires Windows")
            return
            
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                windows.append((hwnd, win32gui.GetWindowText(hwnd)))
            return True
            
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if not windows:
            messagebox.showinfo("Info", "No accessible windows found")
            return
            
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Target Window")
        dialog.geometry("400x300")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select window to type into:", font=FT_BODY,
                bg=BG, fg=TEXT).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=FT_BODY, bg=CARD, fg=TEXT,
                            selectmode="single")
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        for hwnd, title in windows:
            listbox.insert(tk.END, f"{title[:50]}...")
            
        def select():
            selection = listbox.curselection()
            if selection:
                hwnd, title = windows[selection[0]]
                self.target_window = hwnd
                self.window_info.config(text=f"Target: {title[:30]}...", fg=GREEN)
                dialog.destroy()
                
        tk.Button(dialog, text="Select", font=FT_BTN, bg=GREEN, fg=TEXT,
                 command=select).pack(pady=10)
                 
    def start_typing(self):
        """Start typing into selected window"""
        text_content = self.text_area.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("No Text", "Please enter or paste text first")
            return
            
        if not self.target_window:
            messagebox.showwarning("No Window", "Please select a target window first")
            return
            
        self.is_typing = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.main_status.config(text="Typing in progress...", fg=ACCENT)
        
        def type_thread():
            try:
                # Focus target window
                if WINDOWS_SUPPORT:
                    win32gui.ShowWindow(self.target_window, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.target_window)
                    time.sleep(1)
                
                speed = self.speed_var.get()
                delay = 0.05 * max(0.05, 1.05 - speed / 100)
                total_chars = len(text_content)
                
                for i, char in enumerate(text_content):
                    if not self.is_typing:
                        break
                        
                    if WINDOWS_SUPPORT:
                        try:
                            if char == '\n':
                                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                            elif char == '\t':
                                win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
                                win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
                            else:
                                vk = win32api.VkKeyScan(char)
                                if vk != -1:
                                    win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                                    win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                        except:
                            pass
                            
                    # Update progress
                    progress = int((i + 1) / total_chars * 100)
                    self.root.after(0, lambda p=progress: self._update_progress(p))
                    time.sleep(delay)
                    
                if self.is_typing:
                    self.root.after(0, self._typing_complete)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Typing Error", str(e)))
                self.root.after(0, self.stop_typing)
                
        threading.Thread(target=type_thread, daemon=True).start()
        
    def stop_typing(self):
        """Stop typing"""
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.main_status.config(text="Typing stopped", fg=MUTED)
        
    def _update_progress(self, value):
        """Update progress display"""
        self.progress_bar.set_pct(value)
        self.progress_label.config(text=f"{value}%")
        
    def _typing_complete(self):
        """Handle typing completion"""
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.main_status.config(text="✅ Typing completed!", fg=GREEN)
        
    def _update_speed_label(self, value=None):
        """Update speed label"""
        speed = int(self.speed_var.get())
        self.speed_label.config(text=f"{speed}%")
        
    # ═══════════════════════════════════════════
    #  LICENSING SYSTEM
    # ═══════════════════════════════════════════
    def start_app(self):
        """Start app with license checking"""
        threading.Thread(target=self._check_license, daemon=True).start()
        
    def _check_license(self):
        """Check license and unlock if valid"""
        try:
            # Check local license file
            if os.path.exists("license.json"):
                with open("license.json") as f:
                    license_data = json.load(f)
                    
                # Validate with server
                response = requests.post(
                    f"{self.server_url}/api/device/validate_license",
                    json={"device_id": self.device_id, "license_key": license_data.get("license_key")},
                    timeout=10
                )
                
                if response.status_code == 200 and response.json().get("valid"):
                    self.root.after(0, self._unlock_app)
                    return
                    
        except:
            pass
            
        # Show activation screen
        self.root.after(0, lambda: self.license_status_label.config(
            text="🔒 License Required - Contact Admin", fg=RED))
        self.root.after(0, lambda: self.status_label.config(
            text="Please contact admin to activate your license"))
            
    def _unlock_app(self):
        """Unlock the app"""
        self.license_data = {"valid": True}
        self.root.after(0, self._build_main_ui)
        
    def _generate_device_id(self):
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

# ═══════════════════════════════════════════════════════
def main():
    try:
        print("Starting AriTyper Streamlined...")
        root = tk.Tk()
        app = AriTyperStreamlined(root)
        print("AriTyper ready!")
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
