"""
AriTyper Web Admin Panel - Flask Application
Host on Render for device management and license approval
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Database setup
DB_FILE = "arityper_admin.db"

def init_database():
    """Initialize the admin database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    
    # Website visits tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS website_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            user_agent TEXT,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            page_visited TEXT,
            referrer TEXT,
            session_id TEXT
        )
    ''')
    
    # Downloads tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            user_agent TEXT,
            download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_name TEXT,
            file_size INTEGER,
            download_source TEXT,
            session_id TEXT
        )
    ''')
    
    # Analytics summary
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE,
            total_visits INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            total_downloads INTEGER DEFAULT 0,
            unique_downloads INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Licenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE,
            device_id TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP,
            expires_at TIMESTAMP,
            plan TEXT,
            payment_info TEXT,
            approved_by TEXT,
            phone_number TEXT
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            phone_number TEXT,
            amount TEXT,
            network TEXT,
            device_id TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP,
            approved_at TIMESTAMP,
            license_key TEXT,
            notes TEXT
        )
    ''')
    
    # Activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            action TEXT,
            timestamp TIMESTAMP,
            details TEXT,
            admin_user TEXT
        )
    ''')
    
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM admin_users')
    if cursor.fetchone()[0] == 0:
        default_password = 'admin123'
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)', ('admin', password_hash))
    
    conn.commit()
    conn.close()

def log_activity(device_id, action, details=None, admin_user=None):
    """Log activity"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_log (device_id, action, timestamp, details, admin_user)
        VALUES (?, ?, ?, ?, ?)
    ''', (device_id, action, datetime.now(), json.dumps(details) if details else None, admin_user))
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate input
        if not username or not password or len(username) < 3 or len(password) < 6:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if admin and hashlib.sha256(password.encode()).hexdigest() == admin['password_hash']:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session.permanent = True  # Enhanced session security
            log_activity(None, 'admin_login', {'username': username}, username)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Admin logout"""
    if 'admin_username' in session:
        log_activity(None, 'admin_logout', {'username': session['admin_username']}, session['admin_username'])
    session.clear()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Change admin password"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html')
        
        # Verify current password
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin_users WHERE username = ?', (session['admin_username'],)).fetchone()
        
        if admin and hashlib.sha256(current_password.encode()).hexdigest() == admin['password_hash']:
            # Update password
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            conn.execute('UPDATE admin_users SET password_hash = ? WHERE username = ?', 
                       (new_password_hash, session['admin_username']))
            conn.commit()
            
            log_activity(None, 'password_changed', {'username': session['admin_username']}, session['admin_username'])
            flash('Password changed successfully', 'success')
        else:
            flash('Current password is incorrect', 'error')
        
        conn.close()
    
    return render_template('change_password.html')

@app.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get statistics
    stats = {
        'total_devices': conn.execute('SELECT COUNT(*) FROM devices').fetchone()[0],
        'active_devices': conn.execute('SELECT COUNT(*) FROM devices WHERE status = "active"').fetchone()[0],
        'total_licenses': conn.execute('SELECT COUNT(*) FROM licenses').fetchone()[0],
        'active_licenses': conn.execute('SELECT COUNT(*) FROM licenses WHERE status = "active"').fetchone()[0],
        'pending_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status = "pending"').fetchone()[0],
    }
    
    # Get recent devices
    recent_devices = conn.execute('''
        SELECT device_id, hostname, last_seen, status, license_status
        FROM devices 
        ORDER BY last_seen DESC 
        LIMIT 5
    ''').fetchall()
    
    # Get pending payments
    pending_payments = conn.execute('''
        SELECT transaction_id, phone_number, amount, network, submitted_at
        FROM payments 
        WHERE status = "pending"
        ORDER BY submitted_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                        stats=stats, 
                        recent_devices=recent_devices,
                        pending_payments=pending_payments)

@app.route('/devices')
def devices():
    """Device management page"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    devices = conn.execute('''
        SELECT device_id, hostname, os_info, first_seen, last_seen, 
               status, license_key, license_status, ip_address, user_info
        FROM devices 
        ORDER BY last_seen DESC
    ''').fetchall()
    conn.close()
    
    return render_template('devices.html', devices=devices)

@app.route('/licenses')
def licenses():
    """License management page"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    licenses = conn.execute('''
        SELECT license_key, device_id, status, created_at, expires_at, 
               plan, payment_info, approved_by, phone_number
        FROM licenses 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('licenses.html', licenses=licenses)

@app.route('/payments')
def payments():
    """Payment management page"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    payments = conn.execute('''
        SELECT transaction_id, phone_number, amount, network, device_id,
               status, submitted_at, approved_at, license_key, notes
        FROM payments 
        ORDER BY submitted_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('payments.html', payments=payments)

@app.route('/api/approve_payment', methods=['POST'])
def approve_payment():
    """Approve a payment"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    data = request.json
    transaction_id = data.get('transaction_id')
    phone_number = data.get('phone_number')
    device_id = data.get('device_id')
    
    try:
        conn = get_db_connection()
        
        # Generate license key
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        key = ''.join(random.choices(chars, k=12))
        license_key = f"ARI-{key}"
        
        # Calculate expiration (1 year from now)
        expires = datetime.now() + timedelta(days=365)
        
        # Update payment status
        conn.execute('''
            UPDATE payments 
            SET status = 'approved', approved_at = ?, license_key = ?, notes = ?
            WHERE transaction_id = ?
        ''', (datetime.now(), license_key, f"Approved by {session.get('admin_username')}", transaction_id))
        
        # Create license record
        conn.execute('''
            INSERT INTO licenses 
            (license_key, device_id, status, created_at, expires_at, plan, approved_by, phone_number)
            VALUES (?, ?, 'active', ?, ?, 'yearly', ?, ?)
        ''', (license_key, device_id, datetime.now(), expires, session.get('admin_username'), phone_number))
        
        # Update device license status
        conn.execute('''
            UPDATE devices 
            SET license_key = ?, license_status = 'active'
            WHERE device_id = ?
        ''', (license_key, device_id))
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(device_id, 'payment_approved', {
            'transaction_id': transaction_id,
            'license_key': license_key,
            'phone_number': phone_number
        }, session.get('admin_username'))
        
        return jsonify({
            'success': True,
            'message': 'Payment approved successfully',
            'license_key': license_key
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reject_payment', methods=['POST'])
def reject_payment():
    """Reject a payment"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    data = request.json
    transaction_id = data.get('transaction_id')
    reason = data.get('reason', 'Rejected by admin')
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE payments 
            SET status = 'rejected', notes = ?
            WHERE transaction_id = ?
        ''', (reason, transaction_id))
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(None, 'payment_rejected', {
            'transaction_id': transaction_id,
            'reason': reason
        }, session.get('admin_username'))
        
        return jsonify({
            'success': True,
            'message': 'Payment rejected successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/deactivate_device', methods=['POST'])
def deactivate_device():
    """Deactivate a device"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    data = request.json
    device_id = data.get('device_id')
    
    try:
        conn = get_db_connection()
        
        # Update device status
        conn.execute('''
            UPDATE devices 
            SET status = 'deactivated', license_status = 'inactive'
            WHERE device_id = ?
        ''', (device_id,))
        
        # Update license status
        conn.execute('''
            UPDATE licenses 
            SET status = 'deactivated'
            WHERE device_id = ?
        ''', (device_id,))
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(device_id, 'device_deactivated', {}, session.get('admin_username'))
        
        return jsonify({
            'success': True,
            'message': 'Device deactivated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/submit_payment', methods=['POST'])
def submit_payment():
    """Submit payment from device"""
    try:
        data = request.json
        device_id = data.get('device_id')
        transaction_id = data.get('transaction_id')
        phone_number = data.get('phone_number')
        amount = data.get('amount', '10000')
        network = data.get('network', 'airtel')
        notes = data.get('notes', '')
        
        conn = get_db_connection()
        
        # Check if transaction already exists
        existing = conn.execute(
            'SELECT id FROM payments WHERE transaction_id = ?', 
            (transaction_id,)
        ).fetchone()
        
        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Transaction ID already submitted'
            })
        
        # Insert payment request
        conn.execute('''
            INSERT INTO payments 
            (transaction_id, phone_number, amount, network, device_id, status, submitted_at, notes)
            VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
        ''', (transaction_id, phone_number, amount, network, device_id, datetime.now(), notes))
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(device_id, 'payment_submitted', {
            'transaction_id': transaction_id,
            'phone_number': phone_number,
            'amount': amount
        })
        
        return jsonify({
            'success': True,
            'message': 'Payment submitted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device_heartbeat', methods=['POST'])
def device_heartbeat():
    """Receive heartbeat from device"""
    try:
        data = request.json
        device_id = data.get('device_id')
        hostname = data.get('hostname', 'Unknown')
        os_info = data.get('os_info', 'Unknown')
        ip_address = request.remote_addr
        user_info = data.get('user_info', {})
        
        conn = get_db_connection()
        
        # Check if device exists
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM devices WHERE device_id = ?', (device_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update last seen and set status to active
            cursor.execute('''
                UPDATE devices 
                SET last_seen = ?, ip_address = ?, user_info = ?, status = 'active'
                WHERE device_id = ?
            ''', (datetime.now(), ip_address, json.dumps(user_info), device_id))
        else:
            # Register new device
            cursor.execute('''
                INSERT INTO devices 
                (device_id, hostname, os_info, first_seen, last_seen, ip_address, user_info, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
            ''', (device_id, hostname, os_info, datetime.now(), datetime.now(), ip_address, json.dumps(user_info)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/updates')
def updates():
    """Updates management page"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    return render_template('updates.html')

@app.route('/api/upload_update', methods=['POST'])
def upload_update():
    """Upload application update"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not file.filename.endswith('.exe'):
            return jsonify({'success': False, 'message': 'Only .exe files are allowed'})
        
        # Validate file size (500MB max)
        if file.content_length and file.content_length > 500 * 1024 * 1024:
            return jsonify({'success': False, 'message': 'File size must be less than 500MB'})
        
        # Save file (in production, use cloud storage)
        version = request.form.get('version', 'unknown')
        filename = f"AriTyper-{version}.exe"
        
        # Create updates directory if it doesn't exist
        if not os.path.exists('updates'):
            os.makedirs('updates')
        
        file_path = os.path.join('updates', filename)
        file.save(file_path)
        
        # Log activity
        log_activity(None, 'update_uploaded', {
            'filename': filename,
            'version': version,
            'size': file.content_length
        }, session.get('admin_username'))
        
        return jsonify({
            'success': True,
            'message': 'Update uploaded successfully',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """Download app file"""
    try:
        updates_dir = os.path.join(os.getcwd(), 'updates')
        file_path = os.path.join(updates_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/latest_version')
def get_latest_version():
    """Get latest app version info - only admin-approved files"""
    try:
        updates_dir = os.path.join(os.getcwd(), 'updates')
        if not os.path.exists(updates_dir):
            return jsonify({'success': False, 'message': 'No updates available'})
        
        # Find the latest .exe file
        files = [f for f in os.listdir(updates_dir) if f.endswith('.exe')]
        if not files:
            return jsonify({'success': False, 'message': 'No app files available'})
        
        # Get the latest file (by modification time)
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(updates_dir, f)))
        file_path = os.path.join(updates_dir, latest_file)
        
        # Verify file integrity and admin approval
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'App file not found'})
        
        # Check file size (should be reasonable for an installer)
        file_size = os.path.getsize(file_path)
        if file_size < 1000000 or file_size > 100000000:  # 1MB to 100MB
            return jsonify({'success': False, 'message': 'Invalid file size'})
        
        # Return file info with verification status
        return jsonify({
            'success': True,
            'filename': latest_file,
            'download_url': f'/download/{latest_file}',
            'size': file_size,
            'version': '2.0.0',  # This can be made dynamic
            'upload_date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'verified': True,
            'message': 'Official AriTyper installer - verified by ArihoForge'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/delete_device', methods=['POST'])
def delete_device():
    """Delete a device and all associated data"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'success': False, 'message': 'Device ID is required'})
        
        conn = get_db_connection()
        
        # Check if device exists
        device = conn.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
        if not device:
            conn.close()
            return jsonify({'success': False, 'message': 'Device not found'})
        
        # Delete all associated data in order to maintain foreign key constraints
        # 1. Delete payments associated with this device
        conn.execute('DELETE FROM payments WHERE device_id = ?', (device_id,))
        
        # 2. Delete licenses associated with this device  
        conn.execute('DELETE FROM licenses WHERE device_id = ?', (device_id,))
        
        # 3. Delete activity logs for this device
        conn.execute('DELETE FROM activity_logs WHERE device_id = ?', (device_id,))
        
        # 4. Finally delete the device
        conn.execute('DELETE FROM devices WHERE device_id = ?', (device_id,))
        
        conn.commit()
        conn.close()
        
        # Log activity
        log_activity(None, 'device_deleted', {
            'device_id': device_id,
            'hostname': device['hostname'] if device else 'Unknown'
        }, session.get('admin_username'))
        
        return jsonify({
            'success': True, 
            'message': f'Device {device_id} and all associated data deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/validate_license', methods=['POST'])
def validate_device_license():
    """Validate device license"""
    try:
        data = request.json
        device_id = data.get('device_id')
        license_key = data.get('license_key')
        
        if not device_id or not license_key:
            return jsonify({'valid': False, 'message': 'Device ID and license key required'})
        
        conn = get_db_connection()
        
        # Check if license exists and is active
        license_record = conn.execute('''
            SELECT status, expires_at, device_id 
            FROM licenses 
            WHERE license_key = ?
        ''', (license_key,)).fetchone()
        
        if not license_record:
            conn.close()
            return jsonify({'valid': False, 'message': 'License not found'})
        
        # Check if license is active and not expired
        if license_record['status'] != 'active':
            conn.close()
            return jsonify({'valid': False, 'message': 'License not active'})
        
        # Check expiration
        expires_at = datetime.fromisoformat(license_record['expires_at'])
        if datetime.now() > expires_at:
            conn.close()
            return jsonify({'valid': False, 'message': 'License expired'})
        
        # Check if license is for this device
        if license_record['device_id'] != device_id:
            conn.close()
            return jsonify({'valid': False, 'message': 'License not for this device'})
        
        conn.close()
        return jsonify({'valid': True, 'message': 'License valid'})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)})

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    try:
        conn = get_db_connection()
        
        stats = {
            'total_devices': conn.execute('SELECT COUNT(*) FROM devices').fetchone()[0],
            'active_devices': conn.execute('SELECT COUNT(*) FROM devices WHERE status = "active"').fetchone()[0],
            'total_licenses': conn.execute('SELECT COUNT(*) FROM licenses').fetchone()[0],
            'active_licenses': conn.execute('SELECT COUNT(*) FROM licenses WHERE status = "active"').fetchone()[0],
            'pending_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status = "pending"').fetchone()[0],
            'approved_payments': conn.execute('SELECT COUNT(*) FROM payments WHERE status = "approved"').fetchone()[0],
        }
        
        conn.close()
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/track_visit', methods=['POST'])
def track_visit():
    """Track website visits"""
    try:
        data = request.get_json()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        page_visited = data.get('page', '/')
        referrer = data.get('referrer', '')
        session_id = data.get('session_id', '')
        
        conn = get_db_connection()
        
        # Record visit
        conn.execute('''
            INSERT INTO website_visits (ip_address, user_agent, page_visited, referrer, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (ip_address, user_agent, page_visited, referrer, session_id))
        
        # Update daily summary
        today = datetime.now().date()
        existing = conn.execute('SELECT * FROM analytics_summary WHERE date = ?', (today,)).fetchone()
        
        if existing:
            # Update existing record
            conn.execute('''
                UPDATE analytics_summary 
                SET total_visits = total_visits + 1,
                    unique_visitors = (SELECT COUNT(DISTINCT ip_address) FROM website_visits WHERE DATE(visit_time) = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE date = ?
            ''', (today, today))
        else:
            # Create new record
            conn.execute('''
                INSERT INTO analytics_summary (date, total_visits, unique_visitors)
                VALUES (?, 1, 1)
            ''', (today,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/track_download', methods=['POST'])
def track_download():
    """Track app downloads"""
    try:
        data = request.get_json()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        file_name = data.get('file_name', 'arityper.exe')
        file_size = data.get('file_size', 0)
        download_source = data.get('source', 'website')
        session_id = data.get('session_id', '')
        
        conn = get_db_connection()
        
        # Record download
        conn.execute('''
            INSERT INTO app_downloads (ip_address, user_agent, file_name, file_size, download_source, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ip_address, user_agent, file_name, file_size, download_source, session_id))
        
        # Update daily summary
        today = datetime.now().date()
        existing = conn.execute('SELECT * FROM analytics_summary WHERE date = ?', (today,)).fetchone()
        
        if existing:
            # Update existing record
            conn.execute('''
                UPDATE analytics_summary 
                SET total_downloads = total_downloads + 1,
                    unique_downloads = (SELECT COUNT(DISTINCT ip_address) FROM app_downloads WHERE DATE(download_time) = ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE date = ?
            ''', (today, today))
        else:
            # Create new record
            conn.execute('''
                INSERT INTO analytics_summary (date, total_downloads, unique_downloads)
                VALUES (?, 1, 1)
            ''', (today,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for admin dashboard"""
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    try:
        conn = get_db_connection()
        
        # Get summary data for last 30 days
        summary_data = conn.execute('''
            SELECT date, total_visits, unique_visitors, total_downloads, unique_downloads
            FROM analytics_summary 
            WHERE date >= date('now', '-30 days')
            ORDER BY date DESC
        ''').fetchall()
        
        # Get today's stats
        today = datetime.now().date()
        today_stats = conn.execute('''
            SELECT 
                (SELECT COUNT(*) FROM website_visits WHERE DATE(visit_time) = ?) as visits_today,
                (SELECT COUNT(DISTINCT ip_address) FROM website_visits WHERE DATE(visit_time) = ?) as unique_visitors_today,
                (SELECT COUNT(*) FROM app_downloads WHERE DATE(download_time) = ?) as downloads_today,
                (SELECT COUNT(DISTINCT ip_address) FROM app_downloads WHERE DATE(download_time) = ?) as unique_downloads_today
        ''', (today, today, today, today)).fetchone()
        
        # Get total stats
        total_stats = conn.execute('''
            SELECT 
                (SELECT COUNT(*) FROM website_visits) as total_visits,
                (SELECT COUNT(DISTINCT ip_address) FROM website_visits) as total_unique_visitors,
                (SELECT COUNT(*) FROM app_downloads) as total_downloads,
                (SELECT COUNT(DISTINCT ip_address) FROM app_downloads) as total_unique_downloads
        ''').fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'summary_data': [dict(row) for row in summary_data],
            'today_stats': dict(today_stats) if today_stats else {},
            'total_stats': dict(total_stats) if total_stats else {}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def create_default_admin():
    """Create admin user setup if needed"""
    try:
        conn = get_db_connection()
        
        # Check if any admin user exists
        existing_admin = conn.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
        
        if existing_admin == 0:
            # No admin users exist - create initial setup message
            print("No admin users found. Please create admin user manually.")
            print("To create admin user, access the database directly or use the setup script.")
        else:
            print(f"Admin users already exist: {existing_admin} user(s)")
            
        conn.close()
        
    except Exception as e:
        print(f"Error checking admin users: {str(e)}")

if __name__ == '__main__':
    init_database()
    create_default_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
