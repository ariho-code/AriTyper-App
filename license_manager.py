"""
License Manager - Device ID generation and license validation
"""
import hashlib
import uuid
import platform
import os
import json
import socket
import re
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

class LicenseManager:
    """Handles device identification and license validation"""
    
    def __init__(self, license_file: str = "license.json"):
        self.license_file = license_file
        self.device_id = self._generate_device_id()
        
    def _generate_device_id(self) -> str:
        """Generate unique device ID from multiple hardware identifiers"""
        identifiers = []
        
        # Get computer name
        try:
            identifiers.append(f"HOST:{socket.gethostname()}")
        except:
            pass
        
        # Get platform info
        identifiers.append(f"OS:{platform.system()}")
        identifiers.append(f"ARCH:{platform.machine()}")
        
        # Get MAC addresses (multiple network interfaces)
        if psutil:
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_LINK:
                            mac = addr.address.replace(':', '').replace('-', '')
                            if len(mac) == 12:  # Valid MAC address
                                identifiers.append(f"MAC:{mac}")
            except:
                pass
        
        # Fallback to single MAC address
        try:
            mac = uuid.getnode()
            identifiers.append(f"MAC:{mac:012x}")
        except:
            pass
        
        # Get processor info
        try:
            processor = platform.processor()
            if processor:
                identifiers.append(f"CPU:{processor}")
        except:
            pass
        
        # Get motherboard serial (Windows)
        if platform.system() == "Windows":
            try:
                # Get motherboard serial
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'SerialNumber'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    serial = result.stdout.strip().split('\n')[-1].strip()
                    if serial and serial != 'SerialNumber':
                        identifiers.append(f"MB:{serial}")
                        
                # Get disk serial
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'SerialNumber'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    serial = result.stdout.strip().split('\n')[-1].strip()
                    if serial and serial != 'SerialNumber':
                        identifiers.append(f"DISK:{serial}")
            except:
                pass
        
        # Get BIOS info (Windows)
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ['wmic', 'bios', 'get', 'SerialNumber'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    serial = result.stdout.strip().split('\n')[-1].strip()
                    if serial and serial != 'SerialNumber':
                        identifiers.append(f"BIOS:{serial}")
            except:
                pass
        
        # Get RAM info for additional uniqueness
        if psutil:
            try:
                memory = psutil.virtual_memory()
                identifiers.append(f"RAM:{memory.total}")
            except:
                pass
        
        # Sort identifiers for consistency
        identifiers.sort()
        
        # Combine and hash
        combined = "|".join(identifiers)
        device_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Return first 16 characters as device ID
        return f"ARI-{device_hash[:16].upper()}"
    
    def get_device_id(self) -> str:
        """Return the device ID"""
        return self.device_id
    
    def save_license(self, license_data: Dict[str, Any]) -> bool:
        """Save license data to file"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False
    
    def load_license(self) -> Optional[Dict[str, Any]]:
        """Load license data from file"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading license: {e}")
        return None
    
    def validate_license(self, license_key: str = None) -> Dict[str, Any]:
        """
        Validate license key or check existing license
        Returns dict with 'valid' boolean and 'message' string
        """
        license_data = self.load_license()
        
        # No license file exists
        if not license_data:
            return {
                'valid': False,
                'message': 'No license found. Please purchase a license.',
                'device_id': self.device_id
            }
        
        # Check if license is active
        if license_data.get('status') != 'active':
            return {
                'valid': False,
                'message': f"License is {license_data.get('status', 'inactive')}",
                'device_id': self.device_id
            }
        
        # Check device ID match (if device locking is enabled)
        if license_data.get('device_lock') and license_data.get('device_id'):
            if license_data['device_id'] != self.device_id:
                return {
                    'valid': False,
                    'message': 'License not valid for this device.',
                    'device_id': self.device_id
                }
        
        # Check expiration
        if license_data.get('expires_at'):
            expires = datetime.fromisoformat(license_data['expires_at'])
            if datetime.now() > expires:
                # Auto-expire
                license_data['status'] = 'expired'
                self.save_license(license_data)
                return {
                    'valid': False,
                    'message': 'License has expired. Please renew.',
                    'device_id': self.device_id
                }
        
        return {
            'valid': True,
            'message': 'License is valid',
            'device_id': self.device_id,
            'license_data': license_data
        }
    
    def activate_license(self, license_key: str, phone_number: str = None) -> Dict[str, Any]:
        """
        Activate license with key (admin approved)
        """
        # In production, this would verify against a server
        # For now, we'll check against approved licenses file
        approved_file = "approved_licenses.json"
        
        try:
            if os.path.exists(approved_file):
                with open(approved_file, 'r') as f:
                    approved = json.load(f)
                
                # Check if license key is approved
                if license_key in approved:
                    license_info = approved[license_key]
                    
                    # Create license data
                    license_data = {
                        'license_key': license_key,
                        'device_id': self.device_id,
                        'device_lock': True,
                        'status': 'active',
                        'phone_number': phone_number,
                        'activated_at': datetime.now().isoformat(),
                        'expires_at': license_info.get('expires_at'),
                        'plan': license_info.get('plan', 'monthly'),
                        'approved_by': license_info.get('approved_by', 'admin')
                    }
                    
                    self.save_license(license_data)
                    
                    return {
                        'success': True,
                        'message': 'License activated successfully!',
                        'expires_at': license_info.get('expires_at')
                    }
                else:
                    return {
                        'success': False,
                        'message': 'License key not found or not approved yet.'
                    }
            else:
                return {
                    'success': False,
                    'message': 'License system not configured. Contact admin.'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error activating license: {str(e)}'
            }
    
    def deactivate_license(self) -> bool:
        """Remove local license (for logout/reset)"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except:
            return False
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information"""
        return self.validate_license()


# Admin functions (for managing licenses)
class AdminLicenseManager:
    """Admin functions for managing user licenses"""
    
    def __init__(self, approved_file: str = "approved_licenses.json"):
        self.approved_file = approved_file
        self._load_approved()
    
    def _load_approved(self):
        """Load approved licenses from file"""
        try:
            if os.path.exists(self.approved_file):
                with open(self.approved_file, 'r') as f:
                    self.approved = json.load(f)
            else:
                self.approved = {}
        except:
            self.approved = {}
    
    def _save_approved(self):
        """Save approved licenses to file"""
        with open(self.approved_file, 'w') as f:
            json.dump(self.approved, f, indent=2)
    
    def generate_license_key(self, plan: str = "monthly", months: int = 1) -> str:
        """Generate a new license key"""
        import random
        import string
        
        # Generate random key
        chars = string.ascii_uppercase + string.digits
        key = ''.join(random.choices(chars, k=12))
        license_key = f"ARI-{key}"
        
        # Calculate expiration
        expires = datetime.now() + timedelta(days=30 * months)
        
        # Store license info
        self.approved[license_key] = {
            'plan': plan,
            'months': months,
            'expires_at': expires.isoformat(),
            'created_at': datetime.now().isoformat(),
            'approved_by': 'admin',
            'status': 'approved'
        }
        
        self._save_approved()
        
        return license_key
    
    def approve_payment(self, phone_number: str, transaction_id: str, 
                       plan: str = "monthly", months: int = 1) -> str:
        """
        Approve a payment and generate license key
        Returns the license key
        """
        license_key = self.generate_license_key(plan, months)
        
        # Store payment info
        payment_file = "payments.json"
        try:
            if os.path.exists(payment_file):
                with open(payment_file, 'r') as f:
                    payments = json.load(f)
            else:
                payments = {}
            
            payments[transaction_id] = {
                'phone_number': phone_number,
                'license_key': license_key,
                'plan': plan,
                'months': months,
                'approved_at': datetime.now().isoformat()
            }
            
            with open(payment_file, 'w') as f:
                json.dump(payments, f, indent=2)
        except:
            pass
        
        return license_key
    
    def cancel_subscription(self, license_key: str, reason: str = "") -> bool:
        """Cancel a user's subscription"""
        if license_key in self.approved:
            self.approved[license_key]['status'] = 'cancelled'
            self.approved[license_key]['cancelled_at'] = datetime.now().isoformat()
            self.approved[license_key]['cancel_reason'] = reason
            self._save_approved()
            return True
        return False
    
    def get_all_licenses(self) -> Dict[str, Any]:
        """Get all license information"""
        return self.approved
    
    def get_pending_payments(self) -> list:
        """Get list of pending payments"""
        payment_file = "payments.json"
        try:
            if os.path.exists(payment_file):
                with open(payment_file, 'r') as f:
                    payments = json.load(f)
                return list(payments.values())
        except:
            pass
        return []


if __name__ == "__main__":
    # Test device ID generation
    lm = LicenseManager()
    print(f"Device ID: {lm.get_device_id()}")
    
    # Test validation
    result = lm.validate_license()
    print(f"License valid: {result}")