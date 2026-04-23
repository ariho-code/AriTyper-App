import sqlite3

conn = sqlite3.connect('arityper_admin.db')
cursor = conn.cursor()

# Update the license record with the correct device_id
cursor.execute('''
    UPDATE licenses 
    SET device_id = ? 
    WHERE device_id = 'pending'
''', ('ARI-5C85EA80EB388901',))

# Update the device license status
cursor.execute('''
    UPDATE devices 
    SET license_status = 'active', license_key = (SELECT license_key FROM licenses WHERE device_id = ?)
    WHERE device_id = ?
''', ('ARI-5C85EA80EB388901', 'ARI-5C85EA80EB388901'))

conn.commit()
conn.close()

print('License fixed successfully')
