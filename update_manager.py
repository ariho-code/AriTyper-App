"""
Update Manager - Online update checking and downloading for AriTyper
"""
import json
import urllib.request
import urllib.error
import hashlib
import os
import sys
import subprocess
import tempfile
import threading
from datetime import datetime
from typing import Dict, Optional, Tuple

class UpdateManager:
    """Manages online updates for AriTyper"""
    
    def __init__(self, current_version: str = "1.0.0"):
        self.current_version = current_version
        self.update_server_url = "https://arityper.ug/updates"  # Your update server
        self.update_info_file = "update_info.json"
        self.temp_dir = tempfile.gettempdir()
        
    def check_for_updates(self, show_no_update_msg: bool = True) -> Dict:
        """
        Check for available updates online
        Returns dict with update information
        """
        try:
            # In production, this would fetch from your server
            # For now, we'll simulate with a local check
            update_info = self._fetch_update_info()
            
            if not update_info:
                return {
                    'has_update': False,
                    'message': 'Unable to check for updates',
                    'error': True
                }
            
            latest_version = update_info.get('version', '1.0.0')
            
            if self._is_newer_version(latest_version, self.current_version):
                return {
                    'has_update': True,
                    'latest_version': latest_version,
                    'current_version': self.current_version,
                    'download_url': update_info.get('download_url', ''),
                    'release_notes': update_info.get('release_notes', ''),
                    'file_size': update_info.get('file_size', 0),
                    'checksum': update_info.get('checksum', ''),
                    'mandatory': update_info.get('mandatory', False)
                }
            else:
                result = {
                    'has_update': False,
                    'message': 'You have the latest version',
                    'current_version': self.current_version
                }
                
                if show_no_update_msg:
                    result['message'] = f"You are running the latest version ({self.current_version})"
                
                return result
                
        except Exception as e:
            return {
                'has_update': False,
                'message': f'Error checking for updates: {str(e)}',
                'error': True
            }
    
    def _fetch_update_info(self) -> Optional[Dict]:
        """Fetch update information from server"""
        try:
            # For demo purposes, return simulated update info
            # In production, this would be an HTTP request to your server
            return {
                'version': '1.1.0',
                'download_url': 'https://arityper.ug/downloads/AriTyper-1.1.0.exe',
                'release_notes': '''
                    <h5>What's new in v1.1.0:</h5>
                    <ul>
                        <li>Improved PDF text extraction accuracy</li>
                        <li>Better format preservation for Word documents</li>
                        <li>Enhanced typing speed control</li>
                        <li>Bug fixes and performance improvements</li>
                        <li>Updated payment integration for Uganda</li>
                    </ul>
                ''',
                'file_size': 26214400,  # ~25MB
                'checksum': 'sha256:abc123...',  # Would be actual checksum
                'mandatory': False,
                'release_date': '2024-01-15'
            }
            
            # Production code would be:
            # url = f"{self.update_server_url}/version.json"
            # with urllib.request.urlopen(url, timeout=10) as response:
            #     return json.loads(response.read().decode())
            
        except Exception as e:
            print(f"Error fetching update info: {e}")
            return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, update_info: Dict, progress_callback=None) -> Tuple[bool, str]:
        """
        Download update file
        Returns (success, file_path_or_error_message)
        """
        try:
            download_url = update_info.get('download_url', '')
            if not download_url:
                return False, "No download URL available"
            
            # Generate temporary file path
            filename = f"AriTyper-{update_info['latest_version']}.exe"
            temp_file_path = os.path.join(self.temp_dir, filename)
            
            # Download with progress tracking
            def progress_hook(transferred, total):
                if progress_callback and total > 0:
                    percent = (transferred / total) * 100
                    progress_callback(percent, transferred, total)
            
            success, message = self._download_file(download_url, temp_file_path, progress_hook)
            
            if success:
                # Verify checksum if provided
                if update_info.get('checksum'):
                    if not self._verify_checksum(temp_file_path, update_info['checksum']):
                        os.remove(temp_file_path)
                        return False, "Downloaded file verification failed"
                
                return True, temp_file_path
            else:
                return False, message
                
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def _download_file(self, url: str, file_path: str, progress_callback=None) -> Tuple[bool, str]:
        """Download file with progress tracking"""
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
                
                return True, "Download completed successfully"
                
        except urllib.error.URLError as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Download error: {str(e)}"
    
    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            if expected_checksum.startswith('sha256:'):
                expected = expected_checksum.split(':')[1]
                hash_obj = hashlib.sha256()
            elif expected_checksum.startswith('md5:'):
                expected = expected_checksum.split(':')[1]
                hash_obj = hashlib.md5()
            else:
                return True  # Skip verification if format not recognized
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            actual = hash_obj.hexdigest()
            return actual.lower() == expected.lower()
            
        except Exception as e:
            print(f"Checksum verification error: {e}")
            return False
    
    def install_update(self, installer_path: str) -> bool:
        """
        Launch the installer and exit current application
        """
        try:
            # Create a batch file to run the installer
            batch_file = os.path.join(self.temp_dir, "update_arityper.bat")
            
            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'echo Updating AriTyper...\n')
                f.write(f'timeout /t 2 /nobreak >nul\n')
                f.write(f'start "" "{installer_path}"\n')
                f.write(f'del "{batch_file}"\n')
            
            # Launch the batch file
            subprocess.Popen(batch_file, shell=True)
            
            # Exit current application
            sys.exit(0)
            
            return True
            
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def get_update_info_display(self, update_info: Dict) -> str:
        """Format update information for display"""
        if not update_info.get('has_update'):
            return update_info.get('message', 'No update information available')
        
        current = update_info.get('current_version', 'Unknown')
        latest = update_info.get('latest_version', 'Unknown')
        size_mb = update_info.get('file_size', 0) / (1024 * 1024)
        release_notes = update_info.get('release_notes', 'No release notes available')
        mandatory = update_info.get('mandatory', False)
        
        urgency = "Mandatory" if mandatory else "Optional"
        
        display_text = f"""
        <div class='update-info'>
            <h4>Update Available! ({urgency})</h4>
            <p><strong>Current Version:</strong> {current}</p>
            <p><strong>Latest Version:</strong> {latest}</p>
            <p><strong>Download Size:</strong> {size_mb:.1f} MB</p>
            
            <div class='release-notes'>
                <h5>Release Notes:</h5>
                {release_notes}
            </div>
            
            <p class='update-notice'>
                {'This is a mandatory update. You must update to continue using AriTyper.' if mandatory 
                 else 'It is recommended to install this update for the best experience.'}
            </p>
        </div>
        """
        
        return display_text


class UpdateDialog:
    """Update dialog for user interaction"""
    
    def __init__(self, parent, update_manager: UpdateManager):
        self.parent = parent
        self.update_manager = update_manager
        self.update_info = None
        self.installer_path = None
        
    def show_update_dialog(self, update_info: Dict):
        """Show update dialog to user"""
        self.update_info = update_info
        
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("AriTyper - Update Available")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='#1a1a2e')
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.setup_dialog_ui()
        
    def setup_dialog_ui(self):
        import tkinter as tk
        from tkinter import ttk
        
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title = tk.Label(
            header_frame,
            text="🔄 Update Available",
            font=("Arial", 18, "bold"),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        title.pack()
        
        # Update info
        info_frame = tk.Frame(self.dialog, bg='#16213e', padx=20, pady=15)
        info_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create text widget for release notes
        text_widget = tk.Text(
            info_frame,
            wrap='word',
            font=("Arial", 10),
            bg='#16213e',
            fg='#ffffff',
            padx=15,
            pady=15,
            relief='flat',
            height=15
        )
        text_widget.pack(fill='both', expand=True)
        
        # Insert update information
        update_text = self.update_manager.get_update_info_display(self.update_info)
        text_widget.insert('1.0', update_text)
        text_widget.config(state='disabled')
        
        # Progress bar (initially hidden)
        self.progress_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        
        self.status_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        button_frame.pack(fill='x', padx=20, pady=20)
        
        self.update_button = tk.Button(
            button_frame,
            text="📥 Download Update",
            command=self.start_update,
            bg='#00ff88',
            fg='#1a1a2e',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.update_button.pack(side='left', padx=5)
        
        skip_button = tk.Button(
            button_frame,
            text="Skip",
            command=self.skip_update,
            bg='#555555',
            fg='white',
            font=("Arial", 11),
            padx=20,
            pady=10
        )
        skip_button.pack(side='right', padx=5)
        
        # If mandatory update, disable skip button
        if self.update_info.get('mandatory', False):
            skip_button.config(state='disabled', text="Cannot Skip (Mandatory)")
    
    def start_update(self):
        """Start the update download process"""
        self.update_button.config(state='disabled', text="Downloading...")
        
        # Show progress frame
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        self.status_label.pack(pady=5)
        self.progress_bar.pack()
        
        # Start download in separate thread
        threading.Thread(
            target=self._download_update_thread,
            daemon=True
        ).start()
    
    def _download_update_thread(self):
        """Download update in background thread"""
        def progress_callback(percent, transferred, total):
            # Update UI in main thread
            self.dialog.after(0, self._update_progress, percent, transferred, total)
        
        success, result = self.update_manager.download_update(
            self.update_info,
            progress_callback
        )
        
        # Handle result in main thread
        self.dialog.after(0, self._download_complete, success, result)
    
    def _update_progress(self, percent, transferred, total):
        """Update progress bar"""
        self.progress_var.set(percent)
        
        if total > 0:
            transferred_mb = transferred / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.status_label.config(
                text=f"Downloading... {transferred_mb:.1f} MB / {total_mb:.1f} MB"
            )
        else:
            self.status_label.config(text="Downloading...")
    
    def _download_complete(self, success, result):
        """Handle download completion"""
        if success:
            self.installer_path = result
            self.status_label.config(text="Download complete! Ready to install.")
            self.update_button.config(
                state='normal',
                text="🚀 Install Now",
                command=self.install_update
            )
        else:
            self.status_label.config(text=f"Download failed: {result}")
            self.update_button.config(
                state='normal',
                text="🔄 Retry Download",
                command=self.start_update
            )
    
    def install_update(self):
        """Install the update"""
        if self.installer_path and os.path.exists(self.installer_path):
            from tkinter import messagebox
            
            response = messagebox.askyesno(
                "Install Update",
                "AriTyper will close and the installer will launch.\n\n"
                "Do you want to continue with the installation?"
            )
            
            if response:
                self.status_label.config(text="Launching installer...")
                self.update_manager.install_update(self.installer_path)
    
    def skip_update(self):
        """Skip the update"""
        if not self.update_info.get('mandatory', False):
            self.dialog.destroy()


if __name__ == "__main__":
    # Test update manager
    um = UpdateManager()
    update_info = um.check_for_updates()
    print("Update check result:", update_info)
