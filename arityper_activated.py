#!/usr/bin/env python3
"""
AriTyper Activated — Premium UI Redesign
Activation-first flow with glassmorphism dark theme, smooth animations,
professional typography and rounded card layout.
All backend logic preserved from original.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
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
    from PIL import Image, ImageTk
    import io
    WINDOWS_SUPPORT = True
except ImportError:
    WINDOWS_SUPPORT = False
    # Create dummy objects if imports fail
    pywintypes = None
    win32gui = None
    win32con = None
    win32api = None
    win32clipboard = None
    win32com = None
    pythoncom = None

# Document processing imports (always available)
try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ═══════════════════════════════════════════════════════
#  LICENSING
# ═══════════════════════════════════════════════════════
# AriTyper is free and unrestricted. There is no activation step, no payment
# gate and no license server to call — the app always runs fully unlocked.
FREE_LICENSE = {
    "valid":      True,
    "plan":       "free",
    "expires_at": "Never",
    "message":    "AriTyper is free — no license required.",
}

# ═══════════════════════════════════════════════════════
#  DESIGN TOKENS
# ═══════════════════════════════════════════════════════
BG       = "#060b14"
SURFACE  = "#0b1623"
CARD     = "#0f1f31"
CARD2    = "#132538"
BORDER   = "#1a3050"
ACCENT   = "#00d4ff"
ACCENT2  = "#0066cc"
GREEN    = "#00e676"
ORANGE   = "#ffab40"
RED      = "#ff5252"
YELLOW   = "#ffd740"
TEXT     = "#ddeeff"
MUTED    = "#3d6080"
DIM      = "#1e3a55"

# Typography — Palatino for display, Verdana for body
FT_HERO  = ("Palatino", 28, "bold")
FT_HEAD  = ("Palatino", 17, "bold")
FT_SUB   = ("Verdana", 11, "bold")
FT_BODY  = ("Verdana", 9)
FT_MONO  = ("Courier New", 11, "bold")
FT_BTN   = ("Verdana", 11, "bold")
FT_SM    = ("Verdana", 8)
FT_CAPS  = ("Verdana", 8, "bold")


# ═══════════════════════════════════════════════════════
#  REUSABLE WIDGETS
# ═══════════════════════════════════════════════════════

class RoundedCard(tk.Frame):
    """Dark card with 1-px accent border achieved via outer/inner frame."""
    def __init__(self, parent, border_color=BORDER, **kw):
        outer = tk.Frame(parent, bg=border_color, bd=0)
        super().__init__(outer, bg=CARD, bd=0, **kw)
        self.pack(fill="both", expand=True, padx=1, pady=1)
        self._outer = outer

    def place_in(self, **pack_kw):
        self._outer.pack(**pack_kw)
        return self


class PulseLabel(tk.Label):
    """Label that alternates between two colours."""
    def __init__(self, *a, c1=ORANGE, c2=MUTED, interval=750, **kw):
        super().__init__(*a, **kw)
        self._c = [c1, c2]
        self._i = 0
        self._interval = interval
        self._active = False

    def start(self):
        self._active = True
        self._tick()

    def stop(self, color=None):
        self._active = False
        if color:
            self.config(fg=color)

    def _tick(self):
        if not self._active:
            return
        self.config(fg=self._c[self._i % 2])
        self._i += 1
        self.after(self._interval, self._tick)


class GlowButton(tk.Button):
    """Button with hover highlight and active-press effect."""
    def __init__(self, *a, base_bg=ACCENT, hover_bg=None, **kw):
        self._base  = base_bg
        self._hover = hover_bg or self._lighten(base_bg)
        super().__init__(*a, bg=base_bg, activebackground=self._hover,
                         relief="flat", bd=0, **kw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self._hover)

    def _on_leave(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self._base)

    @staticmethod
    def _lighten(hex_color):
        r = min(255, int(hex_color[1:3], 16) + 24)
        g = min(255, int(hex_color[3:5], 16) + 24)
        b = min(255, int(hex_color[5:7], 16) + 24)
        return f"#{r:02x}{g:02x}{b:02x}"


class ProgressArc(tk.Canvas):
    """Thin rounded progress bar drawn on a Canvas."""
    def __init__(self, parent, w=460, h=10, **kw):
        super().__init__(parent, width=w, height=h,
                         bg=CARD, highlightthickness=0, **kw)
        # NB: don't use self._w / self._h — Tkinter stores the widget's Tcl
        # path name in _w, and shadowing it breaks every canvas command.
        self._cw, self._ch = w, h
        self._pct = 0
        self._draw()

    def set_pct(self, v):
        self._pct = max(0, min(100, v))
        self._draw()

    def _draw(self):
        self.delete("all")
        r = self._ch // 2
        # track
        self._rr(0, 0, self._cw, self._ch, r, fill=CARD2, outline=DIM)
        # fill
        fw = int(self._cw * self._pct / 100)
        if fw >= self._ch:
            self._rr(0, 0, fw, self._ch, r, fill=ACCENT, outline="")
        elif fw > 0:
            self.create_oval(0, 0, self._ch, self._ch, fill=ACCENT, outline="")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        self.create_polygon(pts, smooth=True, **kw)


def _sep(parent, bg=BORDER, pady=6):
    tk.Frame(parent, height=1, bg=bg).pack(fill="x", padx=20, pady=pady)


def _section(parent, icon, title, bg=CARD):
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x", padx=20, pady=(14, 4))
    tk.Label(row, text=icon, font=("Segoe UI Emoji", 13),
             bg=bg, fg=ACCENT).pack(side="left")
    tk.Label(row, text=f"  {title}", font=FT_SUB,
             bg=bg, fg=TEXT).pack(side="left")
    _sep(parent, pady=4)


# ═══════════════════════════════════════════════════════
#  MAIN APP CLASS
# ═══════════════════════════════════════════════════════

class AriTyperActivated:
    """AriTyper with activation-first UI — premium redesign."""

    def __init__(self, root):
        self.root = root
        self.server_url = "http://localhost:5000"
        self.device_id = self._generate_device_id()
        # AriTyper is free — no license server, no activation, no payment.
        self.license_data = FREE_LICENSE
        self.target_window = None
        self.is_typing = False
        self.current_view = "main"

        self._setup_window()
        self._style_ttk()
        self.create_main_ui()

    # ───────────────────────────────────────────
    #  WINDOW
    # ───────────────────────────────────────────
    def _setup_window(self):
        self.root.title("AriTyper")
        self.root.geometry("920x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(720, 540)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 460
        y = (self.root.winfo_screenheight() // 2) - 360
        self.root.geometry(f"920x720+{x}+{y}")

    def _style_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TScrollbar",
                    troughcolor=SURFACE, background=BORDER,
                    arrowcolor=MUTED,   bordercolor=SURFACE)
        s.configure("Horizontal.TScale",
                    background=CARD2, troughcolor=DIM, slidercolor=ACCENT)

    # ───────────────────────────────────────────
    #  SHARED HEADER
    # ───────────────────────────────────────────
    def _build_header(self, parent, tag="Free · No License Needed"):
        hdr = tk.Frame(parent, bg=SURFACE, height=82)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # left colour bar
        tk.Frame(hdr, width=5, bg=ACCENT).pack(side="left", fill="y")

        left = tk.Frame(hdr, bg=SURFACE)
        left.pack(side="left", fill="both", expand=True, padx=20)

        tk.Label(left, text="⌨  AriTyper",
                 font=FT_HERO, bg=SURFACE, fg=ACCENT).pack(anchor="w", pady=(10, 0))
        tk.Label(left, text="Professional Document Typing Software",
                 font=FT_SM, bg=SURFACE, fg=MUTED).pack(anchor="w")

        # right tag badge
        badge = tk.Frame(hdr, bg=DIM, padx=12, pady=4)
        badge.pack(side="right", padx=20, pady=22)
        tk.Label(badge, text=tag, font=FT_CAPS, bg=DIM, fg=ACCENT).pack()


    # ═══════════════════════════════════════════
    #  MAIN UI (post-activation)
    # ═══════════════════════════════════════════
    def create_main_ui(self):
        if hasattr(self, "activation_frame"):
            self.activation_frame.pack_forget()
        self.root.title("AriTyper  ·  Free")

        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(fill="both", expand=True)

        self._build_header(self.main_frame, tag="✅  Free")

        # active pill bar
        pill = tk.Frame(self.main_frame, bg=SURFACE, height=30)
        pill.pack(fill="x")
        pill.pack_propagate(False)
        tk.Label(pill, text=f"● ACTIVE  |  {self.device_id[:22]}…",
                 font=FT_CAPS, bg=SURFACE, fg=GREEN, padx=16).pack(side="left", pady=6)

        # ── grid layout body ──────────────────────
        body = tk.Frame(self.main_frame, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=18)

        # Configure grid columns for better space usage
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # Create panels with grid
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 4))
        
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 4))

        # Document display panel (spans full width)
        doc_panel = tk.Frame(body, bg=BG)
        doc_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(4, 0))

        self._build_file_panel(left)
        self._build_controls_panel(right)
        self._build_document_panel(doc_panel)

        self.main_status_label = tk.Label(
            self.main_frame, text="Ready.",
            font=FT_BODY, bg=BG, fg=MUTED)
        self.main_status_label.pack(pady=(0, 10))

    # ── File panel ───────────────────────────────
    def _build_file_panel(self, parent):
        c = RoundedCard(parent)
        c._outer.pack(fill="both", expand=True)

        _section(c, "📄", "Document & Content Input")

        # Quick actions row - prominent paste and window selection
        quick_actions = tk.Frame(c, bg=CARD)
        quick_actions.pack(fill="x", padx=20, pady=(0, 12))

        # Window selection button (prominent)
        self.window_btn = GlowButton(
            quick_actions, text="🪟 Select Window",
            font=FT_BTN, base_bg=ACCENT2, fg=TEXT,
            padx=16, pady=10, cursor="hand2",
            command=self.select_target_window
        )
        self.window_btn.pack(side="left", padx=(0, 8))

        # Paste button (prominent)
        self.paste_btn = GlowButton(
            quick_actions, text="📋 Paste Text",
            font=FT_BTN, base_bg=ORANGE, fg=TEXT,
            padx=16, pady=10, cursor="hand2",
            command=self.paste_text
        )
        self.paste_btn.pack(side="left", padx=(0, 8))

        # Clear button
        self.clear_btn = GlowButton(
            quick_actions, text="🗑️ Clear",
            font=FT_BTN, base_bg=RED, fg=TEXT,
            padx=16, pady=10, cursor="hand2",
            command=self.clear_document
        )
        self.clear_btn.pack(side="right")

        # Window info label
        self.window_info = tk.Label(
            c, text="No target window selected",
            font=FT_SM, bg=CARD, fg=MUTED
        )
        self.window_info.pack(anchor="w", padx=20, pady=(0, 8))

        _sep(c, pady=8)

        # drop zone
        dz = tk.Frame(c, bg=CARD2, cursor="hand2", padx=10, pady=10)
        dz.pack(fill="x", padx=20, pady=(0, 12))
        dz.bind("<Button-1>", lambda e: self.browse_file())

        tk.Label(dz, text="📂", font=("Segoe UI Emoji", 30),
                 bg=CARD2, fg=MUTED).pack(pady=(16, 4))
        self.file_label = tk.Label(
            dz, text="Click to select or drag a file",
            font=FT_BODY, bg=CARD2, fg=MUTED, wraplength=280)
        self.file_label.pack(pady=(0, 4))
        tk.Label(dz, text="TXT  ·  DOCX  ·  PDF",
                 font=FT_SM, bg=CARD2, fg=DIM).pack(pady=(0, 18))

        GlowButton(
            c, text="Browse Files",
            font=FT_BTN, base_bg=ACCENT2, fg=TEXT,
            padx=20, pady=10, cursor="hand2",
            command=self.browse_file
        ).pack(padx=20, pady=(0, 18))

    # ── Controls panel ───────────────────────────
    def _build_controls_panel(self, parent):
        c = RoundedCard(parent)
        c._outer.pack(fill="both", expand=True)

        _section(c, "⌨", "Typing Controls")

        # Speed
        sr = tk.Frame(c, bg=CARD)
        sr.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(sr, text="Speed", font=FT_BODY, bg=CARD, fg=MUTED).pack(side="left")
        self.speed_var = tk.DoubleVar(value=50)
        ttk.Scale(sr, from_=1, to=100, variable=self.speed_var,
                  orient="horizontal", length=170,
                  command=self._update_speed_label
                  ).pack(side="left", padx=10)
        self.speed_label = tk.Label(sr, text="50 %",
                                    font=FT_MONO, bg=CARD, fg=ACCENT)
        self.speed_label.pack(side="left")

        # Progress bar
        pb_wrap = tk.Frame(c, bg=CARD)
        pb_wrap.pack(fill="x", padx=20, pady=(10, 4))
        tk.Label(pb_wrap, text="Progress", font=FT_SM,
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 4))
        self.progress_bar = ProgressArc(pb_wrap, w=360, h=12)
        self.progress_bar.pack()

        self._pct_lbl = tk.Label(c, text="0 %", font=FT_SM, bg=CARD, fg=MUTED)
        self._pct_lbl.pack(anchor="e", padx=24, pady=(2, 10))

        _sep(c, pady=6)

        # Buttons
        br = tk.Frame(c, bg=CARD)
        br.pack(padx=20, pady=(6, 18))

        self.start_btn = GlowButton(
            br, text="▶  Start Typing",
            font=FT_BTN, base_bg=GREEN, fg=BG,
            padx=26, pady=13, cursor="hand2",
            command=self.start_typing)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = GlowButton(
            br, text="⏹  Stop",
            font=FT_BTN, base_bg=RED, fg=TEXT,
            padx=26, pady=13, cursor="hand2",
            state="disabled", command=self.stop_typing)
        self.stop_btn.pack(side="left")

    # ── Document panel ───────────────────────────
    def _build_document_panel(self, parent):
        c = RoundedCard(parent)
        c._outer.pack(fill="both", expand=True)

        _section(c, "📖", "Document Content Preview")

        # Document display area
        self.doc_frame = tk.Frame(c, bg=CARD2)
        self.doc_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        # Document text display
        self.doc_text = scrolledtext.ScrolledText(
            self.doc_frame, 
            font=("Consolas", 11),
            bg=CARD2, fg=TEXT,
            wrap=tk.WORD,
            height=8,
            relief="flat",
            bd=0,
            padx=12, pady=8
        )
        self.doc_text.pack(fill="both", expand=True)
        self.doc_text.config(state="disabled")

        # Status info
        status_frame = tk.Frame(c, bg=CARD)
        status_frame.pack(fill="x", padx=20, pady=(0, 18))
        
        self.doc_status = tk.Label(
            status_frame, text="No content loaded - paste text or select a file",
            font=FT_SM, bg=CARD, fg=MUTED
        )
        self.doc_status.pack(anchor="w")

    # ═══════════════════════════════════════════
    #  BACKEND  (free build — no licensing)
    # ═══════════════════════════════════════════
    def start_app(self):
        """No-op: AriTyper is free, so there is nothing to register or verify."""
        self.license_data = FREE_LICENSE

    def _unlock_app(self):
        """The app ships unlocked; kept so old call sites stay valid."""
        self.license_data = FREE_LICENSE
        if self.current_view != "main":
            self.current_view = "main"
            self.create_main_ui()

    def _check_license(self):
        """Always licensed — no server call, works fully offline."""
        self.license_data = FREE_LICENSE

    def _get_local_license_key(self):
        return None


    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[("PDF", "*.pdf"), ("Word", "*.docx"),
                       ("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.selected_file = path
            fname = os.path.basename(path)
            self.file_label.config(text=fname, fg=TEXT)
            self.main_status_label.config(text=f"File loaded: {fname}", fg=GREEN)

    def start_typing(self):
        # Get text content - try document display first, then file
        text_content = ""
        
        if hasattr(self, 'doc_text'):
            try:
                self.doc_text.config(state="normal")
                text_content = self.doc_text.get("1.0", tk.END).strip()
                self.doc_text.config(state="disabled")
            except:
                pass
        
        # If no content in display, try loading from file
        if not text_content and hasattr(self, 'selected_file') and self.selected_file:
            try:
                file_ext = os.path.splitext(self.selected_file)[1].lower()
                if file_ext == '.txt':
                    try:
                        with open(self.selected_file, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                    except UnicodeDecodeError:
                        with open(self.selected_file, 'r', encoding='latin-1') as f:
                            text_content = f.read()
                elif file_ext == '.docx' and DOCX_SUPPORT:
                    doc = Document(self.selected_file)
                    text_content = '\n'.join([para.text for para in doc.paragraphs])
                elif file_ext == '.pdf' and PDF_SUPPORT:
                    with open(self.selected_file, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text_content = ''
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() + '\n'
            except:
                pass
        
        if not text_content:
            messagebox.showwarning("No Content", "Please load or paste text content first.")
            return
            
        self.is_typing = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.main_status_label.config(text="Typing in progress…", fg=ACCENT)
        self.progress_bar.set_pct(0)

        def _run():
            try:
                # Bring target window to front if selected
                if hasattr(self, 'target_window') and self.target_window and WINDOWS_SUPPORT:
                    try:
                        win32gui.ShowWindow(self.target_window, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(self.target_window)
                        time.sleep(1)  # Give window time to focus
                    except:
                        pass
                
                speed = self.speed_var.get()
                delay = 0.05 * max(0.05, 1.05 - speed / 100)
                total_chars = len(text_content)
                
                # Type the content
                if WINDOWS_SUPPORT:
                    # Use Windows API for typing
                    for i, char in enumerate(text_content):
                        if not self.is_typing:
                            break
                        
                        try:
                            if char == '\n':
                                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                            elif char == '\t':
                                win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
                                win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
                            else:
                                # Convert character to key code
                                vk = win32api.VkKeyScan(char)
                                if vk != -1:
                                    win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                                    win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                                else:
                                    # Handle special characters
                                    if char.isupper():
                                        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                                        vk = win32api.VkKeyScan(char.lower())
                                        if vk != -1:
                                            win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                                            win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                                        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                        except:
                            # Skip problematic characters
                            pass
                        
                        # Update progress
                        progress = int((i + 1) / total_chars * 100)
                        self.root.after(0, self._set_progress, progress)
                        time.sleep(delay)
                else:
                    # Fallback - just simulate progress
                    for i in range(total_chars):
                        if not self.is_typing:
                            break
                        progress = int((i + 1) / total_chars * 100)
                        self.root.after(0, self._set_progress, progress)
                        time.sleep(delay)
                
                if self.is_typing:
                    self.root.after(0, self._done_typing)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Typing Error", f"Failed to type: {str(e)}"))
                self.root.after(0, self.stop_typing)
                
        threading.Thread(target=_run, daemon=True).start()

    def _set_progress(self, v):
        self.progress_bar.set_pct(v)
        self._pct_lbl.config(text=f"{v} %")

    def _done_typing(self):
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.main_status_label.config(text="✅  Typing complete!", fg=GREEN)

    def stop_typing(self):
        self.is_typing = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_bar.set_pct(0)
        self._pct_lbl.config(text="0 %")
        self.main_status_label.config(text="Stopped.", fg=MUTED)

    def _update_speed_label(self, val=None):
        v = int(self.speed_var.get())
        self.speed_label.config(text=f"{v} %")

    def _generate_device_id(self):
        parts = []
        try:    parts.append(socket.gethostname())
        except: pass
        parts.append(platform.system())
        parts.append(platform.machine())
        try:
            import uuid
            parts.append(str(uuid.getnode()))
        except: pass
        h = hashlib.sha256("|".join(parts).encode()).hexdigest()
        return f"ARI-{h[:16].upper()}"

    # ═══════════════════════════════════════════
    #  ENHANCED FUNCTIONALITY
    # ═══════════════════════════════════════════
    def select_target_window(self):
        """Allow user to select a window to type into"""
        if not WINDOWS_SUPPORT:
            messagebox.showerror("Error", "Window selection requires Windows OS with pywin32 installed.")
            return
            
        try:
            def enum_windows_callback(hwnd, windows):
                try:
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        windows.append((hwnd, win32gui.GetWindowText(hwnd)))
                except:
                    pass
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if not windows:
                messagebox.showinfo("No Windows", "No accessible windows found.")
                return

            # Create window selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Select Target Window")
            dialog.geometry("500x400")
            dialog.configure(bg=BG)
            dialog.transient(self.root)
            dialog.grab_set()

            tk.Label(dialog, text="Select the window where you want to type:",
                    font=FT_BODY, bg=BG, fg=TEXT).pack(pady=10)

            # Listbox with scrollbar
            list_frame = tk.Frame(dialog, bg=BG)
            list_frame.pack(fill="both", expand=True, padx=20, pady=10)

            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")

            window_listbox = tk.Listbox(list_frame, font=FT_BODY, bg=CARD2, fg=TEXT,
                                       yscrollcommand=scrollbar.set, relief="flat", bd=0)
            window_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=window_listbox.yview)

            for hwnd, title in windows:
                window_listbox.insert(tk.END, f"{title[:60]}...")

            def select_window():
                selection = window_listbox.curselection()
                if selection:
                    hwnd, title = windows[selection[0]]
                    self.target_window = hwnd
                    if hasattr(self, 'window_info'):
                        self.window_info.config(text=f"Target: {title[:40]}...", fg=GREEN)
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Selected: {title}")

            tk.Button(dialog, text="Select", font=FT_BTN, bg=GREEN, fg=TEXT,
                     command=select_window).pack(pady=10)
                     
        except Exception as e:
            messagebox.showerror("Error", f"Window selection failed: {str(e)}")

    def paste_text(self):
        """Paste text from clipboard to document display"""
        try:
            self.doc_text.config(state="normal")
            self.doc_text.delete("1.0", tk.END)
            
            # Get clipboard content
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                self.doc_text.insert("1.0", data)
                self.main_status_label.config(text="✅ Text pasted successfully", fg=GREEN)
                if hasattr(self, 'doc_status'):
                    self.doc_status.config(text=f"Text pasted - {len(data)} characters", fg=GREEN)
            except:
                # Fallback to tkinter clipboard
                try:
                    data = self.root.clipboard_get()
                    self.doc_text.insert("1.0", data)
                    self.main_status_label.config(text="✅ Text pasted successfully", fg=GREEN)
                    if hasattr(self, 'doc_status'):
                        self.doc_status.config(text=f"Text pasted - {len(data)} characters", fg=GREEN)
                except:
                    messagebox.showinfo("Info", "No text found in clipboard")
                    
            self.doc_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste text: {str(e)}")

    def clear_document(self):
        """Clear document display"""
        self.doc_text.config(state="normal")
        self.doc_text.delete("1.0", tk.END)
        self.doc_text.config(state="disabled")
        self.main_status_label.config(text="Document cleared", fg=MUTED)
        if hasattr(self, 'doc_status'):
            self.doc_status.config(text="No content loaded - paste text or select a file", fg=MUTED)

    def load_document(self, file_path):
        """Load and display document content"""
        try:
            # Store file path for typing
            self.selected_file = file_path
            
            # Update file label
            fname = os.path.basename(file_path)
            self.file_label.config(text=fname[:30] + "...", fg=TEXT)
            
            # Load content into document display
            content = ""
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                        
            elif file_ext == '.docx':
                if not DOCX_SUPPORT:
                    messagebox.showerror("Error", "DOCX support not available. Please install python-docx.")
                    return
                try:
                    doc = Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load DOCX file: {str(e)}")
                    return
                    
            elif file_ext == '.pdf':
                if not PDF_SUPPORT:
                    messagebox.showerror("Error", "PDF support not available. Please install PyPDF2.")
                    return
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ''
                        for page in pdf_reader.pages:
                            content += page.extract_text() + '\n'
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load PDF file: {str(e)}")
                    return
            else:
                messagebox.showerror("Error", "Unsupported file format.")
                return
            
            # Display content in text widget
            if hasattr(self, 'doc_text'):
                try:
                    self.doc_text.config(state="normal")
                    self.doc_text.delete("1.0", tk.END)
                    self.doc_text.insert("1.0", content)
                    self.doc_text.config(state="disabled")
                except Exception as e:
                    print(f"Error updating text widget: {e}")
            
            self.main_status_label.config(text=f"✅ Loaded: {fname}", fg=GREEN)
            if hasattr(self, 'doc_status'):
                self.doc_status.config(text=f"Loaded {fname} - {len(content)} characters", fg=GREEN)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load document: {str(e)}")

    def browse_file(self):
        """Enhanced file browser with document loading"""
        file_types = [
            ("All Supported", "*.txt;*.docx;*.pdf"),
            ("Text Files", "*.txt"),
            ("Word Documents", "*.docx"),
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=file_types
        )
        
        if file_path:
            self.load_document(file_path)


# ═══════════════════════════════════════════════════════
def main():
    try:
        print("Starting AriTyper Activated…")
        root = tk.Tk()
        AriTyperActivated(root)
        print("AriTyper ready!")
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Startup Error",
                f"An error occurred while starting AriTyper:\n\n{e}")
        except: pass
        sys.exit(1)

if __name__ == "__main__":
    main()
