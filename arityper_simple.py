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
import requests
from datetime import datetime

class AriTyperSimple:
    """Simple AriTyper with clean, easy-to-use interface"""
    
    def __init__(self, root):
        self.root = root
        self.device_id = self._generate_device_id()
        self.license_data = None
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
            text="🔑 License & Payment",
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
        
        # Payment info
        payment_frame = tk.Frame(right_frame, bg='#ecf0f1')
        payment_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(
            payment_frame,
            text="💳 Payment Required",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#e74c3c'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(
            payment_frame,
            text="Pay UGX 10,000 to:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            payment_frame,
            text="• Airtel Money: 66562536",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#27ae60'
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            payment_frame,
            text="• MTN MoMo: 7074948",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#27ae60'
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            payment_frame,
            text="• Business Name: AT Tech Solutions Uganda",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#3498db'
        ).pack(anchor='w', padx=10, pady=(2, 10))
        
        # Transaction ID entry
        tk.Label(
            payment_frame,
            text="Enter Transaction ID:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.transaction_entry = tk.Entry(
            payment_frame,
            font=('Arial', 11),
            bg='white',
            fg='#2c3e50',
            relief='solid',
            bd=1
        )
        self.transaction_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        # Activate button
        self.activate_btn = tk.Button(
            payment_frame,
            text="🔑 Activate License",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.activate_license
        )
        self.activate_btn.pack(padx=10, pady=(0, 10))
        
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
        """Start application"""
        self.update_status("Initializing...")
        
        # Start device monitoring in background
        threading.Thread(target=self._start_device_monitoring, daemon=True).start()
        
        # Start periodic license checking
        threading.Thread(target=self._start_license_monitoring, daemon=True).start()
        
        # Check license
        self._check_license()
    
    def _start_device_monitoring(self):
        """Start device monitoring"""
        time.sleep(1)  # Allow UI to load
        
        # Register with server
        self._register_device()
        
        # Start heartbeat
        self._start_heartbeat()
    
    def _register_device(self):
        """Register device with server"""
        try:
            payload = {
                'device_id': self.device_id,
                'hostname': platform.node(),
                'os_info': f"{platform.system()} {platform.release()}",
                'user_info': {'app_version': '2.0.0'}
            }
            
            response = requests.post(
                f"{self.server_url}/api/device_heartbeat",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.root.after(0, self.update_status, "Device registered - Connected to server")
            else:
                self.root.after(0, self.update_status, "Server connection failed")
                
        except Exception as e:
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
    
    def _start_license_monitoring(self):
        """Start periodic license checking with auto-unlock"""
        while True:
            try:
                # Check license status from server
                response = requests.post(
                    f"{self.server_url}/api/device/validate_license",
                    json={'device_id': self.device_id, 'license_key': self._get_local_license_key()},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('valid') and not self.license_data:
                        # License was just approved - auto unlock!
                        self.license_data = result
                        self.root.after(0, self._update_license_status, 'active')
                        self.root.after(0, self.update_status, "License approved - App unlocked!")
                        self.root.after(0, self._enable_typing_controls)
                        return
                        
            except:
                pass
            
            time.sleep(30)  # Check every 30 seconds
    
    def _enable_typing_controls(self):
        """Enable typing controls"""
        self.start_btn.config(state='normal')
        self.activate_btn.config(state='disabled')
        self.transaction_entry.config(state='disabled')
    
    def _check_license(self):
        """Check license status"""
        try:
            # Try server validation
            response = requests.post(
                f"{self.server_url}/api/device/validate_license",
                json={'device_id': self.device_id, 'license_key': self._get_local_license_key()},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('valid'):
                    self.license_data = result
                    self.root.after(0, self._update_license_status, 'active')
                    self.root.after(0, self.update_status, "License active - Ready to use")
                    self.root.after(0, self._enable_typing_controls)
                    return
        
        except:
            pass
        
        # Fallback to local check
        local_key = self._get_local_license_key()
        if local_key:
            self.root.after(0, self._update_license_status, 'pending')
            self.root.after(0, self.update_status, "Local license - Waiting for approval...")
        else:
            self.root.after(0, self._update_license_status, 'unlicensed')
            self.root.after(0, self.update_status, "No license - Payment required")
    
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
    
    def _update_license_status(self, status):
        """Update license status"""
        colors = {
            'active': '#27ae60',
            'pending': '#f39c12',
            'unlicensed': '#e74c3c'
        }
        
        texts = {
            'active': 'License: Active',
            'pending': 'License: Pending',
            'unlicensed': 'License: Unlicensed'
        }
        
        self.license_status.config(
            text=texts.get(status, 'License: Unknown'),
            fg=colors.get(status, '#7f8c8d')
        )
    
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
                    'phone_number': '66562536',
                    'amount': '10000',
                    'network': 'airtel',
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
