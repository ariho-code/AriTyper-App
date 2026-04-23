"""
AriTyper Server API - Multi-device communication and management
"""
import json
import sqlite3
import hashlib
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

# Database setup
DB_FILE = "arityper_server.db"

def init_database():
    """Initialize the server database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            device_id TEXT UNIQUE,
            hostname TEXT,
            os_info TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'active',
            license_key TEXT,
            license_status TEXT,
            ip_address TEXT,
            user_info TEXT
        )
    ''')
    
    # Licenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_key TEXT PRIMARY KEY,
            device_id TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP,
            expires_at TIMESTAMP,
            plan TEXT,
            payment_info TEXT,
            approved_by TEXT
        )
    ''')
    
    # Activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            action TEXT,
            timestamp TIMESTAMP,
            details TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_activity(device_id, action, details=None):
    """Log device activity"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_log (device_id, action, timestamp, details)
        VALUES (?, ?, ?, ?)
    ''', (device_id, action, datetime.now(), json.dumps(details) if details else None))
    conn.commit()
    conn.close()

@app.route('/api/device/register', methods=['POST'])
def register_device():
    """Register a new device"""
    try:
        data = request.json
        device_id = data.get('device_id')
        hostname = data.get('hostname', 'Unknown')
        os_info = data.get('os_info', 'Unknown')
        ip_address = request.remote_addr
        user_info = data.get('user_info', {})
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if device already exists
        cursor.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update last seen
            cursor.execute('''
                UPDATE devices 
                SET last_seen = ?, ip_address = ?, user_info = ?
                WHERE device_id = ?
            ''', (datetime.now(), ip_address, json.dumps(user_info), device_id))
            message = "Device updated"
        else:
            # Register new device
            cursor.execute('''
                INSERT INTO devices 
                (id, device_id, hostname, os_info, first_seen, last_seen, ip_address, user_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), device_id, hostname, os_info, 
                  datetime.now(), datetime.now(), ip_address, json.dumps(user_info)))
            message = "Device registered"
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(device_id, 'register', {'hostname': hostname, 'ip': ip_address})
        
        return jsonify({
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device/heartbeat', methods=['POST'])
def device_heartbeat():
    """Receive heartbeat from device"""
    try:
        data = request.json
        device_id = data.get('device_id')
        status = data.get('status', 'active')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE devices 
            SET last_seen = ?, status = ?
            WHERE device_id = ?
        ''', (datetime.now(), status, device_id))
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(device_id, 'heartbeat', {'status': status})
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device/validate_license', methods=['POST'])
def validate_license():
    """Validate license for a device"""
    try:
        data = request.json
        device_id = data.get('device_id')
        license_key = data.get('license_key')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check license
        cursor.execute('''
            SELECT * FROM licenses 
            WHERE license_key = ? AND device_id = ?
        ''', (license_key, device_id))
        
        license_data = cursor.fetchone()
        
        if license_data:
            # Check expiration
            expires_at = license_data[4]
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                # License expired
                cursor.execute('''
                    UPDATE licenses SET status = 'expired' WHERE license_key = ?
                ''', (license_key,))
                conn.commit()
                conn.close()
                
                log_activity(device_id, 'license_check_failed', {'reason': 'expired'})
                
                return jsonify({
                    'valid': False,
                    'message': 'License has expired'
                })
            
            # License valid
            cursor.execute('''
                UPDATE devices 
                SET license_key = ?, license_status = 'active'
                WHERE device_id = ?
            ''', (license_key, device_id))
            conn.commit()
            conn.close()
            
            log_activity(device_id, 'license_check_success')
            
            return jsonify({
                'valid': True,
                'message': 'License is valid',
                'expires_at': expires_at
            })
        else:
            conn.close()
            log_activity(device_id, 'license_check_failed', {'reason': 'not_found'})
            
            return jsonify({
                'valid': False,
                'message': 'License not found or invalid for this device'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/devices', methods=['GET'])
def get_devices():
    """Get all registered devices (admin only)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_id, hostname, os_info, first_seen, last_seen, 
                   status, license_key, license_status, ip_address
            FROM devices 
            ORDER BY last_seen DESC
        ''')
        
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'device_id': row[0],
                'hostname': row[1],
                'os_info': row[2],
                'first_seen': row[3],
                'last_seen': row[4],
                'status': row[5],
                'license_key': row[6],
                'license_status': row[7],
                'ip_address': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/device/<device_id>/deactivate', methods=['POST'])
def deactivate_device(device_id):
    """Deactivate a device (admin only)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Update device status
        cursor.execute('''
            UPDATE devices 
            SET status = 'deactivated', license_status = 'inactive'
            WHERE device_id = ?
        ''', (device_id,))
        
        # Update license status
        cursor.execute('''
            UPDATE licenses 
            SET status = 'deactivated'
            WHERE device_id = ?
        ''', (device_id,))
        
        conn.commit()
        conn.close()
        
        log_activity(device_id, 'device_deactivated', {'admin': True})
        
        return jsonify({
            'success': True,
            'message': 'Device deactivated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/activity', methods=['GET'])
def get_activity():
    """Get recent activity log (admin only)"""
    try:
        limit = request.args.get('limit', 50)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_id, action, timestamp, details
            FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'device_id': row[0],
                'action': row[1],
                'timestamp': row[2],
                'details': json.loads(row[3]) if row[3] else None
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """Get system statistics (admin only)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Device stats
        cursor.execute('SELECT COUNT(*) FROM devices')
        total_devices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM devices WHERE status = "active"')
        active_devices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM devices WHERE license_status = "active"')
        licensed_devices = cursor.fetchone()[0]
        
        # License stats
        cursor.execute('SELECT COUNT(*) FROM licenses')
        total_licenses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = "active"')
        active_licenses = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_devices': total_devices,
                'active_devices': active_devices,
                'licensed_devices': licensed_devices,
                'total_licenses': total_licenses,
                'active_licenses': active_licenses
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    print("🚀 AriTyper Server API starting...")
    print("📊 Database initialized")
    print("🌐 Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
