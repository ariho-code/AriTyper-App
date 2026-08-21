#!/usr/bin/env python3
"""
AriTyper Simple - Easy to use UI with all features
Simple, clean interface for document typing
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import platform
import socket
import hashlib
import json
import os
from datetime import datetime

# AriTyper is free and unrestricted. There is no activation step, no payment
# gate and no license server to call — the app always runs fully unlocked.
FREE_LICENSE = {
    "valid":      True,
    "plan":       "free",
    "expires_at": "Never",
    "message":    "AriTyper is free — no license required.",
}

class AriTyperSimple:
    """Simple AriTyper with clean, easy-to-use interface"""
    
    def __init__(self, root):
        self.root = root
        self.device_id = self._generate_device_id()
        # AriTyper is free — no license server, no activation, no payment.
        self.license_data = FREE_LICENSE
        self.selected_file = None
        self.is_typing = False
        self.server_url = "http://localhost:5000"
        
        # Setup window
        self.setup_window()
        
        # Create simple UI
        self.create_ui()
        
        # Start app
        self.start_app()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("AriTyper - Document Typing Software")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 400
        y = (self.root.winfo_screenheight() // 2) - 300
        self.root.geometry(f"800x600+{x}+{y}")
    
    def create_ui(self):
        """Create simple, clean UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="🔤 AriTyper",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # Status bar
        status_frame = tk.Frame(header_frame, bg='white')
        status_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="Starting...",
            font=('Arial', 10),
            bg='white',
            fg='#7f8c8d'
        )
        self.status_label.pack(side='left')
        
        self.license_status = tk.Label(
            status_frame,
            text="License: Checking...",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#e74c3c'
        )
        self.license_status.pack(side='right')
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True)
        
        # Left side - File selection
        left_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📄 Select Document",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # File display
        self.file_label = tk.Label(
            left_frame,
            text="No file selected",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#7f8c8d',
            relief='sunken',
            bd=1,
            padx=15,
            pady=15,
            width=40,
            height=3
        )
        self.file_label.pack(padx=20, pady=(0, 15))
        
        # Browse button
        self.browse_btn = tk.Button(
            left_frame,
            text="📁 Browse Files",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.browse_file
        )
        self.browse_btn.pack(padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            left_frame,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(padx=20, pady=(0, 15))
        
        # Right side - License and payment
        right_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="🖥️ Device Info",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # Device info
        device_frame = tk.Frame(right_frame, bg='#ecf0f1')
        device_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(
            device_frame,
            text="Device ID:",
            font=('Arial', 10, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(
            device_frame,
            text=self.device_id,
            font=('Courier', 9),
            bg='#ecf0f1',
            fg='#3498db',
            wraplength=250
        ).pack(anchor='w', padx=10, pady=(0, 10))
        
        # Typing controls
        typing_frame = tk.Frame(right_frame, bg='#ecf0f1')
        typing_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(
            typing_frame,
            text="⌨️ Typing Controls",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Speed control
        speed_frame = tk.Frame(typing_frame, bg='#ecf0f1')
        speed_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        tk.Label(
            speed_frame,
            text="Speed:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=50)
        speed_scale = ttk.Scale(
            speed_frame,
            from_=1,
            to=100,
            variable=self.speed_var,
            orient='horizontal',
            length=150
        )
        speed_scale.pack(side='left', padx=10)
        
        self.speed_label = tk.Label(
            speed_frame,
            text="50%",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#3498db'
        )
        self.speed_label.pack(side='left')
        
        self.speed_var.trace('w', self._update_speed_label)
        
        # Control buttons
        button_frame = tk.Frame(typing_frame, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=(10, 10))
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Typing",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.start_typing
        )
        self.start_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.stop_typing,
            state='disabled'
        )
        self.stop_btn.pack(side='left')
    
    def start_app(self):
        """AriTyper is free — nothing to register, verify or unlock."""
        self.license_data = FREE_LICENSE
        self._update_license_status('active')
        self._enable_typing_controls()
        self.update_status("Ready - AriTyper is free to use")

    def _enable_typing_controls(self):
        """Enable typing controls (always enabled in the free build)."""
        self.start_btn.config(state='normal')

    def _check_license(self):
        """Always licensed — no server call, works fully offline."""
        self.license_data = FREE_LICENSE

    def _get_local_license_key(self):
        return None

    def _update_license_status(self, status='active'):
        """Status pill — the free build is always active."""
        self.license_status.config(text="Free - No License Needed", fg='#27ae60')

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
                    self.root.after(0, self.progress_var.set, progress)
                
                if self.is_typing:
                    self.root.after(0, self.update_status, "Typing completed!")
                    self.root.after(0, self.progress_var.set, 100)
                
            except Exception as e:
                self.root.after(0, self.update_status, f"Typing error: {e}")
        
        threading.Thread(target=typing_thread, daemon=True).start()
    
    def stop_typing(self):
        """Stop typing process"""
        self.is_typing = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Typing stopped")
        self.progress_var.set(0)
    
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
        
        # Combine and hash
        combined = "|".join(identifiers)
        device_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Return first 16 characters as device ID
        return f"ARI-{device_hash[:16].upper()}"

def main():
    """Main entry point"""
    try:
        print("Starting AriTyper Simple...")
        
        root = tk.Tk()
        app = AriTyperSimple(root)
        
        print("AriTyper Simple ready!")
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
