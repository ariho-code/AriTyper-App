"""
AriTyper Device Client - Communication with server
"""
import json
import requests
import threading
import time
from datetime import datetime
from typing import Dict, Optional
import platform
import socket

class DeviceClient:
    """Client for communicating with AriTyper server"""
    
    def __init__(self, server_url: str = "http://localhost:5000", device_id: str = None):
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.is_registered = False
        self.heartbeat_thread = None
        self.heartbeat_running = False
        
    def register_device(self, device_id: str, user_info: Dict = None) -> bool:
        """Register this device with the server"""
        try:
            self.device_id = device_id
            
            # Get device information
            hostname = socket.gethostname()
            os_info = f"{platform.system()} {platform.release()}"
            ip_address = self._get_local_ip()
            
            payload = {
                'device_id': device_id,
                'hostname': hostname,
                'os_info': os_info,
                'user_info': user_info or {}
            }
            
            response = requests.post(
                f"{self.server_url}/api/device/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.is_registered = True
                    print(f"✅ Device registered with server: {hostname}")
                    return True
                else:
                    print(f"❌ Registration failed: {result.get('error')}")
                    return False
            else:
                print(f"❌ Server error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during registration: {e}")
            return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def validate_license_server(self, license_key: str) -> Dict:
        """Validate license with server"""
        try:
            if not self.is_registered:
                return {'valid': False, 'message': 'Device not registered'}
            
            payload = {
                'device_id': self.device_id,
                'license_key': license_key
            }
            
            response = requests.post(
                f"{self.server_url}/api/device/validate_license",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {'valid': False, 'message': f'Server error: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'valid': False, 'message': f'Network error: {e}'}
        except Exception as e:
            return {'valid': False, 'message': f'Validation error: {e}'}
    
    def send_heartbeat(self, status: str = 'active') -> bool:
        """Send heartbeat to server"""
        try:
            if not self.is_registered:
                return False
            
            payload = {
                'device_id': self.device_id,
                'status': status
            }
            
            response = requests.post(
                f"{self.server_url}/api/device/heartbeat",
                json=payload,
                timeout=5
            )
            
            return response.status_code == 200
            
        except:
            return False
    
    def start_heartbeat(self, interval: int = 60):
        """Start sending periodic heartbeats"""
        if self.heartbeat_running:
            return
        
        self.heartbeat_running = True
        
        def heartbeat_loop():
            while self.heartbeat_running:
                try:
                    if self.send_heartbeat():
                        print("💓 Heartbeat sent successfully")
                    else:
                        print("💓 Heartbeat failed")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"💓 Heartbeat error: {e}")
                    time.sleep(interval)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        print(f"💓 Heartbeat started (interval: {interval}s)")
    
    def stop_heartbeat(self):
        """Stop heartbeat thread"""
        self.heartbeat_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        print("💓 Heartbeat stopped")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Create a socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    def check_server_status(self) -> bool:
        """Check if server is reachable"""
        try:
            response = requests.get(f"{self.server_url}/api/admin/stats", timeout=5)
            return response.status_code == 200
        except:
            return False


class EnhancedLicenseManager:
    """Enhanced license manager with server communication"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        from license_manager import LicenseManager
        self.local_manager = LicenseManager()
        self.client = DeviceClient(server_url)
        self.server_url = server_url
        
    def validate_license_hybrid(self, license_key: str = None) -> Dict:
        """Validate license with fallback to local validation"""
        # First try server validation
        if self.client.check_server_status():
            server_result = self.client.validate_license_server(license_key)
            if server_result.get('valid'):
                # Server validation successful, update local license
                return server_result
        
        # Fallback to local validation
        return self.local_manager.validate_license(license_key)
    
    def activate_license_hybrid(self, license_key: str, phone_number: str = None) -> Dict:
        """Activate license with server registration"""
        # Register device first
        device_id = self.local_manager.get_device_id()
        user_info = {'phone_number': phone_number} if phone_number else {}
        
        if self.client.register_device(device_id, user_info):
            # Try server activation
            server_result = self.client.validate_license_server(license_key)
            if server_result.get('valid'):
                # Server activation successful, activate locally too
                local_result = self.local_manager.activate_license(license_key, phone_number)
                return local_result
        
        # Fallback to local activation
        return self.local_manager.activate_license(license_key, phone_number)
    
    def start_monitoring(self):
        """Start device monitoring"""
        device_id = self.local_manager.get_device_id()
        
        # Register device
        if self.client.register_device(device_id):
            # Start heartbeat
            self.client.start_heartbeat()
            return True
        return False
    
    def stop_monitoring(self):
        """Stop device monitoring"""
        self.client.stop_heartbeat()
