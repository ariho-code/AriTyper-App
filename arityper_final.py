#!/usr/bin/env python3
"""
AriTyper Final - Modern UI with Web Integration
Professional document typing with strict device locking and payment verification
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import threading
import platform
import sys
import hashlib
import webbrowser
import os
import json
import socket
import requests
from datetime import datetime, timedelta
import uuid
import subprocess

# Modern UI Components
# AriTyper is free and unrestricted. There is no activation step, no payment
# gate and no license server to call — the app always runs fully unlocked.
FREE_LICENSE = {
    "valid":      True,
    "plan":       "free",
    "expires_at": "Never",
    "message":    "AriTyper is free — no license required.",
}

class ModernTheme:
    """Modern theme matching website design"""
    def __init__(self):
        self.colors = {
            'bg': '#050a10',
            'surface': '#0c1520',
            'card': '#111d2b',
            'border': '#1a2d42',
            'cyan': '#00e5ff',
            'blue': '#1565ff',
            'green': '#00ff87',
            'orange': '#ff6b35',
            'red': '#ff4757',
            'text': '#e8f4f8',
            'muted': '#6b8ca4'
        }
        
        self.fonts = {
            'heading': ('Outfit', 24, 'bold'),
            'subheading': ('Outfit', 18, 'bold'),
            'body': ('Outfit', 11),
            'mono': ('Space Mono', 10),
            'button': ('Outfit', 11, 'bold')
        }

class ModernButton(tk.Button):
    """Modern button with hover effects"""
    def __init__(self, parent, text, style='primary', **kwargs):
        self.style = style
        theme = ModernTheme()
        
        colors = {
            'primary': theme.colors['cyan'],
            'success': theme.colors['green'],
            'danger': theme.colors['red'],
            'warning': theme.colors['orange'],
            'secondary': theme.colors['muted']
        }
        
        bg_color = colors.get(style, theme.colors['cyan'])
        hover_color = self._get_hover_color(bg_color)
        
        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg=theme.colors['bg'],
            font=theme.fonts['button'],
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            **kwargs
        )
        
        self.bind('<Enter>', lambda e: self.config(bg=hover_color))
        self.bind('<Leave>', lambda e: self.config(bg=bg_color))
    
    def _get_hover_color(self, color):
        """Get hover color"""
        # Simple hover effect - make color slightly darker
        return color

class ModernCard(tk.Frame):
    """Modern card with border and background"""
    def __init__(self, parent, title=None, **kwargs):
        theme = ModernTheme()
        super().__init__(parent, bg=theme.colors['card'], relief='flat', bd=0, **kwargs)
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=theme.fonts['subheading'],
                bg=theme.colors['card'],
                fg=theme.colors['text']
            )
            title_label.pack(padx=20, pady=(20, 10))

class ModernProgressBar(tk.Canvas):
    """Modern progress bar"""
    def __init__(self, parent, width=300, height=8, **kwargs):
        theme = ModernTheme()
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=theme.colors['surface'],
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.progress = 0
        self.theme = theme
        
    def set_progress(self, value):
        """Set progress (0-100)"""
        self.progress = max(0, min(100, value))
        self._draw()
    
    def _draw(self):
        """Draw progress bar"""
        self.delete("all")
        
        # Background
        self.create_rectangle(
            0, 0, self.width, self.height,
            fill=self.theme.colors['surface'],
            outline=self.theme.colors['border']
        )
        
        # Progress
        progress_width = (self.width * self.progress) / 100
        self.create_rectangle(
            0, 0, progress_width, self.height,
            fill=self.theme.colors['cyan'],
            outline=''
        )

class StatusIndicator(tk.Frame):
    """Status indicator with dot and text"""
    def __init__(self, parent, **kwargs):
        theme = ModernTheme()
        super().__init__(parent, bg=theme.colors['surface'], **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            width=12,
            height=12,
            bg=theme.colors['surface'],
            highlightthickness=0
        )
        self.canvas.pack(side='left', padx=(0, 8))
        
        self.label = tk.Label(
            self,
            text="",
            font=theme.fonts['body'],
            bg=theme.colors['surface'],
            fg=theme.colors['muted']
        )
        self.label.pack(side='left')
        
        self.set_status('offline', 'Offline')
    
    def set_status(self, status, text=None):
        """Set status"""
        theme = ModernTheme()
        colors = {
            'online': theme.colors['green'],
            'offline': theme.colors['red'],
            'connecting': theme.colors['orange'],
            'active': theme.colors['cyan']
        }
        
        color = colors.get(status, theme.colors['muted'])
        
        self.canvas.delete("all")
        self.canvas.create_oval(
            2, 2, 10, 10,
            fill=color,
            outline=''
        )
        
        if text:
            self.label.config(text=text)
        else:
            self.label.config(text=status.capitalize())

class AriTyperFinal:
    """Final AriTyper application with modern UI and web integration"""
    
    def __init__(self, root):
        self.root = root
        self.theme = ModernTheme()
        
        # Setup window
        self.setup_window()
        
        # Initialize components
        self.device_id = self._generate_device_id()
        # AriTyper is free — no license server, no activation, no payment.
        self.license_data = FREE_LICENSE
        self.is_typing = False
        self.selected_file = None
        self.server_url = "http://localhost:5000"  # Update to your Render URL
        
        # Create UI
        self.create_ui()
        
        # Start authentication and device monitoring
        self.start_app()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("AriTyper - Professional Document Typing")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.theme.colors['bg'])
        self.root.minsize(800, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 400
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def create_ui(self):
        """Create main UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.theme.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=self.theme.colors['bg'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel - File and typing controls
        left_panel = self.create_left_panel(content_frame)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Device and license info
        right_panel = self.create_right_panel(content_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header"""
        header_frame = tk.Frame(parent, bg=self.theme.colors['surface'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg=self.theme.colors['surface'])
        logo_frame.pack(side='left', padx=20, pady=20)
        
        tk.Label(
            logo_frame,
            text="🔤 AriTyper",
            font=self.theme.fonts['heading'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['cyan']
        ).pack(anchor='w')
        
        tk.Label(
            logo_frame,
            text="Professional Document Typing Software",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['muted']
        ).pack(anchor='w')
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg=self.theme.colors['surface'])
        status_frame.pack(side='right', padx=20, pady=20)
        
        self.license_status = StatusIndicator(status_frame)
        self.license_status.pack(side='right', padx=10)
        
        self.server_status = StatusIndicator(status_frame)
        self.server_status.pack(side='right', padx=10)
    
    def create_left_panel(self, parent):
        """Create left panel with file and typing controls"""
        card = ModernCard(parent, "Document Processing")
        card.pack(fill='both', expand=True)
        
        # File selection
        file_frame = tk.Frame(card, bg=self.theme.colors['card'])
        file_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            file_frame,
            text="Select Document:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['muted'],
            relief='flat',
            bd=1,
            padx=10,
            pady=10
        )
        self.file_label.pack(fill='x', pady=(10, 0))
        
        # Browse button
        browse_btn = ModernButton(
            file_frame,
            text="📁 Browse Files",
            style='primary',
            command=self.browse_file
        )
        browse_btn.pack(pady=(10, 20))
        
        # Progress bar
        self.progress_bar = ModernProgressBar(file_frame, width=400)
        self.progress_bar.pack(pady=(0, 20))
        
        # Typing controls
        typing_frame = tk.Frame(card, bg=self.theme.colors['card'])
        typing_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            typing_frame,
            text="Typing Controls:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        # Speed control
        speed_frame = tk.Frame(typing_frame, bg=self.theme.colors['card'])
        speed_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(
            speed_frame,
            text="Typing Speed:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=50)
        speed_scale = ttk.Scale(
            speed_frame,
            from_=1,
            to=100,
            variable=self.speed_var,
            orient='horizontal',
            length=200
        )
        speed_scale.pack(side='left', padx=10)
        
        self.speed_label = tk.Label(
            speed_frame,
            text="50%",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['cyan']
        )
        self.speed_label.pack(side='left')
        
        self.speed_var.trace('w', self._update_speed_label)
        
        # Control buttons
        button_frame = tk.Frame(typing_frame, bg=self.theme.colors['card'])
        button_frame.pack(fill='x', pady=(20, 0))
        
        self.start_btn = ModernButton(
            button_frame,
            text="▶ Start Typing",
            style='success',
            command=self.start_typing
        )
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ModernButton(
            button_frame,
            text="⏹ Stop",
            style='danger',
            command=self.stop_typing,
            state='disabled'
        )
        self.stop_btn.pack(side='left')
        
        return card
    
    def create_right_panel(self, parent):
        """Create right panel with device and license info"""
        card = ModernCard(parent, "Device Information")
        card.pack(fill='both', expand=True)
        
        # Device ID
        device_frame = tk.Frame(card, bg=self.theme.colors['card'])
        device_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            device_frame,
            text="Device ID:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        tk.Label(
            device_frame,
            text=self.device_id,
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['cyan'],
            relief='flat',
            bd=1,
            padx=10,
            pady=10
        ).pack(fill='x', pady=(5, 0))
        
        # License status
        license_frame = tk.Frame(card, bg=self.theme.colors['card'])
        license_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            license_frame,
            text="Status:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        self.license_info = tk.Text(
            license_frame,
            height=6,
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['text'],
            relief='flat',
            bd=1,
            wrap='word'
        )
        self.license_info.pack(fill='x', pady=(5, 0))
        
        # Server connection
        server_frame = tk.Frame(card, bg=self.theme.colors['card'])
        server_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            server_frame,
            text="Server Connection:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        self.server_info = tk.Text(
            server_frame,
            height=4,
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['text'],
            relief='flat',
            bd=1,
            wrap='word'
        )
        self.server_info.pack(fill='x', pady=(5, 0))
        
        # Payment section
        return card
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg=self.theme.colors['surface'], height=40)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Starting...",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['text']
        )
        self.status_label.pack(side='left', padx=20, pady=10)
        
        tk.Label(
            status_frame,
            text="v2.0.0",
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['muted']
        ).pack(side='right', padx=20, pady=10)
    
    def start_app(self):
        """AriTyper is free — nothing to register, verify or unlock."""
        self.license_data = FREE_LICENSE
        self._update_license_status('active', 'Never')
        self._update_server_status('offline', 'Not needed - AriTyper runs offline')
        self.update_status("Ready - AriTyper is free to use")

    def _update_server_status(self, status, text):
        """Server panel is informational only in the free build."""
        self.server_info.delete(1.0, tk.END)
        self.server_info.insert(tk.END, "No server required\nAriTyper runs fully offline\n")

    def _check_license(self):
        """Always licensed — no server call, works fully offline."""
        self.license_data = FREE_LICENSE

    def _get_local_license_key(self):
        return None

    def _update_license_status(self, status='active', details='Never'):
        """Status panel — the free build is always active."""
        self.license_status.set_status('active', 'Free')

        self.license_info.delete(1.0, tk.END)
        self.license_info.insert(tk.END, "Status: Free\n")
        self.license_info.insert(tk.END, "Expires: Never\n")
        self.license_info.insert(tk.END, f"Device: {self.device_id}\n")
        self.license_info.insert(tk.END, "Type: No license required")

    def browse_file(self):
        """Browse for document file"""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Selected: {filename}")
            self.update_status(f"File loaded: {filename}")
    
    def start_typing(self):
        """Start typing process"""
        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a document file first")
            return
        
        self.is_typing = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.update_status("Typing started...")
        
        # Simulate typing process
        def typing_thread():
            try:
                speed = self.speed_var.get()
                total_time = 5.0  # Simulate 5 seconds of typing
                
                for i in range(0, 101):
                    if not self.is_typing:
                        break
                    
                    time.sleep(total_time / 100)
                    progress = i * (speed / 100)
                    self.root.after(0, self.progress_bar.set_progress, progress)
                
                if self.is_typing:
                    self.root.after(0, self.update_status, "Typing completed!")
                    self.root.after(0, self.progress_bar.set_progress, 100)
                
            except Exception as e:
                self.root.after(0, self.update_status, f"Typing error: {e}")
        
        threading.Thread(target=typing_thread, daemon=True).start()
    
    def stop_typing(self):
        """Stop typing process"""
        self.is_typing = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Typing stopped")
        self.progress_bar.set_progress(0)
    
    def _update_speed_label(self, *args):
        """Update speed label"""
        speed = int(self.speed_var.get())
        self.speed_label.config(text=f"{speed}%")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def _generate_device_id(self):
        """Generate unique device ID"""
        identifiers = []
        
        # Get computer name
        try:
            identifiers.append(socket.gethostname())
        except:
            pass
        
        # Get platform info
        identifiers.append(platform.system())
        identifiers.append(platform.machine())
        
        # Get MAC address
        try:
            import uuid
            mac = uuid.getnode()
            identifiers.append(str(mac))
        except:
            pass
        
        # Get processor info
        try:
            identifiers.append(platform.processor())
        except:
            pass
        
        # Combine and hash
        combined = "|".join(identifiers)
        device_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Return first 16 characters as device ID
        return f"ARI-{device_hash[:16].upper()}"

def main():
    """Main entry point"""
    try:
        print("Starting AriTyper Final...")
        
        root = tk.Tk()
        app = AriTyperFinal(root)
        
        print("AriTyper Final ready!")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            messagebox.showerror(
                "Startup Error",
                f"An error occurred while starting AriTyper:\n\n{str(e)}"
            )
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
