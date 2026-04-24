"""
AriTyper Web Admin Panel - Flask Application
Host on Render for device management and license approval
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_cors import CORS
from flask_limiter import Limiter
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

# Rate limiting configuration
limiter = Limiter(
    app,
    key_func=lambda: request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
    default_limits=["200 per day", "50 per hour", "10 per minute"],
    storage_uri="memory://",
)

# Database setup
DB_FILE = "arityper_admin.db"

def init_database():
    """Initialize admin database"""
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
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            phone_number TEXT,
            amount REAL,
            network TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            approved_by TEXT
        )
    ''')
    
    # Licenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE,
            device_id TEXT,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            expires_at TIMESTAMP
        )
    ''')
    
    # Activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(device_id, action, details=None, admin_user=None):
    """Log activity to database"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO activity_log (device_id, action, details, timestamp, ip_address)
        VALUES (?, ?, ?, ?, ?)
    ''', (device_id, action, json.dumps(details) if details else None, datetime.now(), request.remote_addr))
    conn.commit()
    conn.close()

def create_default_admin():
    """Create admin user setup if needed"""
    try:
        conn = get_db_connection()
        
        # Check if any admin user exists
        existing_admin = conn.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
        
        if existing_admin == 0:
            # No admin users exist - create initial setup message
            print("No admin users found. Please create admin user manually.")
            print("To create admin user, access the database directly or use setup script.")
        else:
            print(f"Admin users already exist: {existing_admin} user(s)")
            
        conn.close()
        
    except Exception as e:
        print(f"Error checking admin users: {str(e)}")

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Admin login with rate limiting"""
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
@limiter.limit("3 per hour")
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

if __name__ == '__main__':
    init_database()
    create_default_admin()
    app.run(host='0.0.0.0', port=5000, debug=True)
