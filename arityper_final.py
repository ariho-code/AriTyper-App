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
        self.license_data = None
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
        card = ModernCard(parent, "Device & License Information")
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
            text="License Status:",
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
        payment_frame = tk.Frame(card, bg=self.theme.colors['card'])
        payment_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            payment_frame,
            text="Payment & Activation:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['card'],
            fg=self.theme.colors['text']
        ).pack(anchor='w')
        
        # Payment info
        payment_info_frame = tk.Frame(payment_frame, bg=self.theme.colors['surface'], relief='flat', bd=1)
        payment_info_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(
            payment_info_frame,
            text="Pay UGX 10,000 to:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['text']
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(
            payment_info_frame,
            text="• Airtel Money: 66562536",
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['cyan']
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            payment_info_frame,
            text="• MTN MoMo: 66562536",
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['cyan']
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            payment_info_frame,
            text="Then enter transaction ID below:",
            font=self.theme.fonts['body'],
            bg=self.theme.colors['surface'],
            fg=self.theme.colors['text']
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Transaction ID entry
        self.transaction_entry = tk.Entry(
            payment_info_frame,
            font=self.theme.fonts['mono'],
            bg=self.theme.colors['bg'],
            fg=self.theme.colors['text'],
            insertbackground=self.theme.colors['text'],
            relief='flat',
            bd=1
        )
        self.transaction_entry.pack(fill='x', padx=10, pady=(5, 10))
        
        # Activate button
        activate_btn = ModernButton(
            payment_frame,
            text="🔑 Activate License",
            style='primary',
            command=self.activate_license
        )
        activate_btn.pack(pady=(10, 0))
        
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
        """Start application with authentication"""
        self.update_status("Initializing...")
        
        # Start device monitoring thread
        threading.Thread(target=self._start_device_monitoring, daemon=True).start()
        
        # Check license
        self._check_license()
    
    def _start_device_monitoring(self):
        """Start device monitoring in background"""
        time.sleep(1)  # Allow UI to load
        
        # Register device with server
        self._register_device()
        
        # Start heartbeat
        self._start_heartbeat()
    
    def _register_device(self):
        """Register device with server"""
        try:
            hostname = platform.node()
            os_info = f"{platform.system()} {platform.release()}"
            
            payload = {
                'device_id': self.device_id,
                'hostname': hostname,
                'os_info': os_info,
                'user_info': {'app_version': '2.0.0'}
            }
            
            response = requests.post(
                f"{self.server_url}/api/device_heartbeat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.root.after(0, self._update_server_status, 'online', 'Connected')
                self.root.after(0, self.update_status, "Device registered with server")
            else:
                self.root.after(0, self._update_server_status, 'offline', 'Server error')
                
        except Exception as e:
            self.root.after(0, self._update_server_status, 'offline', 'No connection')
            self.root.after(0, self.update_status, "Server unavailable")
    
    def _start_heartbeat(self):
        """Start periodic heartbeat"""
        def heartbeat_loop():
            while True:
                try:
                    payload = {
                        'device_id': self.device_id,
                        'hostname': platform.node(),
                        'os_info': f"{platform.system()} {platform.release()}",
                        'user_info': {'app_version': '2.0.0'}
                    }
                    
                    requests.post(
                        f"{self.server_url}/api/device_heartbeat",
                        json=payload,
                        timeout=5
                    )
                    
                except:
                    pass
                
                time.sleep(60)  # Send heartbeat every minute
        
        threading.Thread(target=heartbeat_loop, daemon=True).start()
    
    def _update_server_status(self, status, text):
        """Update server status indicator"""
        self.server_status.set_status(status, text)
        
        if status == 'online':
            self.server_info.delete(1.0, tk.END)
            self.server_info.insert(tk.END, f"Connected to server\n{self.server_url}\nLast check: {datetime.now().strftime('%H:%M:%S')}")
        else:
            self.server_info.delete(1.0, tk.END)
            self.server_info.insert(tk.END, f"Server: {text}\nStatus: Offline\nCheck internet connection")
    
    def _check_license(self):
        """Check license status"""
        try:
            # Try server validation first
            response = requests.post(
                f"{self.server_url}/api/device/validate_license",
                json={'device_id': self.device_id, 'license_key': self._get_local_license_key()},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('valid'):
                    self._update_license_status('active', result.get('expires_at', 'Never'))
                    self.license_data = result
                    self.update_status("License validated - Ready to use")
                    return
        
        except:
            pass
        
        # Fallback to local check
        local_key = self._get_local_license_key()
        if local_key:
            self._update_license_status('pending', 'Local license - Server verification needed')
            self.update_status("Local license found - Waiting for server verification")
        else:
            self._update_license_status('unlicensed', 'No license - Payment required')
            self.update_status("No license - Please make payment to activate")
    
    def _get_local_license_key(self):
        """Get locally stored license key"""
        try:
            license_file = "license.json"
            if os.path.exists(license_file):
                with open(license_file, 'r') as f:
                    data = json.load(f)
                    return data.get('license_key')
        except:
            pass
        return None
    
    def _update_license_status(self, status, details):
        """Update license status"""
        self.license_status.set_status(status, status.replace('_', ' ').title())
        
        self.license_info.delete(1.0, tk.END)
        
        if status == 'active':
            self.license_info.insert(tk.END, f"Status: Active\n")
            self.license_info.insert(tk.END, f"Expires: {details}\n")
            self.license_info.insert(tk.END, f"Device: {self.device_id}\n")
            self.license_info.insert(tk.END, f"Type: Device-locked license")
        elif status == 'pending':
            self.license_info.insert(tk.END, f"Status: Pending verification\n")
            self.license_info.insert(tk.END, f"Device: {self.device_id}\n")
            self.license_info.insert(tk.END, f"Type: Local license\n")
            self.license_info.insert(tk.END, f"Note: Server verification in progress")
        else:
            self.license_info.insert(tk.END, f"Status: Unlicensed\n")
            self.license_info.insert(tk.END, f"Device: {self.device_id}\n")
            self.license_info.insert(tk.END, f"Action: Payment required\n")
            self.license_info.insert(tk.END, f"Price: UGX 10,000 (one-time)")
    
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
        
        if not self.license_data or not self.license_data.get('valid'):
            messagebox.showwarning("License Required", "Please activate your license to use this feature")
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
    
    def activate_license(self):
        """Activate license with transaction ID"""
        transaction_id = self.transaction_entry.get().strip()
        
        if not transaction_id:
            messagebox.showwarning("Invalid Input", "Please enter your transaction ID")
            return
        
        if len(transaction_id) < 4:
            messagebox.showwarning("Invalid Input", "Transaction ID is too short")
            return
        
        # Submit to server for approval
        def submit_thread():
            try:
                payload = {
                    'device_id': self.device_id,
                    'transaction_id': transaction_id,
                    'phone_number': '+256760730254',  # User will provide actual number
                    'amount': '10000',
                    'network': 'airtel',  # Default
                    'notes': f'License request from device {self.device_id}'
                }
                
                response = requests.post(
                    f"{self.server_url}/api/submit_payment",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.root.after(0, messagebox.showinfo, "Payment Submitted", 
                                      "Your payment has been submitted for approval.\n\n"
                                      "You will receive your license key once approved.\n"
                                      "This usually takes a few minutes.")
                        self.root.after(0, self.update_status, "Payment submitted - Waiting for approval")
                    else:
                        self.root.after(0, messagebox.showerror, "Error", result.get('message', 'Unknown error'))
                else:
                    self.root.after(0, messagebox.showerror, "Server Error", "Failed to submit payment")
                    
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Network Error", f"Failed to connect: {e}")
        
        threading.Thread(target=submit_thread, daemon=True).start()
    
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
