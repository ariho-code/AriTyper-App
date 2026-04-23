import sqlite3

conn = sqlite3.connect('arityper_admin.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check devices
if 'devices' in [t[0] for t in tables]:
    cursor.execute('SELECT device_id, hostname, status, license_key, license_status FROM devices ORDER BY last_seen DESC LIMIT 5')
    devices = cursor.fetchall()
    print('Devices:')
    for device in devices:
        print(f'  {device}')

# Check licenses
if 'licenses' in [t[0] for t in tables]:
    cursor.execute('SELECT license_key, device_id, status FROM licenses ORDER BY created_at DESC LIMIT 5')
    licenses = cursor.fetchall()
    print('Licenses:')
    for license in licenses:
        print(f'  {license}')

# Check payments
if 'payments' in [t[0] for t in tables]:
    cursor.execute('SELECT transaction_id, phone_number, device_id, status FROM payments ORDER BY submitted_at DESC LIMIT 5')
    payments = cursor.fetchall()
    print('Payments:')
    for payment in payments:
        print(f'  {payment}')

conn.close()
